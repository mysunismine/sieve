import logging
from typing import List, Tuple
import httpx

from src.vibechecker.config import Settings
from src.vibechecker.services.google import SearchResult

OPENAI_RESPONSES_PATH = "/responses"
logger = logging.getLogger(__name__)


class OpenAIError(Exception):
    """Raised when OpenAI response generation fails."""


def _build_sources_block(results: List[SearchResult]) -> str:
    lines = []
    for result in results:
        lines.append(f"[{result.index}] {result.title}\n{result.url}\n{result.snippet}")
    return "\n\n".join(lines) if lines else "(no search results available)"


async def generate_answer(
    query: str, results: List[SearchResult], settings: Settings, model: str
) -> Tuple[str, str]:
    """Ask OpenAI Responses API to craft a markdown answer with citations."""
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }

    sources_block = _build_sources_block(results)
    prompt = (
        "You are an assistant that writes concise markdown answers."
        " Always reference evidence with bracketed numbers such as [1], [2],"
        " matching the provided sources block."
        " If no sources are available, explain that search was unavailable."
        " Do not invent citations."
    )

    payload = {
        "model": model,
        "input": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt,
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            f"Question: {query}\n\n"
                            f"Sources:\n{sources_block}\n\n"
                            "Respond in markdown with inline citations."
                        ),
                    }
                ],
            },
        ],
    }
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
    answer_chunks: List[str] = []
    for item in data.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"}:
                text = content.get("text", "")
                if text:
                    answer_chunks.append(text)

    answer = "\n".join(answer_chunks).strip()

    if not answer:
        logger.error("OpenAI вернул пустой ответ для запроса: %s", query)
        raise OpenAIError("OpenAI вернул пустой ответ")

    logger.info("Ответ OpenAI успешно получен (модель: %s)", model)
    return answer, data.get("id", "")
