import os
import ssl
import sys
from contextlib import asynccontextmanager

# Configure SSL context to disable certificate verification for development
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Set the default SSL context for the entire process
ssl._create_default_https_context = lambda: ssl_context

from common.database import DatabaseSessionFactory
from common.models import Base
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from loguru import logger

from .api import router as api_router
from .health import health_checker

load_dotenv(override=False)

logger.remove(0)
logger.add(sys.stderr, level=os.getenv("WEBAPP_LOG_LEVEL", "DEBUG"))


default_session_factory = DatabaseSessionFactory()

# ========================
# FastAPI App
# ========================


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_factory = default_session_factory

    try:
        # Initialize schema from model definitions
        await default_session_factory.initialize_schema()
        if bool(int(os.getenv("DATABASE_USE_REFLECTION", "0"))):
            async with default_session_factory.engine.connect() as conn:
                await conn.run_sync(Base.metadata.reflect)

    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        os._exit(1)
    yield
    await default_session_factory.engine.dispose()


app = FastAPI(
    title="Open Sesame API",
    docs_url="/docs",
    lifespan=lifespan,
)

# Configure CORS for Vercel frontend
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*")
if allowed_origins != "*":
    allowed_origins = [origin.strip() for origin in allowed_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/", response_class=HTMLResponse)
async def home():
    return "Sesame is running"


@app.get("/env-check", response_class=JSONResponse)
async def env_check():
    """Debug endpoint to check environment variables (remove in production)"""
    return {
        "DEEPGRAM_API_KEY": "SET" if os.getenv("DEEPGRAM_API_KEY") else "MISSING",
        "CEREBRAS_API_KEY": "SET" if os.getenv("CEREBRAS_API_KEY") else "MISSING", 
        "DAILY_API_KEY": "SET" if os.getenv("DAILY_API_KEY") else "MISSING",
        "GEMINI_API_KEY": "SET" if os.getenv("GEMINI_API_KEY") else "MISSING",
        "DATABASE_URL": "SET" if os.getenv("DATABASE_URL") else "MISSING",
        "WEBAPP_PORT": os.getenv("WEBAPP_PORT", "NOT_SET"),
        "RAILWAY_ENVIRONMENT": os.getenv("RAILWAY_ENVIRONMENT", "NOT_SET"),
    }


@app.get("/healthz", response_class=JSONResponse)
async def health_check():
    """Basic health check endpoint for Fly.io and other platforms"""
    result = await health_checker.basic_health()
    status_code = 200 if result["status"] == "healthy" else 503
    return JSONResponse(content=result, status_code=status_code)


@app.get("/health", response_class=JSONResponse)
async def standard_health():
    """Standard health check - includes database"""
    result = await health_checker.standard_health()
    status_code = 200 if result["status"] == "healthy" else 503
    return JSONResponse(content=result, status_code=status_code)


@app.get("/health/detailed", response_class=JSONResponse)
async def comprehensive_health():
    """Comprehensive health check - all components"""
    result = await health_checker.comprehensive_health()
    status_code = 200 if result["status"] == "healthy" else 503
    return JSONResponse(content=result, status_code=status_code)


@app.get("/health/ready", response_class=JSONResponse)
async def readiness_check():
    """Kubernetes-style readiness check"""
    result = await health_checker.standard_health()
    status_code = 200 if result["status"] == "healthy" else 503
    return JSONResponse(content=result, status_code=status_code)


@app.get("/health/live", response_class=JSONResponse)
async def liveness_check():
    """Kubernetes-style liveness check"""
    result = await health_checker.basic_health()
    return JSONResponse(content=result, status_code=200)