"""Lightweight local intent detection."""

import re
from dataclasses import dataclass

from .greetings import is_farewell, is_greeting, is_thanks


@dataclass(frozen=True)
class Intent:
    """A detected action name with no hidden external model dependency."""

    name: str


class IntentDetector:
    """Detect simple conversational intents and route other text to knowledge."""

    _calculation = re.compile(r"\d\s*[+*/%()-]\s*\d")

    def detect(self, text: str) -> Intent:
        if is_greeting(text):
            return Intent("greeting")
        if is_thanks(text):
            return Intent("thanks")
        if is_farewell(text):
            return Intent("farewell")
        if self._calculation.search(text) or text.casefold().startswith(("calculate ", "compute ")):
            return Intent("calculator")
        return Intent("knowledge")