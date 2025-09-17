"""In-memory repository for Ask history entries."""

from __future__ import annotations

import threading
from collections.abc import Iterable
from uuid import UUID

from src.sieve.models.ask import Citation
from src.sieve.models.history import HistoryEntry, HistoryListResponse, HistoryResult
from src.sieve.services.google import SearchResult


class HistoryRepository:
    """Thread-safe in-memory storage for ask history."""

    def __init__(self, max_size: int) -> None:
        self._max_size = max_size
        self._items: list[HistoryEntry] = []
        self._lock = threading.Lock()

    def insert(
        self,
        *,
        query: str,
        top_n: int,
        model: str,
        answer_markdown: str,
        message: str | None,
        citations: Iterable[Citation],
        results: Iterable[SearchResult],
        search_used: bool,
    ) -> HistoryEntry:
        history_results = [
            HistoryResult(
                title=item.title,
                url=item.url,
                snippet=item.snippet,
                index=item.index,
            )
            for item in results
        ]

        entry = HistoryEntry(
            query=query,
            top_n=top_n,
            model=model,
            answer_markdown=answer_markdown,
            message=message,
            citations=list(citations),
            results=history_results,
            search_used=search_used,
        )

        with self._lock:
            self._items.insert(0, entry)
            if len(self._items) > self._max_size:
                self._items = self._items[: self._max_size]

        return entry

    def list(self) -> HistoryListResponse:
        with self._lock:
            items = list(self._items)
        return HistoryListResponse(items=items)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()

    def delete(self, entry_id: UUID) -> bool:
        with self._lock:
            for index, item in enumerate(self._items):
                if item.id == entry_id:
                    del self._items[index]
                    return True
        return False
