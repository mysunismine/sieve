"""Validation helpers specific to the Ask workflow."""

from __future__ import annotations

from src.sieve.config import Settings
from src.sieve.core.logging import get_logger
from src.sieve.models.ask import AskRequest
from src.sieve.services.exceptions import AskServiceError

logger = get_logger(__name__)


def clean_query(payload: AskRequest) -> str:
    query = payload.query.strip()
    if not query:
        raise AskServiceError("Текст запроса не может быть пустым", status_code=422)
    return query


def resolve_model(payload: AskRequest, settings: Settings) -> str:
    model_name = (payload.model or settings.openai_model).strip()
    allowed_models = set(settings.openai_model_options) | {settings.openai_model}
    if model_name not in allowed_models:
        logger.warning("Получен недопустимый идентификатор модели: %s", model_name)
        raise AskServiceError(
            "Выбранная модель недоступна. Обновите страницу и попробуйте снова.",
            status_code=400,
        )
    return model_name


def resolve_top_n(payload: AskRequest, settings: Settings) -> int:
    requested = payload.top_n or settings.default_top_n
    return max(settings.min_top_n, min(requested, settings.max_top_n))
