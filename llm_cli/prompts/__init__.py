"""Prompt loading utilities for llm-cli."""

from __future__ import annotations

from pathlib import Path
from functools import lru_cache

PROMPTS_DIR = Path(__file__).resolve().parent


@lru_cache(maxsize=None)
def load_prompt(name: str) -> str:
    """Load a prompt file from the prompts directory."""
    path = PROMPTS_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Prompt '{name}' not found in {PROMPTS_DIR}")
    return path.read_text(encoding="utf-8").strip()


__all__ = ["load_prompt", "PROMPTS_DIR"]
