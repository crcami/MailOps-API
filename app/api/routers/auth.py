"""Authentication routes."""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_reset_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.models import User
from app.services.mailer import send_password_reset_email

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> dict:
    """Register a new user."""
    existing = (
        db.query(User)
        .filter((User.email == payload.email) | (User.username == payload.username))
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Usuário já existe.")

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"id": user.id, "username": user.username, "email": user.email}


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Authenticate user and return an access token."""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Username ou senha inválidos.")

    token = create_access_token(user_id=user.id)
    return TokenResponse(access_token=token)


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)) -> dict:
    """Send a password reset link if user exists."""
    user = db.query(User).filter(User.email == payload.email).first()

    # Always respond with success to avoid email enumeration.
    if not user:
        return {"message": "Se o e-mail existir, um link para redefinição de senha será enviado."}

    token = create_reset_token(user.id, user.email, user.password_hash)
    reset_url = f"{settings.frontend_base_url}/reset-password?token={token}"

    send_password_reset_email(
        to_email=user.email,
        username=user.username,
        reset_url=reset_url,
    )

    return {"message": "Se o e-mail existir, um link para redefinição de senha será enviado.."}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)) -> dict:
    """Reset user password using a valid token."""
    try:
        data = decode_token(payload.token)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado.") from exc

    if data.get("type") != "reset":
        raise HTTPException(status_code=400, detail="Tipo de token inválido.")

    user_id = int(data["sub"])
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="Token de usuário inválido.")

    if data.get("email") != user.email:
        raise HTTPException(status_code=400, detail="Email do token inválido.")

    # Token becomes invalid after password change due to "pwd" claim mismatch.
    if data.get("pwd") != user.password_hash:
        raise HTTPException(status_code=400, detail="O token não é mais válido.")

    user.password_hash = hash_password(payload.new_password)
    db.add(user)
    db.commit()

    return {"message": "Senha atualizada com sucesso."}
