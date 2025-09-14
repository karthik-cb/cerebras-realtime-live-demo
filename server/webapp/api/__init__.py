from common.config import SERVICE_API_KEYS
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from .bots import router as bots_router
from .conversations import router as conversations_router

router = APIRouter()

router.include_router(conversations_router, tags=["Conversations"])
router.include_router(bots_router, tags=["Bots"])


@router.get("/", response_class=JSONResponse)
async def config():
    # Note: do not send api keys in production (keys will be exposed to the client.) Please see README.
    return {
        "websocket-enabled": bool(SERVICE_API_KEYS["deepgram"] and SERVICE_API_KEYS["cerebras"]),
        "webrtc-enabled": bool(SERVICE_API_KEYS["daily"]),
        "tts-llm-stt-enabled": bool(SERVICE_API_KEYS["deepgram"] and SERVICE_API_KEYS["cerebras"]),
        "deepgram-api-key": SERVICE_API_KEYS["deepgram"],
        "cerebras-api-key": SERVICE_API_KEYS["cerebras"],
        "daily-api-key": SERVICE_API_KEYS["daily"],
        # Legacy support
        "gemini-api-key": SERVICE_API_KEYS["gemini"],
    }
