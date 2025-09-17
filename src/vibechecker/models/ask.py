from typing import List, Optional
from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    query: str = Field(min_length=1, description="User question to process")
    top_n: Optional[int] = Field(default=None, ge=1, le=10, description="Number of search results")
    model: Optional[str] = Field(default=None, description="Preferred OpenAI model identifier")


class Citation(BaseModel):
    title: str
    url: str
    snippet: str
    index: int


class AskResponse(BaseModel):
    answer_markdown: str
    citations: List[Citation]
    search_used: bool
    message: Optional[str] = None
