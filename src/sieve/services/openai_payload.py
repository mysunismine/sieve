"""Helpers for interacting with the OpenAI Responses API."""

from __future__ import annotations

from typing import Any

from src.sieve.core.prompts import OPENAI_SYSTEM_PROMPT, build_user_prompt


def build_responses_payload(query: str, sources_block: str, model: str) -> dict[str, Any]:
    """Construct the request payload sent to the OpenAI Responses endpoint."""
    return {
        "model": model,
        "input": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": OPENAI_SYSTEM_PROMPT,
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": build_user_prompt(query=query, sources_block=sources_block),
                    }
                ],
            },
        ],
    }


def extract_answer_chunks(output_payload: dict[str, Any]) -> list[str]:
    """Pull text segments from OpenAI Responses output structure."""
    chunks: list[str] = []
    for item in output_payload.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"}:
                text = content.get("text", "")
                if text:
                    chunks.append(text)
    return chunks
