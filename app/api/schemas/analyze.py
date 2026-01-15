"""Analyze schemas."""
from __future__ import annotations

from pydantic import BaseModel, Field


class AnalyzeResponse(BaseModel):
    """Analyze response payload."""
    category: str = Field(examples=["Produtivo", "Improdutivo"])
    intent: str = Field(examples=["SUPPORT", "PRAISE", "RESUME", "COMPLAINT", "OTHER"])
    confidence: float = Field(ge=0.0, le=1.0)

    suggested_subject: str
    suggested_reply: str

    short_justification: str
    provider: str

    recommended_contact: str | None = None
