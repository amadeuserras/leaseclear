from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, cast


def pretty_print(value: Any) -> None:
    title = "👋 Hello! 🖨️ Pretty print:"
    print(title)
    print(json.dumps(_to_jsonable(value), indent=2, default=str))


def _to_jsonable(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return asdict(value)
    if isinstance(value, list):
        items = cast(list[Any], value)
        return [_to_jsonable(item) for item in items]
    if isinstance(value, tuple):
        items = cast(tuple[Any, ...], value)
        return [_to_jsonable(item) for item in items]
    if isinstance(value, dict):
        mapping = cast(dict[str, Any], value)
        return {key: _to_jsonable(item) for key, item in mapping.items()}
    return value
