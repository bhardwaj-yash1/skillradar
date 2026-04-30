"""Provider-aware OpenAI-compatible client helpers."""

from __future__ import annotations

from openai import AsyncOpenAI

from backend.config import Settings


def build_async_llm_client(settings: Settings) -> AsyncOpenAI:
    """Build an OpenAI-compatible async client for the selected provider."""
    return AsyncOpenAI(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        default_headers=settings.llm_default_headers or None,
    )
