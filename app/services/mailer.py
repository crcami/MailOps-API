"""Email sending service."""
from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_password_reset_email(to_email: str, username: str, reset_url: str) -> None:
    """Send a password reset email."""
    subject = "MailOps AI - Recuperação de senha"
    body = (
        f"Olá {username},\n\n"
        "Recebemos uma solicitação para redefinir sua senha.\n"
        f"Use o link abaixo dentro de {settings.reset_token_expire_minutes} minutos:\n\n"
        f"{reset_url}\n\n"
        "Se você não solicitou isso, você pode ignorar este email.\n\n"
        "Atenciosamente,\n"
        "MailOps AI\n"
    )

    # If SMTP is not configured, log the email body (useful for dev).
    if not settings.smtp_host:
        logger.info("SMTP não configurado, imprimindo email de recuperação de senha:\n%s", body)
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        if settings.smtp_username:
            server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(msg)
