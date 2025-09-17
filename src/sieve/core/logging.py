"""Central logging utilities."""

from __future__ import annotations

import logging
from typing import Any

_DEFAULT_LEVEL = logging.INFO


def configure_logging(level: int = _DEFAULT_LEVEL, **kwargs: Any) -> None:
    """Configure application-wide logging if not already set."""
    if logging.getLogger().handlers:
        return
    logging.basicConfig(level=level, **kwargs)


def get_logger(name: str) -> logging.Logger:
    """Return a module-specific logger ensuring global configuration."""
    configure_logging()
    return logging.getLogger(name)
