from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    google_api_key: str = ""
    google_cse_id: str = ""
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_model_options: List[str] = ["gpt-4o-mini", "gpt-4o", "o4-mini"]
    openai_base_url: str = "https://api.openai.com/v1"
    google_timeout: float = 10.0
    openai_timeout: float = 30.0
    default_top_n: int = 5
    min_top_n: int = 1
    max_top_n: int = 10

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
