import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.api.router import api_router
from src.api.websocket import ws_router
from src.core.exceptions import register_exception_handlers
from src.database import engine
from src.services.websocket_manager import WebSocketManager

logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("ElderOS Vision API starting up")
    yield
    await engine.dispose()
    logger.info("ElderOS Vision API shut down")


def create_app() -> FastAPI:
    app = FastAPI(
        title="ElderOS Vision API",
        version="0.1.0",
        description="Backend API for ElderOS Vision — LTC facility safety monitoring",
        lifespan=lifespan,
    )

    # WebSocket manager (shared state for broadcasting)
    app.state.ws_manager = WebSocketManager()

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    register_exception_handlers(app)

    # REST API routes
    app.include_router(api_router)

    # WebSocket routes
    app.include_router(ws_router)

    return app


app = create_app()
