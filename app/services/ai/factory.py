"""AI client factory."""
from __future__ import annotations

from functools import lru_cache

from app.core.config import settings
from app.services.ai.base import AIClient
from app.services.ai.local_ml import LocalMLAIClient
from app.services.ai.mock import MockAIClient


@lru_cache(maxsize=1)
def build_ai_client() -> AIClient:
    """Build and cache an AI client from settings."""
    provider = (settings.ai_provider or "local_ml").lower().strip()

    if provider in {"mock"}:
        return MockAIClient()

    if provider in {"local_ml", "sklearn"}:
        return LocalMLAIClient()

    return LocalMLAIClient()
