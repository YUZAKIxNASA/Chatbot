"""Knowledge-base loading."""

from pathlib import Path
from typing import List

from .nlp import split_sentences


def load_knowledge(path: Path) -> List[str]:
    """Load knowledge facts from a UTF-8 text file."""
    with path.open(encoding="utf-8") as knowledge_file:
        return split_sentences(knowledge_file.read())
