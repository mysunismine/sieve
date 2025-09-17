"""Prompt templates used by the OpenAI integration."""

from __future__ import annotations

OPENAI_SYSTEM_PROMPT = (
    "You are an assistant that writes concise markdown answers."
    " Always reference evidence with bracketed numbers such as [1], [2],"
    " matching the provided sources block."
    " If no sources are available, explain that search was unavailable."
    " Do not invent citations."
)

USER_PROMPT_TEMPLATE = (
    "Question: {query}\n\n"
    "Sources:\n{sources_block}\n\n"
    "Respond in markdown with inline citations."
)


def build_user_prompt(query: str, sources_block: str) -> str:
    """Render the user-facing prompt text for OpenAI Responses API."""
    return USER_PROMPT_TEMPLATE.format(query=query, sources_block=sources_block)
