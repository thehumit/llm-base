"""Search tool implementations and CLI helpers."""

from __future__ import annotations

import argparse
import json
from typing import Any, Callable, Dict, List

from duckduckgo_search import DDGS
from tavily import TavilyClient

from llm_cli.clients import get_default_model, get_openai_client
from llm_cli.prompts import load_prompt
from llm_cli.tools.registry import registry
from settings import settings


# ============================================================
# Search engine interfaces
# ============================================================
class SearchEngineBase:
    def search(self, query: str) -> Dict[str, Any]:
        """Return a dictionary with the search results."""
        raise NotImplementedError


class TavilyEngine(SearchEngineBase):
    """Preferred search engine that requires the Tavily API key."""

    def __init__(self, api_key: str | None = None, max_results: int = 10):
        self.client = TavilyClient(api_key=api_key or settings.tavily_api_key)
        self.max_results = max_results

    def search(self, query: str) -> Dict[str, Any]:
        result = self.client.search(
            query,
            include_domains=None,
            max_results=self.max_results,
        )
        return {
            "engine": "tavily",
            "query": query,
            "results": result["results"],
        }


class DuckDuckGoEngine(SearchEngineBase):
    """Fallback engine when no API key is available."""

    def __init__(self, *, max_results: int = 5, **kwargs: Any):
        self.max_results = max_results
        self.kwargs = kwargs

    def search(self, query: str) -> Dict[str, Any]:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=self.max_results, **self.kwargs))
        return {"engine": "duckduckgo", "query": query, "results": results}


class CustomAPIEngine(SearchEngineBase):
    """Example engine that demonstrates how to plug in another provider."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key or getattr(settings, "custom_search_api_key", "demo-key")
        self.base_url = base_url or "https://my-custom-search.com/api"

    def search(self, query: str) -> Dict[str, Any]:
        # Example placeholder for a real API call.
        return {
            "engine": "custom_api",
            "query": query,
            "results": [{"title": "Example", "url": "https://example.com"}],
        }


# ============================================================
# Registry helpers
# ============================================================
class SearchEngineRegistry:
    def __init__(self) -> None:
        self._factories: Dict[str, Callable[[], SearchEngineBase]] = {}

    def register(self, name: str, factory: Callable[[], SearchEngineBase]) -> None:
        self._factories[name] = factory

    def get(self, name: str) -> SearchEngineBase:
        try:
            return self._factories[name]()
        except KeyError as exc:
            raise ValueError(f"Unknown search engine '{name}'") from exc

    def names(self) -> List[str]:
        return sorted(self._factories.keys())


engine_registry = SearchEngineRegistry()
engine_registry.register("tavily", lambda: TavilyEngine())
engine_registry.register("duckduckgo", lambda: DuckDuckGoEngine())
engine_registry.register("custom_api", lambda: CustomAPIEngine())


# ============================================================
# Tool wiring
# ============================================================
def search_web(params: Dict[str, Any]) -> Dict[str, Any]:
    query = params["query"]
    engine_name = params.get("engine", "tavily").lower()
    try:
        engine_impl = engine_registry.get(engine_name)
    except ValueError:
        engine_impl = engine_registry.get("duckduckgo")
    return engine_impl.search(query)


SEARCH_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "search_web",
        "description": "Perform an internet search using DuckDuckGo by default.",
        "parameters": {
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Query text to search",
                },
                "engine": {
                    "type": "string",
                    "description": f"Engine name ({', '.join(engine_registry.names())})",
                },
            },
        },
    },
}

registry.register(SEARCH_TOOL_SCHEMA, search_web)


# ============================================================
# Chat loop that uses the search tool
# ============================================================
SEARCH_SYSTEM_PROMPT = load_prompt("search_assistant.md")


def run_chat(query: str, *, model: str | None = None) -> None:
    client = get_openai_client()
    model_name = get_default_model(model)

    messages = [
        {"role": "system", "content": SEARCH_SYSTEM_PROMPT},
        {"role": "user", "content": query},
    ]
    finish_reason = None

    while finish_reason is None or finish_reason == "tool_calls":
        completion = client.chat.completions.create(
            model=model_name,
            messages=messages,
            tools=registry.schemas(),
            tool_choice="auto",
            temperature=0.2,
        )

        choice = completion.choices[0]
        finish_reason = choice.finish_reason

        if finish_reason == "tool_calls":
            messages.append(choice.message)

            for tool_call in choice.message.tool_calls:
                tool_result = registry.execute(tool_call)
                print("tool_result", tool_result)

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": json.dumps(tool_result),
                    }
                )

    print(choice.message.content)


# ============================================================
# CLI
# ============================================================
def cli(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="CLI search with LLM tool calling.",
    )
    parser.add_argument("query", type=str, help="Search query string")
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Override the default model configured in settings",
    )
    parser.add_argument(
        "--engine",
        type=str,
        choices=engine_registry.names(),
        default="tavily",
        help="Engine to use when returning raw search results",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Return raw search results (skip the chat completion).",
    )
    args = parser.parse_args(argv)

    if args.raw:
        result = search_web({"query": args.query, "engine": args.engine})
        print(json.dumps(result, indent=2))
    else:
        run_chat(args.query, model=args.model)


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
