"""Routes exposing the Ask workflow."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from src.sieve.config import Settings, get_settings
from src.sieve.models.ask import AskRequest, AskResponse
from src.sieve.services.ask_service import process_ask_request

router = APIRouter(prefix="/api", tags=["ask"])


@router.post("/ask", response_model=AskResponse)
async def ask_endpoint(
    payload: AskRequest,
    settings: Settings = Depends(get_settings),
) -> AskResponse:
    """Handle incoming Ask requests."""
    return await process_ask_request(payload, settings)
