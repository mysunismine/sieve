"""Healthcheck endpoints."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def healthcheck() -> dict[str, str]:
    """Basic health endpoint for diagnostics."""
    return {"status": "ok"}
