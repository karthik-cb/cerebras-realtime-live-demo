from bots.rtvi_actions import register_rtvi_actions
from bots.rtvi_services import register_rtvi_services
from bots.types import BotConfig
from loguru import logger
from pipecat.processors.aggregators.llm_response import LLMUserContextAggregator
from pipecat.processors.frameworks.rtvi import (
    RTVIConfig,
    RTVIProcessor,
    RTVIServiceConfig,
    RTVIServiceOptionConfig,
)


async def create_rtvi_processor(
    bot_config: BotConfig, user_aggregator: LLMUserContextAggregator
) -> RTVIProcessor:
    config = bot_config.config

    #
    # RTVI default config
    #
    default_config = RTVIConfig(
        config=[
            RTVIServiceConfig(
                service="stt",
                options=[
                    RTVIServiceOptionConfig(name="model", value="nova-2-general"),
                    RTVIServiceOptionConfig(name="language", value="en"),
                ],
            ),
            RTVIServiceConfig(
                service="llm",
                options=[
                    RTVIServiceOptionConfig(name="model", value="gpt-oss-120b"),
                ],
            ),
            RTVIServiceConfig(
                service="tts",
                options=[
                    RTVIServiceOptionConfig(name="voice", value="aura-luna-en"),
                ],
            ),
        ]
    )

    #
    # RTVI processor
    #

    # Always use our default config for TTS-LLM-STT pipeline
    # The config parameter might be overriding our Deepgram/Cerebras settings
    rtvi_config = default_config
    logger.info(f"🔧 Using RTVI config: {rtvi_config}")

    rtvi = RTVIProcessor(config=rtvi_config)

    await register_rtvi_services(rtvi, user_aggregator)
    await register_rtvi_actions(rtvi, user_aggregator)
    
    # Log the RTVI configuration
    logger.info(f"🔧 RTVI Configuration: {config}")
    # Note: _services attribute might not be available in this version
    try:
        services = [service.name for service in rtvi._services.values()]
        logger.info(f"🔧 RTVI Services: {services}")
    except AttributeError:
        logger.info("🔧 RTVI Services: Unable to access services list (attribute not available)")

    return rtvi
