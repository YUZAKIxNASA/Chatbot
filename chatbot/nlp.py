"""Small, resource-safe NLP helpers used by the chatbot."""

import re
import string
from typing import List

import nltk
from nltk.stem import WordNetLemmatizer


_lemmatizer = WordNetLemmatizer()
_punctuation_table = str.maketrans("", "", string.punctuation)


def normalize_text(text: str) -> str:
    """Lowercase text and remove punctuation without changing its words."""
    return " ".join(text.lower().translate(_punctuation_table).split())


def tokenize(text: str) -> List[str]:
    """Tokenize with NLTK when available, with a local fallback."""
    normalized = normalize_text(text)
    if not normalized:
        return []
    try:
        return nltk.word_tokenize(normalized)
    except LookupError:
        return re.findall(r"[a-z0-9]+", normalized)


def lemmatize_tokens(tokens: List[str]) -> List[str]:
    """Lemmatize tokens when WordNet data is installed."""
    try:
        return [_lemmatizer.lemmatize(token) for token in tokens]
    except LookupError:
        return tokens


def preprocess(text: str) -> List[str]:
    """Return normalized, tokenized and lemmatized text for vectorization."""
    return lemmatize_tokens(tokenize(text))


def split_sentences(text: str) -> List[str]:
    """Split knowledge text into non-empty sentences or lines safely."""
    try:
        sentences = nltk.sent_tokenize(text)
    except LookupError:
        sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [sentence.strip() for sentence in sentences if sentence.strip()]
