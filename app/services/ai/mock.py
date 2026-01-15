"""Mock AI client."""
from __future__ import annotations

from app.services.ai.base import AIClient, ClassificationResult, ReplyResult


class MockAIClient(AIClient):
    """Mock AI client for local development."""
    async def classify(self, text: str) -> ClassificationResult:
        """Classify an email."""
        productive = _guess_productive(text)
        return ClassificationResult(
            category="Produtivo" if productive else "Improdutivo",
            confidence=0.82 if productive else 0.74,
            justification="Keyword-based mock classification.",
            provider="mock",
        )

    async def draft_reply(self, text: str, category: str) -> ReplyResult:
        """Draft a reply for an email."""
        if category == "Produtivo":
            body = (
                "Olá,\n\n"
                "Recebemos sua solicitação e vamos verificar o ocorrido. "
                "Você poderia informar mais detalhes (ex.: prints, horário, passos)?\n\n"
                "Atenciosamente,\n"
                "Equipe MailOps AI\n"
            )
        else:
            body = (
                "Olá,\n\n"
                "Muito obrigado pela mensagem.\n\n"
                "Atenciosamente,\n"
                "Equipe MailOps AI\n"
            )

        return ReplyResult(subject="Re: Sua mensagem", body=body, provider="mock")


def _guess_productive(text: str) -> bool:
    """Guess productivity using simple heuristics."""
    value = (text or "").lower()
    keywords = [
        "erro", "bug", "falha", "suporte", "urgente", "prazo", "chamado",
        "ticket", "dúvida", "duvida", "problema", "não consigo", "nao consigo",
        "atualização", "status", "pendente",
    ]
    return any(k in value for k in keywords)
