"""Reply templates based on intent."""
from __future__ import annotations

from app.core.config import settings


def build_reply(intent: str, category: str, secondary_intents: tuple[str, ...] = ()) -> tuple[str, str, str | None]:
    """Build a subject and reply for a given intent."""
    company = settings.company_name
    secondary = set(secondary_intents or ())

    if intent == "PRAISE":
        subject = "Re: Obrigado pela sua mensagem"
        body = (
            "Olá,\n\n"
            "Muito obrigado pelo elogio. Ficamos felizes em saber da sua experiência.\n\n"
            f"Atenciosamente,\n{company}\n"
        )
        return subject, body, None

    if intent == "RESUME":
        subject = "Re: Recebemos seu currículo"
        body = (
            "Olá,\n\n"
            "Obrigado por seu interesse em fazer parte da nossa empresa.\n"
            "Para encaminhar seu currículo corretamente, por favor envie para:\n\n"
            f"{settings.hr_email}\n\n"
            "Nossa equipe de RH fará a triagem e retornará caso seu perfil seja selecionado.\n\n"
            f"Atenciosamente,\n{company}\n"
        )
        return subject, body, settings.hr_email

    if intent == "COMPLAINT":
        subject = "Re: Sentimos muito pelo ocorrido"

        prefix = ""
        if "PRAISE" in secondary:
            prefix = (
                "Olá,\n\n"
                "Obrigado pelo seu feedback e por compartilhar sua experiência.\n"
            )
        else:
            prefix = "Olá,\n\n"

        body = (
            f"{prefix}\n"
            "Sentimos muito pela sua experiência.\n"
            "Para que possamos registrar e tratar sua solicitação com prioridade, "
            "por favor envie os detalhes (ex.: prints, data/hora, passos) para:\n\n"
            f"{settings.sac_email}\n\n"
            "Vamos analisar o caso e retornar o mais breve possível.\n\n"
            f"Atenciosamente,\n{company}\n"
        )
        return subject, body, settings.sac_email

    if intent == "SUPPORT":
        subject = "Re: Solicitação recebida"
        body = (
            "Olá,\n\n"
            "Recebemos sua solicitação e vamos verificar.\n"
            "Para agilizar, envie por favor:\n"
            "- Passo a passo do que ocorreu\n"
            "- Data e horário aproximado\n"
            "- Prints ou mensagens de erro\n\n"
            f"Atenciosamente,\n{company}\n"
        )
        return subject, body, None

    if category == "Produtivo":
        subject = "Re: Solicitação recebida"
        body = (
            "Olá,\n\n"
            "Recebemos sua solicitação e vamos analisar. "
            "Se possível, envie mais detalhes para agilizar o atendimento.\n\n"
            f"Atenciosamente,\n{company}\n"
        )
        return subject, body, None

    subject = "Re: Obrigado pelo contato"
    body = (
        "Olá,\n\n"
        "Obrigado pela mensagem. Ficamos à disposição.\n\n"
        f"Atenciosamente,\n{company}\n"
    )
    return subject, body, None
