"""Test configuration and shared fixtures."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure the project root (containing the ``src`` package) is importable when test
# commands are executed via the virtualenv entry point. Without this, ``pytest``
# launched as ``.venv/bin/pytest`` would miss the repository root on ``sys.path``
# leading to ``ModuleNotFoundError: src`` during collection.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def anyio_backend():
    """Run anyio-marked tests on the asyncio backend only."""
    return "asyncio"
