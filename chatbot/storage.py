"""Small local JSON storage helpers."""

import json
from pathlib import Path
from typing import Any


def load_json(path: Path, default: Any = None) -> Any:
    """Load JSON data, returning a default when the file does not exist."""
    try:
        with path.open(encoding="utf-8") as data_file:
            return json.load(data_file)
    except FileNotFoundError:
        return default


def save_json(path: Path, data: Any) -> None:
    """Atomically save JSON data on the local filesystem."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_name(path.name + ".tmp")
    with temporary_path.open("w", encoding="utf-8") as data_file:
        json.dump(data, data_file, ensure_ascii=False, indent=2)
        data_file.write("\n")
    temporary_path.replace(path)