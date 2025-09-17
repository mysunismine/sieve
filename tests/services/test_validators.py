import pytest

from src.sieve.config import Settings
from src.sieve.services.exceptions import AskServiceError
from src.sieve.services.validators import clean_query, resolve_model, resolve_top_n


def test_clean_query_strips_and_returns_value():
    payload = type("Payload", (), {"query": "  hello ", "model": None, "top_n": None})()
    assert clean_query(payload) == "hello"


def test_clean_query_raises_for_empty_string():
    payload = type("Payload", (), {"query": "   ", "model": None, "top_n": None})()
    with pytest.raises(AskServiceError) as exc:
        clean_query(payload)
    assert exc.value.status_code == 422


def test_resolve_model_validates_against_settings():
    settings = Settings(openai_model="model-a", openai_model_options=["model-a", "model-b"])
    payload = type("Payload", (), {"query": "q", "model": "model-b", "top_n": None})()
    assert resolve_model(payload, settings) == "model-b"


def test_resolve_model_rejects_unknown_model():
    settings = Settings(openai_model="model-a", openai_model_options=["model-a"])
    payload = type("Payload", (), {"query": "q", "model": "bad", "top_n": None})()
    with pytest.raises(AskServiceError) as exc:
        resolve_model(payload, settings)
    assert exc.value.status_code == 400


def test_resolve_top_n_respects_limits():
    settings = Settings(default_top_n=5, min_top_n=1, max_top_n=10)
    payload = type("Payload", (), {"query": "q", "model": None, "top_n": 50})()
    assert resolve_top_n(payload, settings) == 10
    payload = type("Payload", (), {"query": "q", "model": None, "top_n": 0})()
    assert resolve_top_n(payload, settings) == 5
    payload = type("Payload", (), {"query": "q", "model": None, "top_n": -3})()
    assert resolve_top_n(payload, settings) == 1
