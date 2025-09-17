"""FastAPI routers grouped by feature."""

from __future__ import annotations

from .ask import router as ask_router
from .health import router as health_router
from .history import router as history_router
from .index import router as index_router

__all__ = [
    "ask_router",
    "health_router",
    "history_router",
    "index_router",
]
