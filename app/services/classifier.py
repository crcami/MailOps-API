"""Email classification orchestrator."""
from __future__ import annotations

from app.services.ai.factory import build_ai_client
from app.services.intent import detect_intent, normalize_category
from app.services.replies import build_reply


async def classify_and_reply(raw_text: str, preprocessed_text: str) -> dict:
    """Classify, detect intent, and generate a reply suggestion."""
    ai = build_ai_client()

    classification = await ai.classify(raw_text)
    intent = detect_intent(raw_text)

    category = normalize_category(classification.category, intent)
    subject, reply, contact = build_reply(intent=intent, category=category)

    justification = classification.justification
    if category != classification.category:
        justification = f"{justification} Intent override applied: {intent}."

    return {
        "category": category,
        "intent": intent,
        "confidence": classification.confidence,
        "short_justification": justification,
        "suggested_subject": subject,
        "suggested_reply": reply,
        "provider": classification.provider,
        "recommended_contact": contact,
    }
