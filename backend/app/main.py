"""Application bootstrapping only.

Responsibilities:
- Create FastAPI application
- Register middleware
- Register exception handlers
- Register routers
- Configure CORS
- Health endpoint

No business logic belongs here.
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import check_database_connection
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.core.redis_client import check_redis_connection

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan: run startup and shutdown routines."""
    configure_logging()
    logger.info("Starting %s in %s mode", settings.APP_NAME, settings.ENVIRONMENT)

    db_ok = await check_database_connection()
    if not db_ok:
        logger.error("Database connectivity check failed on startup")

    redis_ok = await check_redis_connection()
    if not redis_ok:
        logger.warning("Redis connectivity check failed on startup")

    yield

    logger.info("Shutting down %s", settings.APP_NAME)


def create_application() -> FastAPI:
    """Build and configure the FastAPI application."""
    application = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(application)

    from app.api_router import api_router

    application.include_router(api_router, prefix="/api/v1")

    @application.get("/api/v1/health", tags=["health"])
    async def health() -> dict:
        db_ok = await check_database_connection()
        redis_ok = await check_redis_connection()
        return {
            "status": "ok" if (db_ok and redis_ok) else "degraded",
            "app": settings.APP_NAME,
            "environment": settings.ENVIRONMENT,
            "database": "ok" if db_ok else "unavailable",
            "redis": "ok" if redis_ok else "unavailable",
        }

    return application


app = create_application()