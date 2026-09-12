"""Configurable response data and response selection."""

import json
import random
from pathlib import Path
from typing import Any, Dict


DEFAULT_RESPONSES: Dict[str, Any] = {
    "fallback": [
        "I do not know that yet. Try asking about Python, NLP, or chatbots.",
        "I could not find a confident match. Try rephrasing your question.",
    ],
    "thanks": ["You are welcome!"],
    "empty": "Please enter a question, or type 'help' for commands.",
    "error": "I ran into a problem while searching my knowledge base.",
}


class ResponseCatalog:
    """Load editable response text while retaining safe defaults."""

    def __init__(self, path: Path):
        self.data = dict(DEFAULT_RESPONSES)
        try:
            with path.open(encoding="utf-8") as response_file:
                loaded = json.load(response_file)
            if isinstance(loaded, dict):
                self.data.update(loaded)
        except (OSError, json.JSONDecodeError):
            pass

    def random_fallback(self) -> str:
        fallbacks = self.data.get("fallback", DEFAULT_RESPONSES["fallback"])
        return random.choice(fallbacks)

    def thanks(self) -> str:
        return self.data["thanks"][0]

    def empty(self) -> str:
        return self.data["empty"]

    def error(self) -> str:
        return self.data["error"]
