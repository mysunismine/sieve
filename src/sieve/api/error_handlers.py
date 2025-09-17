"""Application-wide exception handlers."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.sieve.core.logging import get_logger
from src.sieve.services.exceptions import AskServiceError

logger = get_logger(__name__)


def register_error_handlers(app: FastAPI) -> None:
    """Attach custom exception handlers to the FastAPI app."""

    @app.exception_handler(AskServiceError)
    async def _ask_service_error_handler(
        request: Request, exc: AskServiceError
    ) -> JSONResponse:
        logger.debug("Handling AskServiceError for request %s", request.url)
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
