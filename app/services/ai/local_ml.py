"""Local ML AI client based on scikit-learn."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib

from app.services.ai.base import AIClient, ClassificationResult, ReplyResult


@dataclass(frozen=True)
class _ModelBundle:
    """Model bundle container."""
    pipeline: object


class LocalMLAIClient(AIClient):
    """Local ML classifier client."""
    def __init__(self, model_path: str = "models/email_classifier.joblib") -> None:
        """Initialize local model client."""
        self._model_path = Path(model_path)
        self._bundle = self._load_model()

    async def classify(self, text: str) -> ClassificationResult:
        """Classify an email."""
        if not self._bundle:
            productive = _fallback_heuristic(text)
            return ClassificationResult(
                category="Produtivo" if productive else "Improdutivo",
                confidence=0.65,
                justification="Fallback heuristic (model not found).",
                provider="local_ml",
            )

        proba = _predict_proba(self._bundle.pipeline, text)
        productive_conf = float(proba[1])
        category = "Produtivo" if productive_conf >= 0.5 else "Improdutivo"
        confidence = productive_conf if category == "Produtivo" else (1 - productive_conf)

        return ClassificationResult(
            category=category,
            confidence=max(0.0, min(1.0, confidence)),
            justification="Local ML model (TF-IDF + LogisticRegression).",
            provider="local_ml",
        )

    async def draft_reply(self, text: str, category: str) -> ReplyResult:
        """Draft a reply for an email."""
        if category == "Produtivo":
            subject = "Re: Solicitação recebida"
            body = (
                "Olá,\n\n"
                "Recebemos sua solicitação e vamos verificar. "
                "Você poderia enviar mais detalhes (ex.: horário, passos, prints)?\n\n"
                "Atenciosamente,\n"
                "Equipe MailOps AI\n"
            )
        else:
            subject = "Re: Obrigado pelo contato"
            body = (
                "Olá,\n\n"
                "Obrigado pela mensagem. Ficamos à disposição.\n\n"
                "Atenciosamente,\n"
                "Equipe MailOps AI\n"
            )

        return ReplyResult(subject=subject, body=body, provider="local_ml")

    def _load_model(self) -> _ModelBundle | None:
        """Load the persisted ML pipeline."""
        if not self._model_path.exists():
            return None
        pipeline = joblib.load(self._model_path)
        return _ModelBundle(pipeline=pipeline)


def _predict_proba(pipeline: object, text: str) -> list[float]:
    """Predict probabilities for input text."""
    predict_proba = getattr(pipeline, "predict_proba", None)
    if not callable(predict_proba):
        return [0.5, 0.5]
    proba = predict_proba([text])[0]
    return [float(proba[0]), float(proba[1])]


def _fallback_heuristic(text: str) -> bool:
    """Fallback heuristic classifier."""
    value = (text or "").lower()
    keywords = [
        "erro", "bug", "falha", "suporte", "urgente", "prazo", "chamado",
        "ticket", "dúvida", "duvida", "problema", "não consigo", "nao consigo",
        "atualização", "status", "pendente",
    ]
    return any(k in value for k in keywords)
