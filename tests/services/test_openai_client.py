import httpx
import pytest

from src.sieve.config import Settings
from src.sieve.services.google import SearchResult
from src.sieve.services.openai_client import OpenAIError, generate_answer


class DummyResponse:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self):
        return self._payload


@pytest.mark.anyio("asyncio")
async def test_generate_answer_success(monkeypatch):
    recorded = {}
    dummy_response = DummyResponse(
        status_code=httpx.codes.OK,
        payload={
            "id": "resp_123",
            "output": [
                {
                    "type": "message",
                    "content": [
                        {
                            "type": "output_text",
                            "text": "Here is the answer with a citation [1].",
                        }
                    ],
                }
            ],
        },
    )

    class DummyClient:
        def __init__(self, *args, **kwargs):
            recorded["init_kwargs"] = kwargs

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def post(self, url, headers=None, json=None):
            recorded["url"] = url
            recorded["headers"] = headers
            recorded["payload"] = json
            return dummy_response

    monkeypatch.setattr(httpx, "AsyncClient", DummyClient)

    settings = Settings(openai_api_key="secret", openai_base_url="https://api.example.com/v1")
    results = [
        SearchResult(
            title="Result One",
            url="https://example.com/one",
            snippet="Snippet one",
            index=1,
        )
    ]

    answer, response_id = await generate_answer("What is AI?", results, settings, model="gpt-test")

    assert "citations" in answer.lower()
    assert response_id == "resp_123"
    assert recorded["headers"]["Authorization"] == "Bearer secret"
    assert recorded["payload"]["model"] == "gpt-test"
    assert recorded["payload"]["input"][1]["content"][0]["text"].startswith("Question: What is AI?")
    assert recorded["url"] == "https://api.example.com/v1/responses"


@pytest.mark.anyio("asyncio")
async def test_generate_answer_non_ok_status(monkeypatch):
    dummy_response = DummyResponse(status_code=500, text="boom")

    class DummyClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def post(self, url, headers=None, json=None):
            return dummy_response

    monkeypatch.setattr(httpx, "AsyncClient", lambda *args, **kwargs: DummyClient())

    settings = Settings(openai_api_key="secret")

    with pytest.raises(OpenAIError):
        await generate_answer("Question", [], settings, model="gpt")


@pytest.mark.anyio("asyncio")
async def test_generate_answer_empty_output(monkeypatch):
    dummy_response = DummyResponse(status_code=httpx.codes.OK, payload={"output": []})

    class DummyClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def post(self, url, headers=None, json=None):
            return dummy_response

    monkeypatch.setattr(httpx, "AsyncClient", lambda *args, **kwargs: DummyClient())

    settings = Settings(openai_api_key="secret")

    with pytest.raises(OpenAIError):
        await generate_answer("Question", [], settings, model="gpt")
