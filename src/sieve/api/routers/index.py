"""Routes serving the HTML frontend."""

from __future__ import annotations

from fastapi import Depends, APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.sieve.config import Settings, get_settings
from src.sieve.core.constants import DEFAULT_TEMPLATES_DIR

router = APIRouter(tags=["ui"])
templates = Jinja2Templates(directory=DEFAULT_TEMPLATES_DIR)


@router.get("/", response_class=HTMLResponse)
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
