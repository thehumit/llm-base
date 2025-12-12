"""Factory helpers for OpenAI-compatible clients."""

from functools import lru_cache
from typing import Optional

from openai import OpenAI

from settings import settings


@lru_cache(maxsize=1)
def get_openai_client() -> OpenAI:
    """Return a singleton OpenAI client configured via settings."""
    return OpenAI(base_url=settings.litellm_url, api_key=settings.api_key)


def get_default_model(model: Optional[str] = None) -> str:
    """Resolve the model to use, fallback to settings."""
    return model or settings.model_name
