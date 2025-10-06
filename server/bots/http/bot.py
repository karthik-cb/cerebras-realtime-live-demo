import asyncio
import ssl
from typing import Any, AsyncGenerator, List, Tuple

from bots.http.frame_serializer import BotFrameSerializer
from bots.persistent_context import PersistentContext
from bots.rtvi import create_rtvi_processor
from bots.types import BotConfig, BotParams
from bots.metrics_capture import create_metrics_collector, create_service_tracker
from common.config import SERVICE_API_KEYS
from common.models import Attachment, Message
from fastapi import HTTPException, status
from loguru import logger
from openai._types import NOT_GIVEN
from sqlalchemy.ext.asyncio import AsyncSession

from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask
from pipecat.processors.async_generator import AsyncGeneratorProcessor
from pipecat.processors.frameworks.rtvi import (
    RTVIActionRun,
    RTVIMessage,
    RTVIProcessor,
)
from pipecat.services.llm_service import OpenAILLMContext
from pipecat.services.cerebras.llm import CerebrasLLMService
from pipecat.adapters.schemas.function_schema import FunctionSchema
from pipecat.adapters.schemas.tools_schema import ToolsSchema
from pipecat.services.mcp_service import MCPClient
from mcp import StdioServerParameters
from bots.mcp_config import get_enabled_mcp_servers


async def http_bot_pipeline(
    params: BotParams,
    config: BotConfig,
    messages,
    attachments: List[Attachment],
    db: AsyncSession,
    language_code: str = "english",
) -> Tuple[AsyncGenerator[Any, None], Any]:
    llm_api_key = SERVICE_API_KEYS.get("cerebras")
    if llm_api_key is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service `cerebras` not available in SERVICE_API_KEYS. Please check your environment variables.",
        )

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
    
    # Get model preferences from params, fallback to defaults
    model_prefs = params.model_preferences or {}
    llm_model = model_prefs.get("llm", "gpt-oss-120b")
    
    llm = CerebrasLLMService(
        api_key=str(SERVICE_API_KEYS["cerebras"]),
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

    system_prompt_list = [
        "You are a helpful assistant with access to weather information, ferry trip planning, and MCP tools.",
        "When users ask about weather, use the get_current_weather function to fetch real-time data.",
        "For ferry trip planning, you can help users search for ferry routes, schedules, and prices across Europe and the Mediterranean using Ferryhopper tools.",
        "When users ask about ferry trips, use the available Ferryhopper MCP tools to search for routes, get port information, and provide booking links.",
        "You also have access to MCP tools for file operations and other external services.", 
        "Keep responses concise and always mention what you're doing when using functions or tools.",
        
    ]
    
    logger.info(f"🔧 Combined tools: {[tool.name for tool in all_tools]}")
    context = OpenAILLMContext(
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant with access to weather information, ferry trip planning, and MCP tools. When users ask about weather, use the get_current_weather function to fetch real-time data. For ferry trip planning, you can help users search for ferry routes, schedules, and prices across Europe and the Mediterranean using Ferryhopper tools. When users ask about ferry trips, use the available Ferryhopper MCP tools to search for routes, get port information, and provide booking links. You also have access to MCP tools for file operations and other external services. Keep responses concise and always mention what you're doing when using functions or tools."
            }
        ] + messages,
        tools=combined_tools
    )
    context_aggregator = llm.create_context_aggregator(
        context, assistant_expect_stripped_words=False
    )
    user_aggregator = context_aggregator.user()
    assistant_aggregator = context_aggregator.assistant()

    storage = PersistentContext(context=context)

    async_generator = AsyncGeneratorProcessor(serializer=BotFrameSerializer())

    #
    # RTVI
    #

    rtvi = await create_rtvi_processor(config, user_aggregator)

    #
    # Processing
    #

    processors = [
        rtvi,
        user_aggregator,
        storage.create_processor(),
        llm,
        async_generator,
        assistant_aggregator,
        storage.create_processor(exit_on_endframe=True),
    ]

    pipeline = Pipeline(processors)

    runner = PipelineRunner(handle_sigint=False)

    task = PipelineTask(pipeline)

    runner_task = asyncio.create_task(runner.run(task))

    @storage.on_context_message
    async def on_context_message(messages: list[Any]):
        logger.debug(f"{len(messages)} message(s) received for storage: {str(messages)[:120]}...")
        try:
            await Message.create_messages(
                db_session=db,
                conversation_id=params.conversation_id,
                messages=messages,
                language_code=language_code,
            )
        except Exception as e:
            logger.error(f"Error storing messages: {e}")
            raise e

    @rtvi.event_handler("on_bot_started")
    async def on_bot_started(rtvi: RTVIProcessor):
        for action in params.actions:
            logger.debug(f"Processing action: {action}")

            # If this is an append_to_messages action, we need to append any
            # attachments. The rule we'll follow is that we should append
            # attachments to the first "user" message in the actions list.
            if action.data.get("action") == "append_to_messages" and attachments:
                for msg in action.data["arguments"][0]["value"]:
                    if msg.get("role") == "user":
                        # Append attachments to this message
                        logger.debug(
                            f"Appending {len(attachments)} attachment(s) to 'user' message"
                        )
                        content = msg.get("content", "")
                        if isinstance(content, str):
                            content = [{"type": "text", "text": content}]
                        for attachment in attachments:
                            # Assume for the moment that all attachments are images
                            content.append(
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{attachment.file_type};base64,{attachment.file_data}"
                                    },
                                }
                            )
                            await db.delete(attachment)
                            await db.commit()
                        break

            await rtvi.handle_message(action)

        # This is a single turn, so we just push an action to stop the running
        # pipeline task.
        action = RTVIActionRun(service="system", action="end")
        message = RTVIMessage(type="action", id="END", data=action.model_dump())
        await rtvi.handle_message(message)

    return (async_generator.generator(), runner_task)
