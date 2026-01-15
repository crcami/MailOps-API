"""Authentication routes."""
from __future__ import annotations

import logging
from hashlib import sha256

from fastapi import APIRouter, Depends, HTTPException, status
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
    decode_reset_token,
    hash_password,
    verify_password,
)
from app.db.models import User
from app.services.mailer import send_password_reset_email

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Register a new user and return a bearer token."""
    existing = (
        db.query(User)
        .filter((User.email == payload.email) | (User.username == payload.username))
        .first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Usuário já existe.")

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user_id=user.id)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Authenticate user and return an access token."""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário ou senha inválidos.")

    token = create_access_token(user_id=user.id)
    return TokenResponse(access_token=token)


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
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

    return {"message": "Se o e-mail existir, um link para redefinição de senha será enviado."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)) -> dict:
    """Reset user password using a valid token."""
    try:
        data = decode_reset_token(payload.token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido ou expirado.",
        ) from exc

    user_id = int(data["sub"])
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token de usuário inválido.")

    if data.get("email") != user.email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email do token inválido.")

    expected_fp = sha256(user.password_hash.encode("utf-8")).hexdigest()
    if data.get("pwd_fp") != expected_fp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="O token não é mais válido.")

    user.password_hash = hash_password(payload.new_password)
    db.add(user)
    db.commit()

    return {"message": "Senha atualizada com sucesso."}
