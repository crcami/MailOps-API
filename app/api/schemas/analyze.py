"""Analyze schemas."""
from __future__ import annotations

from pydantic import BaseModel, Field


class AnalyzeResponse(BaseModel):
    """Analyze response payload."""
    category: str = Field(examples=["Produtivo", "Improdutivo"])
    confidence: float = Field(ge=0.0, le=1.0)

    intent: str = Field(examples=["SUPPORT", "PRAISE", "RESUME", "COMPLAINT", "OTHER"])
    intent_confidence: float = Field(ge=0.0, le=1.0, examples=[0.62])
    intent_source: str = Field(examples=["intent_ml", "rules", "fallback"])

    suggested_subject: str
    suggested_reply: str

    short_justification: str
    provider: str

    recommended_contact: str | None = None
