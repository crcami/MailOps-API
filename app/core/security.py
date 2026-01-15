"""Security helpers (password hashing and JWT tokens)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Any

import jwt
from jwt import PyJWTError
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
        "pwd_fp": _password_fingerprint(password_hash),
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate an access token."""
    payload = _decode_token(token)
    if payload.get("type") != "access":
        raise ValueError("Invalid token type.")
    return payload


def decode_reset_token(token: str) -> dict[str, Any]:
    """Decode and validate a reset token."""
    payload = _decode_token(token)
    if payload.get("type") != "reset":
        raise ValueError("Invalid token type.")
    if "email" not in payload or "pwd_fp" not in payload:
        raise ValueError("Invalid reset token payload.")
    return payload


def _decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT token."""
    try:
        return jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["exp", "iat", "sub"]},
        )
    except PyJWTError as exc:
        raise ValueError("Invalid token.") from exc


def _password_fingerprint(password_hash: str) -> str:
    """Build a stable fingerprint for password invalidation."""
    return sha256(password_hash.encode("utf-8")).hexdigest()
