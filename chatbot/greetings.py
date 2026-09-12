"""Greeting and farewell detection kept separate from knowledge matching."""

import re


GREETINGS = {
    "hello", "hi", "hey", "greetings", "good morning", "good afternoon",
    "good evening", "what s up", "whats up", "sup",
}
FAREWELLS = {"bye", "goodbye", "exit", "quit", "see you"}


def _normalized_phrase(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", text.lower()).strip()


def is_greeting(text: str) -> bool:
    """Return true only when the whole short input is a greeting."""
    return _normalized_phrase(text) in GREETINGS


def is_farewell(text: str) -> bool:
    """Return true only when the whole short input is a farewell command."""
    return _normalized_phrase(text) in FAREWELLS


def greeting_response() -> str:
    return "Hello! Ask me about Python, NLP, or another topic in my knowledge base."


def farewell_response() -> str:
    return "Goodbye, take care!"


def is_thanks(text: str) -> bool:
    return bool(re.search(r"\bthank(?:s| you)?\b", text.lower()))
