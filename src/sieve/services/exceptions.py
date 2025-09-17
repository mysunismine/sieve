"""Domain-specific service exceptions."""

from __future__ import annotations


class AskServiceError(Exception):
    """Domain-level error produced by the Ask service."""

    def __init__(self, detail: str, status_code: int) -> None:
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code
