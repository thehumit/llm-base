"""Primary CLI entry point for llm-cli."""

from __future__ import annotations

import json
from typing import Optional

import typer

from llm_cli.tools import search as search_tools

app = typer.Typer(help="Personal assistant CLI powered by LLMs.", add_completion=False)
agent_app = typer.Typer(help="Agent-style commands.")
app.add_typer(agent_app, name="agent")

AVAILABLE_ENGINES = search_tools.engine_registry.names()


@app.command()
def search(
    query: str = typer.Argument(..., help="Text to pass to the search tool."),
    engine: str = typer.Option(
        "tavily",
        "--engine",
        "-e",
        help=f"Search engine to use ({', '.join(AVAILABLE_ENGINES)}).",
    ),
    raw: bool = typer.Option(
        False,
        "--raw",
        "-r",
        help="Return raw search results instead of invoking the LLM.",
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model",
        "-m",
        help="Override the default chat model.",
    ),
) -> None:
    """Perform a search via Tavily/DuckDuckGo or run the search-enabled chat loop."""
    if raw:
        result = search_tools.search_web({"query": query, "engine": engine})
        typer.echo(json.dumps(result, indent=2))
    else:
        search_tools.run_chat(query, model=model)


@app.command()
def chat(
    question: str = typer.Argument(..., help="Prompt for a quick LLM response."),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Override the chat model."),
) -> None:
    """Temporary chat entry point that reuses the search-enabled agent."""
    search_tools.run_chat(question, model=model)


@agent_app.command("deepresearch")
def agent_deepresearch(
    query: str = typer.Argument(..., help="Research topic for the agent."),
) -> None:
    """Placeholder deep-research agent endpoint."""
    typer.echo(
        "The deepresearch agent is not implemented yet. "
        "Use `llm-cli search` or `llm-cli chat` for now."
    )


def main() -> None:
    """Entry point used by python -m llm_cli.cli or main.py."""
    app()


if __name__ == "__main__":
    main()
