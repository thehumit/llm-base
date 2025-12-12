"""Legacy entry point that proxies to the Typer-powered CLI."""

from llm_cli.cli import app


def main() -> None:
    app()


if __name__ == "__main__":
    main()
