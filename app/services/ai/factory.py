"""AI client factory."""
from __future__ import annotations

from app.core.config import settings
from app.services.ai.base import AIClient
from app.services.ai.local_ml import LocalMLAIClient
from app.services.ai.mock import MockAIClient


def build_ai_client() -> AIClient:
    """Build an AI client from settings."""
    provider = (settings.ai_provider or "local_ml").lower().strip()

    if provider in {"local_ml", "sklearn"}:
        return LocalMLAIClient()

    return MockAIClient()
