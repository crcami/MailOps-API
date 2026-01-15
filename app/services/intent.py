"""Intent detection for emails."""
from __future__ import annotations

import re


def detect_intent(text: str) -> str:
    """Detect an email intent label."""
    value = _normalize(text)

    if _matches(value, _PRAISE_PATTERNS):
        return "PRAISE"

    if _matches(value, _RESUME_PATTERNS):
        return "RESUME"

    if _matches(value, _COMPLAINT_PATTERNS):
        return "COMPLAINT"

    if _matches(value, _SUPPORT_PATTERNS):
        return "SUPPORT"

    return "OTHER"


def normalize_category(category: str, intent: str) -> str:
    """Normalize productive category using intent overrides."""
    if intent in {"SUPPORT", "COMPLAINT", "RESUME"}:
        return "Produtivo"

    if intent in {"PRAISE"}:
        return "Improdutivo"

    return category


def _normalize(text: str) -> str:
    """Normalize text for pattern matching."""
    value = (text or "").lower()
    value = value.replace("\n", " ")
    value = re.sub(r"\s+", " ", value).strip()
    return value


def _matches(value: str, patterns: list[str]) -> bool:
    """Check if any regex pattern matches."""
    return any(re.search(p, value) for p in patterns)


_PRAISE_PATTERNS = [
    r"\belogio\b",
    r"\bparab[eé]ns\b",
    r"\bótimo\b",
    r"\bexcelente\b",
    r"\bmuito bom\b",
    r"\bagrade[cç]o\b",
    r"\bobrigad[oa]\b",
]

_RESUME_PATTERNS = [
    r"\bcurr[ií]culo\b",
    r"\bcv\b",
    r"\bvaga\b",
    r"\btrabalhe conosco\b",
    r"\bprocesso seletivo\b",
    r"\bentrevista\b",
    r"\brecrutamento\b",
]

_COMPLAINT_PATTERNS = [
    r"\breclama[cç][aã]o\b",
    r"\bdecepcionad[oa]\b",
    r"\binsatisfeit[oa]\b",
    r"\bp[eé]ssimo\b",
    r"\bproblema\b",
    r"\bquero cancelar\b",
    r"\bquero reembolso\b",
]

_SUPPORT_PATTERNS = [
    r"\bsuporte\b",
    r"\berro\b",
    r"\bbug\b",
    r"\bfalha\b",
    r"\bn[aã]o consigo\b",
    r"\bd[uú]vida\b",
    r"\bajuda\b",
    r"\bchamado\b",
    r"\bticket\b",
    r"\bstatus\b",
]
