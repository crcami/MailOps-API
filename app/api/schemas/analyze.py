"""Analyze schemas."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

CategoryLabel = Literal["Produtivo", "Improdutivo"]
IntentLabel = Literal["PRAISE", "RESUME", "COMPLAINT", "SUPPORT", "OTHER"]
IntentSource = Literal["rules", "local_ml"]


class AnalyzeResponse(BaseModel):
    """Analyze response payload."""
    category: CategoryLabel = Field(
        description="Classificação de produtividade: Produtivo ou Improdutivo."
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confiança da classificação de produtividade.",
    )
    intent: IntentLabel = Field(
        description="Intent primário: PRAISE, RESUME, COMPLAINT, SUPPORT ou OTHER."
    )
    intent_confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confiança do intent primário.",
    )
    intent_source: IntentSource = Field(
        description="Origem do intent: rules ou local_ml."
    )
    secondary_intents: list[IntentLabel] = Field(
        default_factory=list,
        description="Intents secundários detectados quando o texto é misto.",
    )
    intent_reason: str = Field(
        default="",
        description="Explicação resumida de como o intent final foi escolhido.",
    )
    suggested_subject: str = Field(description="Assunto sugerido.")
    suggested_reply: str = Field(description="Resposta sugerida.")
    short_justification: str = Field(description="Justificativa curta do classificador.")
    provider: str = Field(description="Provedor do classificador (ex.: local_ml).")
    recommended_contact: str | None = Field(
        default=None,
        description="Contato recomendado (ex.: SAC ou RH), quando aplicável.",
    )
