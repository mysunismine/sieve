import httpx

from src.sieve.config import Settings
from src.sieve.core.constants import (
    CITATIONS_HEADER,
    NO_SEARCH_RESULTS_FALLBACK,
    OPENAI_RESPONSES_PATH,
)
from src.sieve.core.logging import get_logger
from src.sieve.services.google import SearchResult
from src.sieve.services.openai_payload import extract_answer_chunks, build_responses_payload
logger = get_logger(__name__)


class OpenAIError(Exception):
    """Raised when OpenAI response generation fails."""


def _build_sources_block(results: list[SearchResult]) -> str:
    lines = []
    for result in results:
        lines.append(f"[{result.index}] {result.title}\n{result.url}\n{result.snippet}")
    return "\n\n".join(lines) if lines else NO_SEARCH_RESULTS_FALLBACK


async def generate_answer(
    query: str, results: list[SearchResult], settings: Settings, model: str
) -> tuple[str, str]:
    """Ask OpenAI Responses API to craft a markdown answer with citations."""
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }

    sources_block = _build_sources_block(results)
    payload = build_responses_payload(query=query, sources_block=sources_block, model=model)
    url = f"{settings.openai_base_url.rstrip('/')}{OPENAI_RESPONSES_PATH}"
    try:
        async with httpx.AsyncClient(timeout=settings.openai_timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
    except httpx.HTTPError as exc:
        logger.error("Ошибка сети при обращении к OpenAI: %s", exc)
        raise OpenAIError("Сетевая ошибка при обращении к OpenAI") from exc

    if response.status_code != httpx.codes.OK:
        logger.error(
            "OpenAI вернул статус %s и тело ответа: %s",
            response.status_code,
            response.text,
        )
        raise OpenAIError(f"Ошибка OpenAI: {response.status_code} {response.text}")

    try:
        data = response.json()
    except ValueError as exc:
        logger.error("Не удалось разобрать JSON от OpenAI: %s", exc)
        raise OpenAIError("Некорректный JSON в ответе OpenAI") from exc
    answer_chunks = extract_answer_chunks(data)
    answer = "\n".join(answer_chunks).strip()

    if not answer:
        logger.error("OpenAI вернул пустой ответ для запроса: %s", query)
        raise OpenAIError("OpenAI вернул пустой ответ")

    citations_block = _build_sources_block(results)
    # Append an explicit citations footer so the UI (and tests) always presents
    # the supporting sources together with the model answer.
    answer_with_citations = f"{answer}\n\n{CITATIONS_HEADER}\n{citations_block}".strip()

    logger.info("Ответ OpenAI успешно получен (модель: %s)", model)
    return answer_with_citations, data.get("id", "")
