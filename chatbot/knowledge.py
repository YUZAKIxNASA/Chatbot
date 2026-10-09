"""Local knowledge loading, editing, importing, and searching."""

import csv
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from .nlp import split_sentences
from .storage import load_json, save_json


@dataclass
class KnowledgeEntry:
    """One question and answer stored in the local knowledge base."""

    id: str
    category: str
    question: str
    answer: str
    tags: List[str]


def _normalized(text: str) -> str:
    return " ".join(re.findall(r"\w+", text.casefold()))


def load_knowledge(path: Path) -> List[str]:
    """Load knowledge facts from a UTF-8 text file."""
    with path.open(encoding="utf-8") as knowledge_file:
        return split_sentences(knowledge_file.read())


class KnowledgeManager:
    """Manage persistent entries, seeded from the legacy text file if needed."""

    def __init__(self, source_path: Path, store_path: Path):
        self.source_path = Path(source_path)
        self.store_path = Path(store_path)
        saved = load_json(self.store_path)
        if saved is None:
            facts = load_knowledge(self.source_path)
            self.entries = [
                KnowledgeEntry(f"legacy_{index:04d}", "general", fact, fact, [])
                for index, fact in enumerate(facts, 1)
            ]
        else:
            self.entries = [self._entry_from_mapping(row) for row in saved]
        self.revision = 0

    @staticmethod
    def _entry_from_mapping(row: Dict[str, object]) -> KnowledgeEntry:
        question = str(row.get("question", "")).strip()
        answer = str(row.get("answer", "")).strip()
        if not question or not answer:
            raise ValueError("Knowledge entries require a question and answer")
        return KnowledgeEntry(
            id=str(row.get("id") or ""),
            category=str(row.get("category") or "general"),
            question=question,
            answer=answer,
            tags=[str(tag) for tag in row.get("tags", [])],
        )

    def _save(self) -> None:
        save_json(self.store_path, [asdict(entry) for entry in self.entries])
        self.revision += 1

    def _find_duplicate(self, question: str, exclude_id: Optional[str] = None) -> Optional[KnowledgeEntry]:
        normalized = _normalized(question)
        return next(
            (entry for entry in self.entries
             if entry.id != exclude_id and _normalized(entry.question) == normalized),
            None,
        )

    def add(self, question: str, answer: str, category: str = "general",
            tags: Optional[Sequence[str]] = None) -> KnowledgeEntry:
        """Add an entry, rejecting duplicate or conflicting questions."""
        question, answer = question.strip(), answer.strip()
        if not question or not answer:
            raise ValueError("Question and answer must not be empty")
        if self._find_duplicate(question):
            raise ValueError("A knowledge entry already exists for that question")
        entry = KnowledgeEntry(
            id=f"knowledge_{len(self.entries) + 1:04d}",
            category=category.strip() or "general",
            question=question,
            answer=answer,
            tags=[tag.strip() for tag in (tags or []) if tag.strip()],
        )
        self.entries.append(entry)
        self._save()
        return entry

    def update(self, entry_id: str, question: Optional[str] = None,
               answer: Optional[str] = None, category: Optional[str] = None,
               tags: Optional[Sequence[str]] = None) -> KnowledgeEntry:
        """Edit fields on an existing entry and persist the change."""
        entry = self.get(entry_id)
        next_question = question.strip() if question is not None else entry.question
        next_answer = answer.strip() if answer is not None else entry.answer
        if not next_question or not next_answer:
            raise ValueError("Question and answer must not be empty")
        if self._find_duplicate(next_question, exclude_id=entry_id):
            raise ValueError("A knowledge entry already exists for that question")
        entry.question, entry.answer = next_question, next_answer
        if category is not None:
            entry.category = category.strip() or "general"
        if tags is not None:
            entry.tags = [tag.strip() for tag in tags if tag.strip()]
        self._save()
        return entry

    def get(self, entry_id: str) -> KnowledgeEntry:
        """Return an entry by ID or raise a clear error."""
        for entry in self.entries:
            if entry.id == entry_id:
                return entry
        raise KeyError(f"No knowledge entry found with ID {entry_id!r}")

    def delete(self, entry_id: str) -> None:
        """Delete an entry by ID and persist the change."""
        self.get(entry_id)
        self.entries = [entry for entry in self.entries if entry.id != entry_id]
        self._save()

    def search(self, query: str) -> List[KnowledgeEntry]:
        """Find entries containing query terms in their fields."""
        terms = _normalized(query).split()
        if not terms:
            return list(self.entries)
        return [
            entry for entry in self.entries
            if all(term in _normalized(" ".join(
                [entry.question, entry.answer, entry.category] + entry.tags
            )) for term in terms)
        ]

    def duplicate_questions(self) -> List[List[KnowledgeEntry]]:
        """Return groups with matching normalized questions."""
        groups: Dict[str, List[KnowledgeEntry]] = {}
        for entry in self.entries:
            groups.setdefault(_normalized(entry.question), []).append(entry)
        return [group for group in groups.values() if len(group) > 1]

    def import_file(self, path: Path) -> int:
        """Import supported TXT, JSON, or CSV entries and persist them."""
        path = Path(path)
        suffix = path.suffix.lower()
        if suffix == ".txt":
            with path.open(encoding="utf-8") as source:
                rows = [{"question": line.strip(), "answer": line.strip()}
                        for line in source if line.strip()]
        elif suffix == ".json":
            with path.open(encoding="utf-8") as source:
                loaded = json.load(source)
            rows = loaded.get("entries", []) if isinstance(loaded, dict) else loaded
        elif suffix == ".csv":
            with path.open(encoding="utf-8", newline="") as source:
                rows = list(csv.DictReader(source))
        else:
            raise ValueError("Supported knowledge imports are .txt, .json, and .csv")
        if not isinstance(rows, list):
            raise ValueError("Import data must contain a list of knowledge entries")

        added = 0
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError("Each imported entry must be an object")
            entry = self._entry_from_mapping({**row, "id": ""})
            existing = self._find_duplicate(entry.question)
            if existing:
                if existing.answer != entry.answer:
                    raise ValueError(f"Conflicting answers for question: {entry.question}")
                continue
            entry.id = f"knowledge_{len(self.entries) + 1:04d}"
            self.entries.append(entry)
            added += 1
        if added:
            self._save()
        return added

    def export(self, path: Path) -> None:
        """Export the current knowledge base as portable JSON."""
        save_json(Path(path), [asdict(entry) for entry in self.entries])
