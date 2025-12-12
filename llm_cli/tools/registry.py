"""Registry for OpenAI tool specifications and callables."""

from __future__ import annotations

import json
from typing import Any, Callable, Dict, Iterable, List


class ToolCall:
    """Minimal structure representing a tool call from OpenAI."""

    def __init__(self, name: str, arguments: str, call_id: str | None = None):
        self.name = name
        self.arguments = arguments
        self.id = call_id


class ToolRegistry:
    def __init__(self) -> None:
        self._functions: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {}
        self._schemas: List[Dict[str, Any]] = []

    def register(self, schema: Dict[str, Any], func: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        name = schema["function"]["name"]
        self._functions[name] = func
        self._schemas.append(schema)

    def schemas(self) -> List[Dict[str, Any]]:
        return list(self._schemas)

    def execute(self, tool_call: Any) -> Dict[str, Any]:
        # tool_call is an OpenAI object but duck-type for portability
        func_payload = getattr(tool_call, "function", None)
        if func_payload is not None:
            name = getattr(func_payload, "name", None)
            arguments = getattr(func_payload, "arguments", "{}")
        else:
            name = getattr(tool_call, "name")
            arguments = getattr(tool_call, "arguments", "{}")

        func = self._functions[name]
        params = json.loads(arguments)
        return func(params)


registry = ToolRegistry()

__all__ = ["registry", "ToolRegistry", "ToolCall"]
