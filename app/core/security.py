"""Security helpers (password hashing and JWT tokens)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from app.core.config import settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password."""
    return _pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    return _pwd_context.verify(password, password_hash)


def create_access_token(user_id: int) -> str:
    """Create a JWT access token."""
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=settings.access_token_expire_minutes)

    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_reset_token(user_id: int, email: str, password_hash: str) -> str:
    """Create a password reset token."""
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=settings.reset_token_expire_minutes)

    payload = {
        "sub": str(user_id),
        "type": "reset",
        "email": email,
        "pwd": password_hash,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token."""
    return jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.jwt_algorithm],
        options={"require": ["exp", "iat", "sub"]},
    )
