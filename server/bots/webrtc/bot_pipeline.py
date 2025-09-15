import ssl
from typing import Any

from bots.persistent_context import PersistentContext
from bots.rtvi import create_rtvi_processor
from bots.types import BotCallbacks, BotConfig, BotParams
from common.config import SERVICE_API_KEYS
from common.models import Conversation, Message
from loguru import logger
from openai._types import NOT_GIVEN
from sqlalchemy.ext.asyncio import AsyncSession

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.pipeline.pipeline import Pipeline
from pipecat.processors.frame_processor import FrameDirection
from pipecat.processors.frameworks.rtvi import (
    RTVIProcessor,
)
from pipecat.services.llm_service import OpenAILLMContext
from pipecat.services.cerebras.llm import CerebrasLLMService
from pipecat.services.deepgram.stt import DeepgramSTTService, LiveOptions
from pipecat.services.deepgram.tts import DeepgramTTSService
from pipecat.transcriptions.language import Language
from pipecat.transports.daily.transport import DailyParams, DailyTransport
from pipecat.adapters.schemas.function_schema import FunctionSchema
from pipecat.adapters.schemas.tools_schema import ToolsSchema
from pipecat.services.mcp_service import MCPClient
from mcp import StdioServerParameters
from bots.mcp_config import get_enabled_mcp_servers

# SSL Certificate configuration for macOS
# The proper way to fix SSL issues on macOS is to extract system certificates
# and set environment variables pointing to them:
#
# 1. Extract certificates:
#    security find-certificate -a -p /System/Library/Keychains/SystemRootCertificates.keychain > cacerts.pem
#    security find-certificate -a -p /Library/Keychains/System.keychain >> cacerts.pem
#    mv cacerts.pem ~/Library/cacerts.pem
#
# 2. Set environment variables:
#    export REQUESTS_CA_BUNDLE="$HOME/Library/cacerts.pem"
#    export SSL_CERT_FILE="$HOME/Library/cacerts.pem"
#
# For development only - disable SSL verification (NOT recommended for production):



async def bot_pipeline(
    params: BotParams,
    config: BotConfig,
    callbacks: BotCallbacks,
    room_url: str,
    room_token: str,
    db: AsyncSession,
) -> Pipeline:
    transport = DailyTransport(
        room_url,
        room_token,
        "Voice Assistant Bot",
        DailyParams(
            audio_in_sample_rate=16000,
            audio_out_enabled=True,
            audio_out_sample_rate=24000,
            transcription_enabled=False,
            vad_enabled=True,
            vad_analyzer=SileroVADAnalyzer(params=VADParams(stop_secs=0.5)),
            vad_audio_passthrough=True,
        ),
    )

    conversation = await Conversation.get_conversation_by_id(params.conversation_id, db)
    if not conversation:
        raise Exception(f"Conversation {params.conversation_id} not found")
    messages = [getattr(msg, "content") for msg in conversation.messages]

    #
    # TTS-LLM-STT Services
    #

    # Create our custom TTS-LLM-STT services
    # Deepgram STT Service
    stt_api_key = SERVICE_API_KEYS.get("deepgram")
    if not stt_api_key:
        raise Exception("DEEPGRAM_API_KEY not found in environment variables")
    
    stt = DeepgramSTTService(
        api_key=stt_api_key,
        live_options=LiveOptions(
            model="nova-2-general",
            language="en",
            smart_format=True,
            sample_rate=16000
        )
    )
    
    # Add event handlers for debugging - using correct event names
    @stt.event_handler("on_started")
    async def on_stt_started(service):
        logger.info("🎤 STT started - listening for speech")
    
    @stt.event_handler("on_stopped")
    async def on_stt_stopped(service):
        logger.info("🎤 STT stopped")
    
    @stt.event_handler("on_text_frame")
    async def on_text_frame(service, frame):
        logger.info(f"🎤 Transcription: {frame.text}")
    
    @stt.event_handler("on_error")
    async def on_stt_error(service, error):
        logger.error(f"🎤 STT Error: {error}")
    
    # Cerebras LLM Service with Function Calling
    llm_api_key = SERVICE_API_KEYS.get("cerebras")
    if not llm_api_key:
        raise Exception("CEREBRAS_API_KEY not found in environment variables")
    
    # Define weather function for tool calling
    weather_function = FunctionSchema(
        name="get_current_weather",
        description="Get current weather information for a specific location",
        properties={
            "location": {
                "type": "string",
                "description": "City and state, e.g. San Francisco, CA"
            },
            "format": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "Temperature unit to use"
            }
        },
        required=["location", "format"]
    )
    
    tools = ToolsSchema(standard_tools=[weather_function])
    
    llm = CerebrasLLMService(
        api_key=llm_api_key,
        model="gpt-oss-120b",
        temperature=0.7,
        max_tokens=1000
    )
    
    # Register weather function handler
    async def fetch_weather(params):
        location = params.arguments["location"]
        format_type = params.arguments["format"]
        
        # Simulate weather data (in a real app, you'd call a weather API)
        weather_data = {
            "location": location,
            "temperature": "75°F" if format_type == "fahrenheit" else "24°C",
            "conditions": "sunny",
            "humidity": "65%",
            "wind": "5 mph"
        }
        
        logger.info(f"🌤️ Weather function called for {location} in {format_type}")
        logger.info(f"🌤️ Weather data: {weather_data}")
        
        # Return the weather information
        await params.result_callback(weather_data)
    
    llm.register_function("get_current_weather", fetch_weather)
    
    # Initialize MCP clients for external tools
    mcp_tools = []
    enabled_servers = get_enabled_mcp_servers()
    
    for server_config in enabled_servers:
        try:
            logger.info(f"🔧 Connecting to MCP server: {server_config.name}")
            mcp_client = MCPClient(server_params=server_config.server_params)
            
            # Register MCP tools with the LLM
            mcp_tools_schema = await mcp_client.register_tools(llm)
            mcp_tools.append(mcp_tools_schema)
            logger.info(f"✅ MCP {server_config.name} server connected successfully")
            logger.info(f"📝 {server_config.description}")
            
        except Exception as e:
            logger.warning(f"⚠️ MCP {server_config.name} server not available: {e}")
            logger.info(f"💡 To enable {server_config.name} MCP tools, check the server configuration")
    
    # Combine weather function with MCP tools
    all_tools = [weather_function]
    for mcp_tool_schema in mcp_tools:
        if hasattr(mcp_tool_schema, 'standard_tools'):
            all_tools.extend(mcp_tool_schema.standard_tools)
    
    combined_tools = ToolsSchema(standard_tools=all_tools)
    
    # Add event handlers for debugging - using correct event names
    @llm.event_handler("on_started")
    async def on_llm_started(service):
        logger.info("🧠 LLM started - ready to process text")
    
    @llm.event_handler("on_stopped")
    async def on_llm_stopped(service):
        logger.info("🧠 LLM stopped")
    
    @llm.event_handler("on_text_frame")
    async def on_llm_text_frame(service, frame):
        logger.info(f"🧠 LLM Response: {frame.text}")
    
    @llm.event_handler("on_error")
    async def on_llm_error(service, error):
        logger.error(f"🧠 LLM Error: {error}")
    
    # Add function call event handlers
    @llm.event_handler("on_function_calls_started")
    async def on_function_calls_started(service, function_calls):
        logger.info(f"🔧 Function calls started: {[call.name for call in function_calls]}")
        for call in function_calls:
            logger.info(f"🔧 Calling function: {call.name} with args: {call.arguments}")
    
    @llm.event_handler("on_function_call_result")
    async def on_function_call_result(service, result):
        logger.info(f"🔧 Function call result: {result}")
    
    # Deepgram TTS Service
    tts_api_key = SERVICE_API_KEYS.get("deepgram")
    if not tts_api_key:
        raise Exception("DEEPGRAM_API_KEY not found in environment variables")
    
    tts = DeepgramTTSService(
        api_key=tts_api_key,
        voice="aura-luna-en",
        sample_rate=24000,
        encoding="linear16"
    )
    
    # Add event handlers for debugging - using correct event names
    @tts.event_handler("on_started")
    async def on_tts_started(service):
        logger.info("🔊 TTS started - ready to generate audio")
    
    @tts.event_handler("on_stopped")
    async def on_tts_stopped(service):
        logger.info("🔊 TTS stopped")
    
    @tts.event_handler("on_audio_frame")
    async def on_tts_audio_frame(service, frame):
        logger.info(f"🔊 TTS Audio generated: {len(frame.audio)} bytes")
    
    @tts.event_handler("on_error")
    async def on_tts_error(service, error):
        logger.error(f"🔊 TTS Error: {error}")
    
    # Create context and aggregators with function calling tools and MCP tools
    context = OpenAILLMContext(
        messages=[
            {
                "role": "system",
                "content": "You are a helpful voice assistant with access to weather information and MCP tools. When users ask about weather, use the get_current_weather function to fetch real-time data. You also have access to MCP tools for file operations and other external services. Keep responses concise for voice output and always mention what you're doing when using functions or tools."
            }
        ] + messages,
        tools=combined_tools
    )
    context_aggregator = llm.create_context_aggregator(context)
    user_aggregator = context_aggregator.user()
    assistant_aggregator = context_aggregator.assistant()
    storage = PersistentContext(context=context)
    
    # Create RTVI processor for client communication
    rtvi = await create_rtvi_processor(config, user_aggregator)
    
    processors = [
        transport.input(),
        stt,  # Deepgram STT
        rtvi,  # RTVI processor for client communication
        user_aggregator,
        llm,  # Cerebras LLM
        tts,  # Deepgram TTS
        transport.output(),
        assistant_aggregator,
        storage.create_processor(exit_on_endframe=True),
    ]

    pipeline = Pipeline(processors)

    @storage.on_context_message
    async def on_context_message(messages: list[Any]):
        logger.debug(f"{len(messages)} message(s) received for storage")
        try:
            await Message.create_messages(
                db_session=db, conversation_id=params.conversation_id, messages=messages
            )
        except Exception as e:
            logger.error(f"Error storing messages: {e}")
            raise e

    @rtvi.event_handler("on_client_ready")
    async def on_client_ready(rtvi):
        logger.info("🔧 Client ready - setting bot ready")
        await rtvi.set_bot_ready()
        logger.info("🔧 Bot ready set - RTVI should now be processing audio")
        for message in params.actions:
            await rtvi.handle_message(message)

    @transport.event_handler("on_first_participant_joined")
    async def on_first_participant_joined(transport, participant):
        # Voice-only chat - no video capture needed
        logger.info(f"Participant {participant['id']} joined for voice chat")
        await callbacks.on_first_participant_joined(participant)

    @transport.event_handler("on_participant_joined")
    async def on_participant_joined(transport, participant):
        await callbacks.on_participant_joined(participant)

    @transport.event_handler("on_participant_left")
    async def on_participant_left(transport, participant, reason):
        await callbacks.on_participant_left(participant, reason)

    @transport.event_handler("on_call_state_updated")
    async def on_call_state_updated(transport, state):
        await callbacks.on_call_state_updated(state)

    return pipeline
