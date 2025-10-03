import asyncio
import os
import ssl
import sys
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
    await subprocess_session_factory.engine.dispose()


def _bot_process(
    params: BotParams,
    config: BotConfig,
    room_url: str,
    room_token: str,
):
    # This is a different process so we need to make sure we have the right log level.
    logger.remove()
    logger.add(sys.stderr, level=os.getenv("BOT_LOG_LEVEL", "INFO"))

    asyncio.run(_bot_main(params, config, room_url, room_token))


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
    process = Process(target=_bot_process, args=(params, config, room_url, room_token))
    process.start()
