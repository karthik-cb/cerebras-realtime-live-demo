import asyncio
import os
import ssl
import sys
import threading
from multiprocessing import Process
from typing import Awaitable, Callable

import aiohttp
from bots.types import BotCallbacks, BotConfig, BotParams
from bots.webrtc.bot_error_pipeline import bot_error_pipeline_task
from bots.webrtc.bot_pipeline import bot_pipeline
from bots.webrtc.bot_pipeline_runner import BotPipelineRunner
from common.config import SERVICE_API_KEYS
from common.database import DatabaseSessionFactory
from fastapi import HTTPException, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.transports.daily.utils import (
    DailyRESTHelper,
    DailyRoomParams,
)

MAX_SESSION_TIME = int(os.getenv("BOT_MAX_VOICE_SESSION_TIME", 15 * 60)) or 15 * 60


def get_concurrency_mode():
    """Determine concurrency mode based on environment."""
    environment = os.getenv("ENVIRONMENT", "development").lower()
    is_railway = bool(os.getenv("RAILWAY_ENVIRONMENT"))
    is_production = environment == "production" or is_railway
    
    mode = "multiprocessing" if is_production else "threading"
    logger.debug(f"Using {mode} concurrency mode (ENVIRONMENT={environment}, RAILWAY_ENVIRONMENT={is_railway})")
    
    return mode


async def _cleanup(room_url: str, config: BotConfig):
    # Create SSL context that doesn't verify certificates (for development only)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    async with aiohttp.ClientSession(connector=connector) as session:
        debug_room = os.getenv("USE_DEBUG_ROOM", None)
        if debug_room:
            return

        transport_api_key = SERVICE_API_KEYS["daily"]

        helper = DailyRESTHelper(
            daily_api_key=str(transport_api_key),
            aiohttp_session=session,
        )

        try:
            logger.info(f"Deleting room {room_url}")
            await helper.delete_room_by_url(room_url)
        except Exception as e:
            logger.error(f"Bot failed to delete room: {e}")


async def _pipeline_task(
    params: BotParams,
    config: BotConfig,
    room_url: str,
    room_token: str,
    db: AsyncSession,
) -> Callable[[BotCallbacks], Awaitable[PipelineTask]]:
    async def create_task(callbacks: BotCallbacks) -> PipelineTask:
        pipeline = await bot_pipeline(params, config, callbacks, room_url, room_token, db)

        task = PipelineTask(
            pipeline,
            params=PipelineParams(
                allow_interruptions=True,
                enable_metrics=True,
                enable_usage_metrics=True,
                send_initial_empty_metrics=False,
            ),
            enable_tracing=True,  # Enable OpenTelemetry tracing
            enable_turn_tracking=True,  # Enable turn tracking
            conversation_id=params.conversation_id,  # Set conversation ID for tracing
        )

        return task

    return create_task


async def _bot_main(
    params: BotParams,
    config: BotConfig,
    room_url: str,
    room_token: str,
):
    """Main bot function that works in both threading and multiprocessing modes."""
    concurrency_mode = get_concurrency_mode()
    
    if concurrency_mode == "multiprocessing":
        # Production: Create new database session factory for this process
        subprocess_session_factory = DatabaseSessionFactory()
        await subprocess_session_factory.initialize_schema()
    else:
        # Development: Use the shared singleton factory
        subprocess_session_factory = DatabaseSessionFactory()
    
    async with subprocess_session_factory() as db:
        bot_runner = BotPipelineRunner(conversation_id=params.conversation_id)
        try:
            task_creator = await _pipeline_task(params, config, room_url, room_token, db)
            await bot_runner.start(task_creator)
        except Exception as e:
            logger.error(f"Error running bot: {e}")
            task_creator = await bot_error_pipeline_task(
                room_url, room_token, f"Error running bot: {e}"
            )
            await bot_runner.start(task_creator)

        await _cleanup(room_url, config)

        logger.info("Bot has finished. Bye!")
    
    # Only dispose engine in multiprocessing mode
    if concurrency_mode == "multiprocessing":
        await subprocess_session_factory.engine.dispose()


def _bot_thread(
    params: BotParams,
    config: BotConfig,
    room_url: str,
    room_token: str,
):
    """Thread-based bot execution for local development."""
    logger.remove()
    logger.add(sys.stderr, level=os.getenv("BOT_LOG_LEVEL", "INFO"))
    
    # Use the main process's event loop (shared memory)
    asyncio.run(_bot_main(params, config, room_url, room_token))


def _bot_process(
    params: BotParams,
    config: BotConfig,
    room_url: str,
    room_token: str,
):
    """Process-based bot execution for production."""
    logger.remove()
    logger.add(sys.stderr, level=os.getenv("BOT_LOG_LEVEL", "INFO"))
    
    # Create new event loop for this process
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(_bot_main(params, config, room_url, room_token))
    finally:
        loop.close()


async def bot_create(daily_api_key: str):
    # Create SSL context that doesn't verify certificates (for development only)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    async with aiohttp.ClientSession(connector=connector) as session:
        daily_rest_helper = DailyRESTHelper(
            daily_api_key=daily_api_key,
            aiohttp_session=session,
        )

        try:
            room = await daily_rest_helper.create_room(params=DailyRoomParams())
            bot_token = await daily_rest_helper.get_token(room.url, MAX_SESSION_TIME)
            user_token = await daily_rest_helper.get_token(room.url, MAX_SESSION_TIME)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unable to run bot: {e}"
            )

        return room, user_token, bot_token


def bot_launch(
    params: BotParams,
    config: BotConfig,
    room_url: str,
    room_token: str,
):
    """Launch bot using environment-appropriate concurrency model."""
    concurrency_mode = get_concurrency_mode()
    
    if concurrency_mode == "multiprocessing":
        # Production: Use multiprocessing with proper event loop management
        logger.info("Launching bot in multiprocessing mode (production)")
        process = Process(target=_bot_process, args=(params, config, room_url, room_token))
        process.start()
    else:
        # Development: Use threading for faster startup and shared memory
        logger.info("Launching bot in threading mode (development)")
        thread = threading.Thread(target=_bot_thread, args=(params, config, room_url, room_token))
        thread.start()
