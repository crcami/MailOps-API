"""Auth schemas."""
from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.password_policy import validate_password_strength


class RegisterRequest(BaseModel):
    """Register request payload."""
    username: str = Field(min_length=3, max_length=60)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def _validate_password(cls, value: str) -> str:
        """Validate password policy."""
        validate_password_strength(value)
        return value


class LoginRequest(BaseModel):
    """Login request payload."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class TokenResponse(BaseModel):
    """Token response payload."""
    access_token: str
    token_type: str = "bearer"


class ForgotPasswordRequest(BaseModel):
    """Forgot password request payload."""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password request payload."""
    token: str = Field(min_length=10, max_length=4096)
    new_password: str = Field(min_length=8, max_length=72)

    @field_validator("new_password")
    @classmethod
    def _validate_new_password(cls, value: str) -> str:
        """Validate password policy."""
        validate_password_strength(value)
        return value


class UserMeResponse(BaseModel):
    """Current user response payload."""
    id: int
    username: str
    email: EmailStr