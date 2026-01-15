"""Email text extraction from input."""
from __future__ import annotations

import io

from fastapi import HTTPException, UploadFile
from pypdf import PdfReader


async def extract_email_text(file: UploadFile | None, email_text: str) -> str:
    """Extract email text from upload or raw input."""
    if email_text and email_text.strip():
        return email_text.strip()

    if not file:
        return ""

    filename = (file.filename or "").lower()
    content = await file.read()

    if filename.endswith(".txt"):
        return content.decode("utf-8", errors="ignore").strip()

    if filename.endswith(".pdf"):
        return _extract_pdf_text(content).strip()

    return ""


def _extract_pdf_text(content: bytes) -> str:
    """Extract PDF text using pypdf."""
    try:
        reader = PdfReader(io.BytesIO(content))
        parts: list[str] = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")
        return "\n".join(parts)
    except Exception as e:
        # Captura erros específicos de PDF
        error_msg = str(e).lower()
        if "password" in error_msg or "encrypted" in error_msg:
            raise HTTPException(
                status_code=400,
                detail="PDF protegido por senha. Por favor, envie um arquivo sem proteção."
            )
        elif "invalid" in error_msg or "corrupt" in error_msg:
            raise HTTPException(
                status_code=400,
                detail="Arquivo PDF inválido ou corrompido. Verifique o arquivo e tente novamente."
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Erro ao processar PDF: {str(e)}"
            )

