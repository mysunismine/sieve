"""History management endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException

from src.sieve.models.history import HistoryListResponse
from src.sieve.services.history import (
    clear_history as clear_history_service,
    delete_history_entry as delete_history_entry_service,
    list_entries,
)

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=HistoryListResponse)
async def list_history() -> HistoryListResponse:
    """Return stored ask history."""
    return list_entries()


@router.delete("", response_model=HistoryListResponse)
async def clear_history() -> HistoryListResponse:
    """Remove all history entries."""
    clear_history_service()
    return list_entries()


@router.delete("/{entry_id}", response_model=HistoryListResponse)
async def delete_history_entry(entry_id: UUID) -> HistoryListResponse:
    """Delete a specific history entry."""
    deleted = delete_history_entry_service(entry_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Запись истории не найдена")
    return list_entries()
