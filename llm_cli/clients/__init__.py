"""Shared client factories used across the CLI."""

from .openai_client import get_default_model, get_openai_client

__all__ = ["get_openai_client", "get_default_model"]
