from __future__ import annotations

from collections.abc import Iterable
from uuid import UUID

from src.sieve.core.constants import DEFAULT_HISTORY_MAX_SIZE
from src.sieve.models.ask import Citation
from src.sieve.models.history import HistoryListResponse
from src.sieve.repositories.history_repository import HistoryRepository
from src.sieve.services.google import SearchResult


class HistoryStore(HistoryRepository):
    """Backwards-compatible alias for the in-memory history repository."""

    def __init__(self, max_size: int = DEFAULT_HISTORY_MAX_SIZE) -> None:
        super().__init__(max_size)

    def add_entry(
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
    ):
        return self.insert(
            query=query,
            top_n=top_n,
            model=model,
            answer_markdown=answer_markdown,
            message=message,
            citations=citations,
            results=results,
            search_used=search_used,
        )

    def list_entries(self) -> HistoryListResponse:
        return self.list()

    def clear(self) -> None:
        super().clear()

    def delete(self, entry_id: UUID) -> bool:
        return super().delete(entry_id)


def add_history_entry(
    *,
    query: str,
    top_n: int,
    model: str,
    answer_markdown: str,
    message: str | None,
    citations: list[Citation],
    results: list[SearchResult],
    search_used: bool,
) -> None:
    history_store.add_entry(
        query=query,
        top_n=top_n,
        model=model,
        answer_markdown=answer_markdown,
        message=message,
        citations=citations,
        results=results,
        search_used=search_used,
    )


def list_entries() -> HistoryListResponse:
    return history_store.list_entries()


def clear_history() -> None:
    history_store.clear()


def delete_history_entry(entry_id: UUID) -> bool:
    return history_store.delete(entry_id)


history_store = HistoryStore()
