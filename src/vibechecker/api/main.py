import logging

from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.vibechecker.config import Settings, get_settings
from src.vibechecker.models.ask import AskRequest, AskResponse, Citation
from src.vibechecker.models.history import HistoryListResponse
from src.vibechecker.services.google import GoogleSearchError, search_google
from src.vibechecker.services.history import history_store
from src.vibechecker.services.openai_client import OpenAIError, generate_answer

app = FastAPI(title="VibeChecker", version="0.1.0")
templates = Jinja2Templates(directory="templates")
logger = logging.getLogger(__name__)


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    """Basic health endpoint for diagnostics."""
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, settings: Settings = Depends(get_settings)):
    """Render the minimal UI for manual interaction."""
    model_options = list(dict.fromkeys([settings.openai_model, *settings.openai_model_options]))

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "default_top_n": settings.default_top_n,
            "max_top_n": settings.max_top_n,
            "models": model_options,
            "default_model": settings.openai_model,
        },
    )


@app.post("/api/ask", response_model=AskResponse)
async def ask(
    payload: AskRequest,
    settings: Settings = Depends(get_settings),
) -> AskResponse:
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=422, detail="Текст запроса не может быть пустым")

    top_n = payload.top_n or settings.default_top_n
    model_name = (payload.model or settings.openai_model).strip()

    allowed_models = set(settings.openai_model_options) | {settings.openai_model}
    if model_name not in allowed_models:
        logger.warning("Получен недопустимый идентификатор модели: %s", model_name)
        raise HTTPException(
            status_code=400,
            detail="Выбранная модель недоступна. Обновите страницу и попробуйте снова.",
        )

    logger.info(
        "Поступил запрос: '%s' (источников: %s, модель: %s)",
        query,
        top_n,
        model_name,
    )

    message = None
    google_ready = bool(settings.google_api_key and settings.google_cse_id)
    if google_ready:
        try:
            results = await search_google(query=query, top_n=top_n, settings=settings)
        except GoogleSearchError as exc:  # Graceful degradation
            results = []
            message = str(exc)
            logger.warning("Поиск Google недоступен: %s", exc)
    else:
        results = []
        message = (
            "Google не настроен: ответ будет сформирован без внешнего поиска."
        )
        logger.info("Google API ключи отсутствуют, пропускаем поиск")

    if not settings.openai_api_key:
        logger.error("Запрос отклонён: отсутствует ключ OpenAI")
        raise HTTPException(status_code=500, detail="Ключ OpenAI не настроен.")

    try:
        answer, _ = await generate_answer(
            query=query, results=results, settings=settings, model=model_name
        )
    except OpenAIError as exc:
        logger.error("Ошибка OpenAI при обработке '%s': %s", query, exc)
        raise HTTPException(
            status_code=502, detail=str(exc) or "OpenAI вернул ошибку"
        ) from exc

    citations = [
        Citation(title=item.title, url=item.url, snippet=item.snippet, index=item.index)
        for item in results
    ]

    search_used = bool(results)
    if not search_used and message is None:
        message = "Поиск недоступен: ответ сгенерирован без внешних источников."

    logger.info("Ответ успешно сформирован (источников: %s)", len(citations))

    history_store.add_entry(
        query=query,
        top_n=top_n,
        model=model_name,
        answer_markdown=answer,
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


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("Приложение VibeChecker запущено")


@app.get("/api/history", response_model=HistoryListResponse)
async def get_history() -> HistoryListResponse:
    """Вернуть историю запросов."""
    return history_store.list_entries()


@app.delete("/api/history", response_model=HistoryListResponse)
async def clear_history() -> HistoryListResponse:
    """Удалить всю историю запросов."""
    history_store.clear()
    logger.info("История запросов очищена")
    return history_store.list_entries()


@app.delete("/api/history/{entry_id}", response_model=HistoryListResponse)
async def delete_history_entry(entry_id: UUID) -> HistoryListResponse:
    """Удалить конкретную запись истории."""
    deleted = history_store.delete(entry_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Запись истории не найдена")
    logger.info("Запись истории %s удалена", entry_id)
    return history_store.list_entries()
