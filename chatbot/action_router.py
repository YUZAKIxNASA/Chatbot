"""Registry that maps detected intents to independent local actions."""

from typing import Any, Callable, Dict

from .intents import Intent


ActionHandler = Callable[[str, Any], Any]


class ActionRouter:
    """Register and invoke handlers without embedding actions in the engine."""

    def __init__(self):
        self._handlers: Dict[str, ActionHandler] = {}

    def register(self, name: str, handler: ActionHandler) -> None:
        self._handlers[name] = handler

    def route(self, intent: Intent, message: str, context: Any = None) -> Any:
        handler = self._handlers.get(intent.name)
        if handler is None:
            raise KeyError(f"No action is registered for intent {intent.name!r}")
        return handler(message, context)