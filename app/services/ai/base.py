"""AI client interfaces."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ClassificationResult:
    """Classification output."""
    category: str
    confidence: float
    justification: str
    provider: str


@dataclass(frozen=True)
class ReplyResult:
    """Reply generation output."""
    subject: str
    body: str
    provider: str


class AIClient:
    """AI client contract."""
    async def classify(self, text: str) -> ClassificationResult:
        """Classify an email."""
        raise NotImplementedError

    async def draft_reply(self, text: str, category: str) -> ReplyResult:
        """Draft a reply for an email."""
        raise NotImplementedError
