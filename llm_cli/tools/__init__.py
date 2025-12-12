"""Tool implementations for llm-cli."""

from .registry import registry
from . import web  # noqa: F401 ensures fetch_page registers
from .search import (
    SearchEngineBase,
    TavilyEngine,
    DuckDuckGoEngine,
    CustomAPIEngine,
    search_web,
    SEARCH_TOOL_SCHEMA,
    run_chat,
)

__all__ = [
    "registry",
    "SearchEngineBase",
    "TavilyEngine",
    "DuckDuckGoEngine",
    "CustomAPIEngine",
    "search_web",
    "SEARCH_TOOL_SCHEMA",
    "run_chat",
]
