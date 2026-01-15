"""Local ML AI client based on scikit-learn."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import joblib

from app.services.ai.base import AIClient, ClassificationResult, ReplyResult

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class _ModelBundle:
    """Model bundle container."""
    pipeline: object
    path: Path


class LocalMLAIClient(AIClient):
    """Local ML classifier client."""

    def __init__(self, model_path: str | None = None) -> None:
        """Initialize local model client."""
        base_dir = Path(__file__).resolve().parents[3]
        default_path = base_dir / "models" / "productivity_classifier.joblib"
        self._model_path = Path(model_path) if model_path else default_path

        logger.info(
            "Initializing LocalMLAIClient | model_path=%s | exists=%s",
            str(self._model_path),
            self._model_path.exists(),
        )

        self._bundle = self._load_model()

        if self._bundle is None:
            logger.warning(
                "Local ML model NOT loaded | model_path=%s",
                str(self._model_path),
            )
        else:
            logger.info(
                "Local ML model loaded successfully | model_path=%s",
                str(self._bundle.path),
            )

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
            justification=f"Local ML model loaded from: {self._bundle.path.name}",
            provider="local_ml",
        )

    async def draft_reply(self, text: str, category: str) -> ReplyResult:
        """Draft a reply for an email."""
        if category == "Produtivo":
            subject = "Re: Request received"
            body = (
                "Hello,\n\n"
                "We received your request and will review it. "
                "Could you share more details (e.g., date/time, steps, screenshots)?\n\n"
                "Sincerely,\n"
                "MailOps AI Team\n"
            )
        else:
            subject = "Re: Thanks for reaching out"
            body = (
                "Hello,\n\n"
                "Thank you for your message. We remain available.\n\n"
                "Sincerely,\n"
                "MailOps AI Team\n"
            )

        return ReplyResult(subject=subject, body=body, provider="local_ml")

    def _load_model(self) -> _ModelBundle | None:
        """Load the persisted ML pipeline."""
        if not self._model_path.exists():
            logger.warning("ML model file not found | model_path=%s", str(self._model_path))
            return None

        try:
            pipeline = joblib.load(self._model_path)
        except Exception:
            logger.exception("Failed to load ML model | model_path=%s", str(self._model_path))
            return None

        logger.info("Loaded ML model from disk | model_path=%s", str(self._model_path))
        return _ModelBundle(pipeline=pipeline, path=self._model_path)


def _predict_proba(pipeline: object, text: str) -> list[float]:
    """Predict probabilities for input text."""
    predict_proba = getattr(pipeline, "predict_proba", None)
    if not callable(predict_proba):
        logger.warning("Pipeline does not implement predict_proba; returning uniform probabilities.")
        return [0.5, 0.5]
    proba = predict_proba([text])[0]
    return [float(proba[0]), float(proba[1])]


def _fallback_heuristic(text: str) -> bool:
    """Fallback heuristic classifier."""
    value = (text or "").lower()
    keywords = [
        "erro",
        "bug",
        "falha",
        "suporte",
        "urgente",
        "prazo",
        "chamado",
        "ticket",
        "dúvida",
        "duvida",
        "problema",
        "não consigo",
        "nao consigo",
        "atualização",
        "status",
        "pendente",
    ]
    return any(k in value for k in keywords)
