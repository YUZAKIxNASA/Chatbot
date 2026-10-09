"""Local retrieval models and model selection."""

from dataclasses import dataclass
from typing import List, Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import MODEL_NAME, TFIDF_ENABLED

from .knowledge import KnowledgeEntry
from .nlp import preprocess


@dataclass
class SearchResult:
    """Best local retrieval match and its similarity score."""

    entry: Optional[KnowledgeEntry]
    score: float


class TfidfModel:
    """Cache a TF-IDF index and rebuild it after knowledge changes."""

    def __init__(self):
        self._revision = -1
        self._vectorizer = None
        self._vectors = None
        self._entries: List[KnowledgeEntry] = []

    def rebuild(self, entries: List[KnowledgeEntry], revision: int) -> None:
        self._entries = list(entries)
        self._revision = revision
        if not entries:
            self._vectorizer = None
            self._vectors = None
            return
        self._vectorizer = TfidfVectorizer(tokenizer=preprocess, token_pattern=None)
        self._vectors = self._vectorizer.fit_transform(
            [f"{entry.question} {entry.answer} {' '.join(entry.tags)}" for entry in entries]
        )

    def search(self, text: str, entries: List[KnowledgeEntry], revision: int) -> SearchResult:
        if revision != self._revision:
            self.rebuild(entries, revision)
        if self._vectorizer is None or self._vectors is None:
            return SearchResult(None, 0.0)
        try:
            query_vector = self._vectorizer.transform([text])
            scores = cosine_similarity(query_vector, self._vectors)[0]
            best_index = int(scores.argmax())
            return SearchResult(self._entries[best_index], float(scores[best_index]))
        except ValueError:
            return SearchResult(None, 0.0)


class ModelManager:
    """Expose a consistent interface for enabled local retrieval models."""

    def __init__(self, selected: str = MODEL_NAME, tfidf_enabled: bool = TFIDF_ENABLED):
        self.selected = selected
        self.enabled = tfidf_enabled and selected == "tfidf"
        self._tfidf = TfidfModel() if self.enabled else None

    def search(self, text: str, entries: List[KnowledgeEntry], revision: int) -> SearchResult:
        if not self.enabled or self._tfidf is None:
            return SearchResult(None, 0.0)
        return self._tfidf.search(text, entries, revision)

    def status(self) -> dict:
        return {"selected": self.selected, "enabled": self.enabled}