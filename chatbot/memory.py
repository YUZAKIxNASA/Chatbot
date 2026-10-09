"""Temporary conversation memory with optional local persistence."""

from collections import deque
from pathlib import Path
from typing import Deque, List, Tuple

from .storage import load_json, save_json


class ConversationMemory:
    """Store recent exchanges in RAM unless local persistence is enabled."""

    def __init__(self, limit: int, path: Path, save_enabled: bool = False):
        self.limit = limit
        self.path = Path(path)
        self.save_enabled = save_enabled
        self._history: Deque[Tuple[str, str]] = deque(maxlen=limit)
        if save_enabled:
            saved = load_json(self.path, [])
            if isinstance(saved, list):
                self._history.extend(
                    (str(row[0]), str(row[1])) for row in saved
                    if isinstance(row, list) and len(row) == 2
                )

    def record(self, user: str, assistant: str) -> None:
        self._history.append((user, assistant))
        self._save()

    def recent(self) -> List[Tuple[str, str]]:
        return list(self._history)

    def clear(self) -> None:
        self._history.clear()
        self._save()

    def _save(self) -> None:
        if self.save_enabled:
            save_json(self.path, list(self._history))