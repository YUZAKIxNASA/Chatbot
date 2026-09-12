"""Conversation engine for the local TF-IDF chatbot."""

from collections import deque
from typing import Deque, Dict, List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import HISTORY_LENGTH, MIN_CONFIDENCE, KNOWLEDGE_FILE, RESPONSES_FILE, VERSION

from .greetings import farewell_response, greeting_response, is_farewell, is_greeting, is_thanks
from .knowledge import load_knowledge
from .nlp import preprocess
from .responses import ResponseCatalog


class ChatbotEngine:
    """Match questions to local facts and retain a short session history."""

    def __init__(self, knowledge_file=KNOWLEDGE_FILE, responses_file=RESPONSES_FILE,
                 min_confidence: float = MIN_CONFIDENCE, history_length: int = HISTORY_LENGTH):
        self.knowledge = load_knowledge(knowledge_file)
        if not self.knowledge:
            raise ValueError("The knowledge base is empty")
        self.responses = ResponseCatalog(responses_file)
        self.min_confidence = min_confidence
        self.history: Deque[Tuple[str, str]] = deque(maxlen=history_length)
        self.questions = 0
        self.matched = 0
        self.fallbacks = 0
        self.vectorizer = TfidfVectorizer(tokenizer=preprocess, token_pattern=None)
        self.knowledge_vectors = self.vectorizer.fit_transform(self.knowledge)

    def respond(self, user_input: str) -> str:
        """Generate a response and record the exchange."""
        text = user_input.strip()
        if not text:
            return self.responses.empty()
        self.questions += 1
        if is_greeting(text):
            response = greeting_response()
        elif is_thanks(text):
            response = self.responses.thanks()
        elif is_farewell(text):
            response = farewell_response()
        else:
            try:
                response = self._knowledge_response(text)
            except Exception:
                response = self.responses.error()
        self.history.append((text, response))
        return response

    def _knowledge_response(self, text: str) -> str:
        try:
            query_vector = self.vectorizer.transform([text])
            scores = cosine_similarity(query_vector, self.knowledge_vectors)[0]
            best_index = int(scores.argmax())
            best_score = float(scores[best_index])
        except ValueError:
            best_index, best_score = 0, 0.0
        if best_score < self.min_confidence:
            self.fallbacks += 1
            return self.responses.random_fallback()
        self.matched += 1
        return self.knowledge[best_index]

    def clear_history(self) -> None:
        self.history.clear()

    def recent_history(self) -> List[Tuple[str, str]]:
        return list(self.history)

    def status(self) -> Dict[str, object]:
        return {
            "version": VERSION,
            "questions": self.questions,
            "matched": self.matched,
            "fallbacks": self.fallbacks,
            "history": len(self.history),
        }
