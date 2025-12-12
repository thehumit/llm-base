"""Tools related to fetching content from the web."""

from __future__ import annotations

import re
from typing import Any, Dict

import requests
from bs4 import BeautifulSoup

from .registry import registry

MAX_CONTENT_LENGTH = 4000


def _clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def fetch_page(params: Dict[str, Any]) -> Dict[str, Any]:
    url = params["url"]
    headers = {"User-Agent": "llm-cli/0.1"}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as exc:
        return {
            "engine": "fetch_page",
            "url": url,
            "error": f"{exc.__class__.__name__}: {exc}",
        }

    soup = BeautifulSoup(resp.text, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else url
    text = soup.get_text(separator=" ")
    text = _clean_text(text)[:MAX_CONTENT_LENGTH]
    return {"engine": "fetch_page", "url": url, "title": title, "content": text}


FETCH_PAGE_TOOL = {
    "type": "function",
    "function": {
        "name": "fetch_page",
        "description": "Fetch the textual contents of a web page given a URL.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Fully qualified URL to fetch.",
                }
            },
            "required": ["url"],
        },
    },
}

registry.register(FETCH_PAGE_TOOL, fetch_page)

__all__ = ["fetch_page", "FETCH_PAGE_TOOL"]
