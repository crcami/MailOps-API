"""NLP preprocessing utilities."""
from __future__ import annotations

import re

from nltk.stem.snowball import SnowballStemmer

_PT_STOPWORDS = {
    "a", "o", "os", "as", "de", "da", "do", "das", "dos", "e", "em", "um",
    "uma", "para", "por", "com", "sem", "no", "na", "nos", "nas", "que",
    "se", "ao", "aos", "à", "às", "eu", "voce", "você", "vocês", "me",
    "minha", "meu", "sua", "seu", "obrigado", "obrigada",
}


def preprocess_text(text: str, language: str = "portuguese") -> str:
    """Preprocess text with stopwords and stemming."""
    normalized = _normalize(text)
    tokens = [t for t in normalized.split() if t and t not in _PT_STOPWORDS]

    stemmer = SnowballStemmer(language)
    stemmed = [stemmer.stem(t) for t in tokens]

    return " ".join(stemmed)


def _normalize(text: str) -> str:
    """Normalize text for tokenization."""
    value = (text or "").lower()
    value = re.sub(r"[^\w\s]", " ", value, flags=re.UNICODE)
    value = re.sub(r"\s+", " ", value).strip()
    return value
