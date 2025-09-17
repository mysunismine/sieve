from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from src.vibechecker.models.ask import Citation


class HistoryResult(BaseModel):
    title: str
    url: str
    snippet: str
    index: int


class HistoryEntry(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    query: str
    top_n: int
    model: str
    answer_markdown: str
    message: Optional[str] = None
    citations: List[Citation]
    results: List[HistoryResult]
    search_used: bool
    created_at: datetime = Field(default_factory=datetime.utcnow)


class HistoryListResponse(BaseModel):
    items: List[HistoryEntry]
