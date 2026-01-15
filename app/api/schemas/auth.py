"""Auth schemas."""
from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Register request payload."""
    username: str = Field(min_length=3, max_length=60)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    """Login request payload."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    """Token response payload."""
    access_token: str
    token_type: str = "bearer"


class ForgotPasswordRequest(BaseModel):
    """Forgot password request payload."""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password request payload."""
    token: str
    new_password: str = Field(min_length=8, max_length=128)
