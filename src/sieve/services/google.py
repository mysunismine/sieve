from dataclasses import dataclass

import httpx

from src.sieve.config import Settings
from src.sieve.core.constants import GOOGLE_SEARCH_ENDPOINT
from src.sieve.core.logging import get_logger

logger = get_logger(__name__)


class GoogleSearchError(Exception):
    """Raised when Google search fails."""


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    index: int


async def search_google(query: str, top_n: int, settings: Settings) -> list[SearchResult]:
    """Query Google Custom Search and return ordered search results."""
    params = {
        "key": settings.google_api_key,
        "cx": settings.google_cse_id,
        "q": query,
        "num": max(settings.min_top_n, min(top_n, settings.max_top_n)),
        "safe": "off",
    }

    try:
        async with httpx.AsyncClient(timeout=settings.google_timeout) as client:
            response = await client.get(GOOGLE_SEARCH_ENDPOINT, params=params)
    except httpx.HTTPError as exc:
        logger.error("Сетевая ошибка при обращении к Google CSE: %s", exc)
        raise GoogleSearchError("Сетевая ошибка при обращении к Google CSE") from exc

    if response.status_code != httpx.codes.OK:
        logger.error(
            "Google CSE вернул статус %s и тело ответа: %s",
            response.status_code,
            response.text,
        )
        raise GoogleSearchError(
            f"Ошибка Google CSE: {response.status_code} {response.text}"
        )

    payload = response.json()
    items = payload.get("items", [])
    results: list[SearchResult] = []
    for index, item in enumerate(items, start=1):
        results.append(
            SearchResult(
                title=item.get("title", ""),
                url=item.get("link", ""),
                snippet=item.get("snippet", ""),
                index=index,
            )
        )

    logger.info("Google поиск вернул %s результатов", len(results))
    return results
