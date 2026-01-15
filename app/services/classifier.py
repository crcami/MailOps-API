"""Email classification orchestrator."""
from __future__ import annotations

from app.services.ai.factory import build_ai_client
from app.services.intent import detect_intent, normalize_category
from app.services.replies import build_reply

_ALLOWED_INTENTS = {"PRAISE", "RESUME", "COMPLAINT", "SUPPORT", "OTHER"}


async def classify_and_reply(raw_text: str, preprocessed_text: str) -> dict:
    """Classify email and build a suggested reply."""
    ai = build_ai_client()

    text_for_productivity = (preprocessed_text or "").strip() or raw_text
    classification = await ai.classify(text_for_productivity)

    intent_label, intent_conf, intent_source, secondary, reason = _safe_detect_intent(raw_text)

    normalized_category = normalize_category(
        category=classification.category,
        intent=intent_label,
    )

    subject, reply, contact = build_reply(
        intent=intent_label,
        category=normalized_category,
        secondary_intents=secondary,
    )

    return {
        "category": normalized_category,
        "confidence": float(classification.confidence),
        "intent": intent_label,
        "intent_confidence": float(intent_conf),
        "intent_source": intent_source,
        "secondary_intents": list(secondary),
        "intent_reason": reason or "",
        "suggested_subject": subject,
        "suggested_reply": reply,
        "short_justification": classification.justification,
        "provider": classification.provider,
        "recommended_contact": contact,
    }


def _safe_detect_intent(text: str) -> tuple[str, float, str, tuple[str, ...], str]:
    """Detect intent with compatibility across implementations."""
    try:
        pred = _call_detect_intent(text)
    except Exception:
        return "OTHER", 0.0, "fallback", (), ""

    if hasattr(pred, "label"):
        label = str(getattr(pred, "label", "OTHER")).strip().upper()
        conf = float(getattr(pred, "confidence", 0.0))
        source = str(getattr(pred, "source", "rules"))
        secondary = getattr(pred, "secondary", ()) or ()
        reason = str(getattr(pred, "reason", "") or "")
        return _normalize_intent(label), _clamp(conf), source, _normalize_secondary(secondary, label), reason

    if hasattr(pred, "intent"):
        label = str(getattr(pred, "intent", "OTHER")).strip().upper()
        conf = float(getattr(pred, "confidence", 0.0))
        source = str(getattr(pred, "source", "rules"))
        secondary = getattr(pred, "secondary", ()) or ()
        reason = str(getattr(pred, "reason", "") or "")
        return _normalize_intent(label), _clamp(conf), source, _normalize_secondary(secondary, label), reason

    return _normalize_intent(str(pred or "OTHER")), 0.50, "rules", (), ""


def _call_detect_intent(text: str):
    """Call detect_intent with optional threshold if supported."""
    try:
        return detect_intent(text, min_confidence=0.60)
    except TypeError:
        return detect_intent(text)


def _normalize_intent(value: str) -> str:
    """Normalize intent to allowed labels."""
    upper = (value or "OTHER").strip().upper()
    return upper if upper in _ALLOWED_INTENTS else "OTHER"


def _normalize_secondary(value: object, primary: str) -> tuple[str, ...]:
    """Normalize secondary intents to allowed labels."""
    if not value:
        return ()
    if isinstance(value, str):
        items = [value]
    else:
        try:
            items = list(value)  # type: ignore[arg-type]
        except Exception:
            return ()
    cleaned = []
    primary_u = (primary or "OTHER").strip().upper()
    for item in items:
        upper = str(item).strip().upper()
        if upper in _ALLOWED_INTENTS and upper != primary_u:
            cleaned.append(upper)
    return tuple(sorted(set(cleaned)))


def _clamp(value: float) -> float:
    """Clamp numeric value to 0..1."""
    return max(0.0, min(1.0, float(value)))
