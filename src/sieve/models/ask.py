from __future__ import annotations

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    query: str = Field(min_length=1, description="User question to process")
    top_n: int | None = Field(default=None, ge=1, le=10, description="Number of search results")
    model: str | None = Field(default=None, description="Preferred OpenAI model identifier")


class Citation(BaseModel):
    title: str
    url: str
    snippet: str
    index: int


class AskResponse(BaseModel):
    answer_markdown: str
    citations: list[Citation]
    search_used: bool
    message: str | None = None
