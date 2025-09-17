"""Application service encapsulating the Ask use case."""

from __future__ import annotations

from typing import Iterable

from src.sieve.config import Settings
from src.sieve.core.logging import get_logger
from src.sieve.models.ask import AskRequest, AskResponse, Citation
from src.sieve.services.google import GoogleSearchError, SearchResult, search_google
from src.sieve.services.history import add_history_entry
from src.sieve.services.openai_client import OpenAIError, generate_answer
from src.sieve.services.validators import clean_query, resolve_model, resolve_top_n
from src.sieve.services.exceptions import AskServiceError

logger = get_logger(__name__)


async def _maybe_search_google(
    query: str, top_n: int, settings: Settings
) -> tuple[list[SearchResult], str | None]:
    google_ready = bool(settings.google_api_key and settings.google_cse_id)
    if not google_ready:
        logger.info("Google API ключи отсутствуют, пропускаем поиск")
        return [], "Google не настроен: ответ будет сформирован без внешнего поиска."

    try:
        results = await search_google(query=query, top_n=top_n, settings=settings)
        return results, None
    except GoogleSearchError as exc:
        logger.warning("Поиск Google недоступен: %s", exc)
        return [], str(exc)


def _ensure_openai_ready(settings: Settings) -> None:
    if not settings.openai_api_key:
        logger.error("Запрос отклонён: отсутствует ключ OpenAI")
        raise AskServiceError("Ключ OpenAI не настроен.", status_code=500)


def _build_citations(results: Iterable[SearchResult]) -> list[Citation]:
    return [
        Citation(title=item.title, url=item.url, snippet=item.snippet, index=item.index)
        for item in results
    ]


def _persist_history(
    *,
    query: str,
    top_n: int,
    model_name: str,
    answer: str,
    message: str | None,
    citations: list[Citation],
    results: list[SearchResult],
    search_used: bool,
) -> None:
    add_history_entry(
        query=query,
        top_n=top_n,
        model=model_name,
        answer_markdown=answer,
        message=message,
        citations=citations,
        results=results,
        search_used=search_used,
    )


async def process_ask_request(payload: AskRequest, settings: Settings) -> AskResponse:
    """Main entry point for orchestrating the ask workflow."""
    query = clean_query(payload)
    model_name = resolve_model(payload, settings)
    top_n = resolve_top_n(payload, settings)

    logger.info(
        "Поступил запрос: '%s' (источников: %s, модель: %s)", query, top_n, model_name
    )

    results, message = await _maybe_search_google(query, top_n, settings)
    _ensure_openai_ready(settings)

    try:
        answer, _ = await generate_answer(
            query=query, results=results, settings=settings, model=model_name
        )
    except OpenAIError as exc:
        logger.error("Ошибка OpenAI при обработке '%s': %s", query, exc)
        raise AskServiceError(str(exc) or "OpenAI вернул ошибку", status_code=502) from exc

    citations = _build_citations(results)
    search_used = bool(results)
    if not search_used and message is None:
        message = "Поиск недоступен: ответ сгенерирован без внешних источников."

    logger.info("Ответ успешно сформирован (источников: %s)", len(citations))
    _persist_history(
        query=query,
        top_n=top_n,
        model_name=model_name,
        answer=answer,
        message=message,
        citations=citations,
        results=results,
        search_used=search_used,
    )

    return AskResponse(
        answer_markdown=answer,
        citations=citations,
        search_used=search_used,
        message=message,
    )
