"""Analyze routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.api.deps import get_current_user
from app.api.schemas.analyze import AnalyzeResponse
from app.db.models import User
from app.services.classifier import classify_and_reply
from app.services.email_extractor import extract_email_text
from app.services.nlp import preprocess_text

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_email(
    email_text: str = Form(default=""),
    file: UploadFile | None = File(default=None),
    _: User = Depends(get_current_user),
) -> AnalyzeResponse:
    """Analyze an email and suggest a reply."""
    raw = await extract_email_text(file=file, email_text=email_text)
    if not raw.strip():
        raise HTTPException(status_code=400, detail="Conteúdo do email vazio.")

    preprocessed = preprocess_text(raw)
    result = await classify_and_reply(raw_text=raw, preprocessed_text=preprocessed)

    return AnalyzeResponse(**result)
