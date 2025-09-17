"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI

from src.sieve.api.error_handlers import register_error_handlers
from src.sieve.api.routers import ask_router, health_router, history_router, index_router
from src.sieve.core.logging import get_logger

logger = get_logger(__name__)


def build_app() -> FastAPI:
    """Construct the FastAPI application with routers and middleware."""
    app = FastAPI(title="Sieve", version="0.1.0")
    app.include_router(health_router)
    app.include_router(index_router)
    app.include_router(ask_router)
    app.include_router(history_router)

    register_error_handlers(app)

    @app.on_event("startup")
    async def _startup_event() -> None:  # pragma: no cover - side-effect logging
        logger.info("Приложение Sieve запущено")

    return app


app = build_app()
