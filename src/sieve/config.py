from functools import lru_cache

from pydantic_settings import BaseSettings

from src.sieve.core.constants import (
    DEFAULT_GOOGLE_TIMEOUT,
    DEFAULT_OPENAI_BASE_URL,
    DEFAULT_OPENAI_MODEL,
    DEFAULT_OPENAI_MODEL_OPTIONS,
    DEFAULT_OPENAI_TIMEOUT,
    DEFAULT_TOP_N,
    MAX_TOP_N,
    MIN_TOP_N,
)


class Settings(BaseSettings):
    google_api_key: str = ""
    google_cse_id: str = ""
    openai_api_key: str = ""
    openai_model: str = DEFAULT_OPENAI_MODEL
    openai_model_options: list[str] = DEFAULT_OPENAI_MODEL_OPTIONS
    openai_base_url: str = DEFAULT_OPENAI_BASE_URL
    google_timeout: float = DEFAULT_GOOGLE_TIMEOUT
    openai_timeout: float = DEFAULT_OPENAI_TIMEOUT
    default_top_n: int = DEFAULT_TOP_N
    min_top_n: int = MIN_TOP_N
    max_top_n: int = MAX_TOP_N

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
