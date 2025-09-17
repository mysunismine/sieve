import httpx
import pytest

from src.sieve.config import Settings
from src.sieve.services.google import GoogleSearchError, search_google


class DummyResponse:
    def __init__(self, status_code=200, json_data=None, text=""):
        self.status_code = status_code
        self._json_data = json_data or {}
        self.text = text

    def json(self):
        return self._json_data


@pytest.mark.asyncio
async def test_search_google_success(monkeypatch):
    recorded = {}
    response_payload = {
        "items": [
            {
                "title": "Result One",
                "link": "https://example.com/one",
                "snippet": "Snippet one",
            },
            {
                "title": "Result Two",
                "link": "https://example.com/two",
                "snippet": "Snippet two",
            },
        ]
    }
    dummy_response = DummyResponse(status_code=httpx.codes.OK, json_data=response_payload)

    class DummyClient:
        def __init__(self, *args, **kwargs):
            recorded["init_kwargs"] = kwargs

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def get(self, url, params=None):
            recorded["url"] = url
            recorded["params"] = params
            return dummy_response

    monkeypatch.setattr(httpx, "AsyncClient", DummyClient)

    settings = Settings(
        google_api_key="test-key",
        google_cse_id="test-cx",
        min_top_n=2,
        max_top_n=4,
    )

    results = await search_google("python", 3, settings)

    assert recorded["url"].endswith("/customsearch/v1")
    assert recorded["params"]["num"] == 3
    assert recorded["params"]["key"] == "test-key"
    assert recorded["params"]["cx"] == "test-cx"
    assert len(results) == 2
    assert results[0].index == 1
    assert results[1].url == "https://example.com/two"


@pytest.mark.asyncio
async def test_search_google_http_error(monkeypatch):
    class DummyClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def get(self, url, params=None):
            raise httpx.ReadTimeout("timeout")

    monkeypatch.setattr(httpx, "AsyncClient", lambda *args, **kwargs: DummyClient())

    settings = Settings(google_api_key="k", google_cse_id="cx")

    with pytest.raises(GoogleSearchError):
        await search_google("query", 1, settings)


@pytest.mark.asyncio
async def test_search_google_non_ok_status(monkeypatch):
    dummy_response = DummyResponse(status_code=500, text="boom")

    class DummyClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def get(self, url, params=None):
            return dummy_response

    monkeypatch.setattr(httpx, "AsyncClient", lambda *args, **kwargs: DummyClient())

    settings = Settings(google_api_key="k", google_cse_id="cx")

    with pytest.raises(GoogleSearchError):
        await search_google("query", 1, settings)
