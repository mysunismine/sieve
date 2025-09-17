"""Centralised constants shared across the application layers."""

from __future__ import annotations

# API endpoints and routing paths
GOOGLE_SEARCH_ENDPOINT = "https://www.googleapis.com/customsearch/v1"
OPENAI_RESPONSES_PATH = "/responses"

# Template configuration
DEFAULT_TEMPLATES_DIR = "templates"

# History configuration
DEFAULT_HISTORY_MAX_SIZE = 50

# Settings defaults
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
DEFAULT_OPENAI_MODEL_OPTIONS = ["gpt-4o-mini", "gpt-4o", "o4-mini"]
DEFAULT_OPENAI_TIMEOUT = 30.0
DEFAULT_OPENAI_BASE_URL = "https://api.openai.com/v1"
DEFAULT_GOOGLE_TIMEOUT = 10.0
DEFAULT_TOP_N = 5
MIN_TOP_N = 1
MAX_TOP_N = 10

# Miscellaneous text fragments
NO_SEARCH_RESULTS_FALLBACK = "(no search results available)"
CITATIONS_HEADER = "Citations:"  # keep UI wording consistent across layers
