"""Conversation pipeline for the local modular chatbot."""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

from config import (
    CONVERSATION_HISTORY_FILE,
    ENABLED_ACTIONS,
    HISTORY_LENGTH,
    KNOWLEDGE_FILE,
    KNOWLEDGE_STORE_FILE,
    MIN_CONFIDENCE,
    MODEL_NAME,
    RESPONSES_FILE,
    SAVE_CONVERSATION_HISTORY,
    TFIDF_ENABLED,
    VERSION,
)

from .greetings import farewell_response, greeting_response, is_farewell, is_greeting, is_thanks
from .action_router import ActionRouter
from .actions.calculator import calculate
from .intents import Intent, IntentDetector
from .knowledge import KnowledgeEntry, KnowledgeManager
from .memory import ConversationMemory
from .models import ModelManager, SearchResult
from .responses import ConfidenceManager, ResponseCatalog, ResponseGenerator


class ChatbotEngine:
    """Match questions to local facts and retain a short session history."""

    def __init__(self, knowledge_file=KNOWLEDGE_FILE, responses_file=RESPONSES_FILE,
                 min_confidence: float = MIN_CONFIDENCE, history_length: int = HISTORY_LENGTH,
                 knowledge_store_file=KNOWLEDGE_STORE_FILE,
                 save_history: bool = SAVE_CONVERSATION_HISTORY,
                 history_file=CONVERSATION_HISTORY_FILE,
                 model_manager: Optional[ModelManager] = None):
        self.knowledge_manager = KnowledgeManager(knowledge_file, knowledge_store_file)
        if not self.knowledge_manager.entries:
            raise ValueError("The knowledge base is empty")
        self.responses = ResponseCatalog(responses_file)
        self.min_confidence = min_confidence
        self.confidence = ConfidenceManager(min_confidence)
        self.response_generator = ResponseGenerator(self.responses, self.confidence)
        self.memory = ConversationMemory(history_length, history_file, save_history)
        self.intent_detector = IntentDetector()
        self.model_manager = model_manager or ModelManager(MODEL_NAME, TFIDF_ENABLED)
        self.action_router = ActionRouter()
        self._register_actions()
        self.questions = 0
        self.matched = 0
        self.fallbacks = 0

    @property
    def knowledge(self) -> List[str]:
        """Compatibility view of the current answer corpus."""
        return [entry.answer for entry in self.knowledge_manager.entries]

    def _register_actions(self) -> None:
        self.action_router.register("greeting", lambda message, context: greeting_response())
        self.action_router.register("thanks", lambda message, context: self.responses.thanks())
        self.action_router.register("farewell", lambda message, context: farewell_response())
        if ENABLED_ACTIONS.get("calculator", True):
            self.action_router.register("calculator", calculate)
        if ENABLED_ACTIONS.get("knowledge", True):
            self.action_router.register("knowledge", self._search_knowledge)

    def _search_knowledge(self, text: str, context=None) -> SearchResult:
        return self.model_manager.search(
            text,
            self.knowledge_manager.entries,
            self.knowledge_manager.revision,
        )

    def respond(self, user_input: str) -> str:
        """Generate a response and record the exchange."""
        text = user_input.strip()
        if not text:
            return self.responses.empty()
        self.questions += 1
        intent = self.intent_detector.detect(text)
        try:
            result = self.action_router.route(intent, text, self.memory.recent())
            response = self.response_generator.generate(intent, self.memory.recent(), result)
            if isinstance(result, SearchResult):
                if result.entry is not None and self.confidence.accepts(result.score):
                    self.matched += 1
                else:
                    self.fallbacks += 1
        except Exception:
            response = self.responses.error()
        self.memory.record(text, response)
        return response

    def _knowledge_response(self, text: str) -> str:
        result = self._search_knowledge(text)
        response = self.response_generator.generate(Intent("knowledge"), self.memory.recent(), result)
        if result.entry is not None and self.confidence.accepts(result.score):
            self.matched += 1
        else:
            self.fallbacks += 1
        return response

    def add_knowledge(self, question: str, answer: str, category: str = "general",
                      tags=None) -> KnowledgeEntry:
        return self.knowledge_manager.add(question, answer, category, tags)

    def update_knowledge(self, entry_id: str, **changes) -> KnowledgeEntry:
        return self.knowledge_manager.update(entry_id, **changes)

    def delete_knowledge(self, entry_id: str) -> None:
        self.knowledge_manager.delete(entry_id)

    def clear_history(self) -> None:
        self.memory.clear()

    def recent_history(self) -> List[Tuple[str, str]]:
        return self.memory.recent()

    def status(self) -> Dict[str, object]:
        return {
            "version": VERSION,
            "questions": self.questions,
            "matched": self.matched,
            "fallbacks": self.fallbacks,
            "history": len(self.memory.recent()),
            "model": self.model_manager.status(),
            "knowledge_entries": len(self.knowledge_manager.entries),
        }
