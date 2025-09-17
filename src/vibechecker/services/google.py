import logging
from dataclasses import dataclass
from typing import List
import httpx

from src.vibechecker.config import Settings

GOOGLE_SEARCH_ENDPOINT = "https://www.googleapis.com/customsearch/v1"
logger = logging.getLogger(__name__)


class GoogleSearchError(Exception):
    """Raised when Google search fails."""


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    index: int


async def search_google(query: str, top_n: int, settings: Settings) -> List[SearchResult]:
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
    results: List[SearchResult] = []
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
