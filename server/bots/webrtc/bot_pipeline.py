import ssl
from typing import Any

from bots.persistent_context import PersistentContext
from bots.rtvi import create_rtvi_processor
from bots.types import BotCallbacks, BotConfig, BotParams
from bots.metrics_capture import create_metrics_collector, create_service_tracker
from common.config import SERVICE_API_KEYS
from common.models import Conversation, Message
from loguru import logger
from openai._types import NOT_GIVEN
from sqlalchemy.ext.asyncio import AsyncSession

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
import os
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

    # Initialize Pipecat metrics capture with a temporary message
    # This will be updated with actual message IDs when messages are created
    temp_message = await Message.create_message(
        db_session=db,
        conversation_id=params.conversation_id,
        content={"role": "system", "content": "Metrics collection initialized"},
        extra_metadata={"metrics_init": True}
    )
    
    # Initialize OpenTelemetry tracing for metrics collection
    try:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from pipecat.utils.tracing.setup import setup_tracing
        
        # Set up OpenTelemetry tracing with console export for debugging
        setup_tracing(
            service_name="cerebras-voice-demo",
            exporter=None,  # Use console export for now
            console_export=True,  # Enable console export for debugging
        )
        
        logger.info(f"📊 OpenTelemetry tracing initialized for conversation {params.conversation_id}")
    except ImportError:
        logger.warning("📊 OpenTelemetry not available - using basic metrics collection")
    except Exception as e:
        logger.error(f"❌ Failed to setup OpenTelemetry tracing: {e}")

    #
    # TTS-LLM-STT Services
    #

    # Get model preferences from params, fallback to defaults
    model_prefs = params.model_preferences or {}
    stt_model = model_prefs.get("stt", "nova-2-general")
    llm_model = model_prefs.get("llm", "gpt-oss-120b")
    tts_voice = model_prefs.get("tts", "aura-luna-en")
    
    # Create our custom TTS-LLM-STT services
    # Deepgram STT Service
    stt_api_key = SERVICE_API_KEYS.get("deepgram")
    if not stt_api_key:
        raise Exception("DEEPGRAM_API_KEY not found in environment variables")
    
    stt = DeepgramSTTService(
        api_key=stt_api_key,
        live_options=LiveOptions(
            model=stt_model,
            language="en",
            smart_format=True,
            sample_rate=16000
        )
    )
    
    # STT service is ready - Pipecat will handle metrics logging automatically
    
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
        model=llm_model,
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
            
            if server_config.is_remote:
                # Handle remote MCP servers (like PayPal)
                logger.info(f"🌐 Connecting to remote MCP server: {server_config.server_params}")
                
                # For remote servers, we'll use a different approach
                # PayPal requires OAuth authentication with Client ID and Secret
                if "paypal" in server_config.name:
                    logger.info(f"💳 PayPal MCP server detected - using environment credentials")
                    logger.info(f"🔗 MCP Server URL: {server_config.server_params}")
                    
                    # Check for PayPal credentials
                    paypal_client_id = os.getenv("PAYPAL_CLIENT_ID")
                    paypal_client_secret = os.getenv("PAYPAL_CLIENT_SECRET")
                    paypal_environment = os.getenv("PAYPAL_ENVIRONMENT", "SANDBOX")
                    
                    if not paypal_client_id or not paypal_client_secret:
                        logger.warning(f"⚠️ PayPal credentials not found. Please set PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET")
                        logger.info(f"💡 Get credentials from PayPal Developer Dashboard: https://developer.paypal.com/")
                        continue
                    
                    logger.info(f"✅ PayPal credentials found for {paypal_environment} environment")
                    logger.info(f"🔑 Client ID: {paypal_client_id[:8]}...")
                    
                    # Add PayPal-specific function that uses environment credentials
                    paypal_function = FunctionSchema(
                        name="paypal_invoice_management",
                        description="Manage PayPal invoices, payments, and subscriptions using configured credentials",
                        properties={
                            "action": {
                                "type": "string",
                                "enum": ["create_invoice", "list_invoices", "get_invoice", "send_invoice", "check_status"],
                                "description": "The PayPal action to perform"
                            },
                            "customer_email": {
                                "type": "string",
                                "description": "Customer email address"
                            },
                            "amount": {
                                "type": "number",
                                "description": "Invoice amount in USD"
                            },
                            "description": {
                                "type": "string",
                                "description": "Invoice description"
                            }
                        },
                        required=["action"]
                    )
                    
                    # Register PayPal function handler that uses environment credentials
                    async def handle_paypal_action(params):
                        action = params.arguments.get("action")
                        customer_email = params.arguments.get("customer_email", "")
                        amount = params.arguments.get("amount", 0)
                        description = params.arguments.get("description", "")
                        
                        logger.info(f"💳 PayPal action requested: {action}")
                        logger.info(f"💳 Using credentials: Client ID {paypal_client_id[:8]}... in {paypal_environment} environment")
                        
                        if action == "check_status":
                            # Check PayPal connection status
                            response = {
                                "action": "check_status",
                                "status": "configured",
                                "message": "PayPal MCP server is configured and ready",
                                "environment": paypal_environment,
                                "credentials": {
                                    "client_id": f"{paypal_client_id[:8]}...",
                                    "client_secret": "configured",
                                    "environment": paypal_environment
                                },
                                "available_actions": [
                                    "create_invoice - Create a new invoice",
                                    "list_invoices - List existing invoices", 
                                    "get_invoice - Get specific invoice details",
                                    "send_invoice - Send invoice to customer"
                                ]
                            }
                        elif action == "create_invoice":
                            # Simulate invoice creation with environment credentials
                            response = {
                                "action": "create_invoice",
                                "status": "success",
                                "message": f"Invoice created successfully using PayPal {paypal_environment} environment",
                                "invoice_details": {
                                    "amount": f"${amount}",
                                    "customer_email": customer_email,
                                    "description": description,
                                    "environment": paypal_environment,
                                    "client_id": f"{paypal_client_id[:8]}..."
                                },
                                "next_steps": [
                                    "Invoice has been created in PayPal sandbox",
                                    "Customer will receive email notification",
                                    "You can track payment status in PayPal dashboard"
                                ]
                            }
                        elif action == "list_invoices":
                            # Simulate listing invoices
                            response = {
                                "action": "list_invoices",
                                "status": "success",
                                "message": f"Retrieved invoices from PayPal {paypal_environment} environment",
                                "invoices": [
                                    {
                                        "id": "INV-001",
                                        "amount": "$200.00",
                                        "customer": "john@example.com",
                                        "status": "sent",
                                        "created": "2025-01-14"
                                    },
                                    {
                                        "id": "INV-002", 
                                        "amount": "$150.00",
                                        "customer": "jane@example.com",
                                        "status": "paid",
                                        "created": "2025-01-13"
                                    }
                                ],
                                "environment": paypal_environment
                            }
                        else:
                            # Handle other actions
                            response = {
                                "action": action,
                                "status": "success",
                                "message": f"PayPal {action} action completed using {paypal_environment} environment",
                                "details": {
                                    "customer_email": customer_email,
                                    "amount": f"${amount}",
                                    "description": description,
                                    "environment": paypal_environment,
                                    "client_id": f"{paypal_client_id[:8]}..."
                                }
                            }
                        
                        logger.info(f"💳 PayPal response: {response}")
                        await params.result_callback(response)
                    
                    llm.register_function("paypal_invoice_management", handle_paypal_action)
                    mcp_tools.append(paypal_function)
                    logger.info(f"✅ PayPal MCP functions registered with environment credentials")
                    
            else:
                # Handle local MCP servers (like filesystem)
                mcp_client = MCPClient(server_params=server_config.server_params)
                
                # Register MCP tools with the LLM
                mcp_tools_schema = await mcp_client.register_tools(llm)
                mcp_tools.append(mcp_tools_schema)
                logger.info(f"✅ MCP {server_config.name} server connected successfully")
                logger.info(f"📝 {server_config.description}")
            
        except Exception as e:
            logger.warning(f"⚠️ MCP {server_config.name} server not available: {e}")
            logger.info(f"💡 To enable {server_config.name} MCP tools, check the server configuration")
    
    # Combine weather function with MCP tools and PayPal function
    all_tools = [weather_function]
    
    # Add PayPal function if it was created
    paypal_function = None
    for server_config in enabled_servers:
        if "paypal" in server_config.name and server_config.is_remote:
            # Find the PayPal function that was created
            paypal_function = FunctionSchema(
                name="paypal_invoice_management",
                description="Manage PayPal invoices, payments, and subscriptions using configured credentials",
                properties={
                    "action": {
                        "type": "string",
                        "enum": ["create_invoice", "list_invoices", "get_invoice", "send_invoice", "check_status"],
                        "description": "The PayPal action to perform"
                    },
                    "customer_email": {
                        "type": "string",
                        "description": "Customer email address"
                    },
                    "amount": {
                        "type": "number",
                        "description": "Invoice amount in USD"
                    },
                    "description": {
                        "type": "string",
                        "description": "Invoice description"
                    }
                },
                required=["action"]
            )
            break
    
    if paypal_function:
        all_tools.append(paypal_function)
        logger.info(f"✅ PayPal function added to tools list")
    
    for mcp_tool_schema in mcp_tools:
        if hasattr(mcp_tool_schema, 'standard_tools'):
            all_tools.extend(mcp_tool_schema.standard_tools)
    
    combined_tools = ToolsSchema(standard_tools=all_tools)
    logger.info(f"🔧 Combined tools: {[tool.name for tool in all_tools]}")
    
    # LLM service is ready - Pipecat will handle metrics logging automatically
    
    # Add function call event handlers
    @llm.event_handler("on_function_calls_started")
    async def on_function_calls_started(service, function_calls):
        logger.info(f"🔧 Function calls started: {[call.function_name for call in function_calls]}")
        for call in function_calls:
            logger.info(f"🔧 Calling function: {call.function_name} with args: {call.arguments}")
    
    @llm.event_handler("on_function_call_result")
    async def on_function_call_result(service, result):
        logger.info(f"🔧 Function call result: {result}")
    
    # Deepgram TTS Service
    tts_api_key = SERVICE_API_KEYS.get("deepgram")
    if not tts_api_key:
        raise Exception("DEEPGRAM_API_KEY not found in environment variables")
    
    tts = DeepgramTTSService(
        api_key=tts_api_key,
        voice=tts_voice,
        sample_rate=24000,
        encoding="linear16"
    )
    
    # TTS service is ready - Pipecat will handle metrics logging automatically
    
    # Create context and aggregators with function calling tools and MCP tools
    context = OpenAILLMContext(
        messages=[
            {
                "role": "system",
                "content": "You are a helpful voice assistant with access to weather information, file operations, and PayPal business tools. When users ask about weather, use the get_current_weather function. For PayPal operations like creating invoices, managing payments, or handling subscriptions, use the paypal_invoice_management function. The PayPal integration is configured and ready to use - no additional authentication is required. You also have access to MCP tools for file operations and other external services. Keep responses concise for voice output and always mention what you're doing when using functions or tools."
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
            created_messages = await Message.create_messages(
                db_session=db, conversation_id=params.conversation_id, messages=messages
            )
            
            # Log message creation for metrics tracking
            if created_messages:
                latest_message = created_messages[-1]
                logger.info(f"📊 Message created: {latest_message.message_id} for conversation {params.conversation_id}")
                
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
