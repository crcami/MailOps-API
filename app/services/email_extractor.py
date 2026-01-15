"""Email text extraction from input."""
from __future__ import annotations

import io

from fastapi import UploadFile
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
    reader = PdfReader(io.BytesIO(content))
    parts: list[str] = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts)
