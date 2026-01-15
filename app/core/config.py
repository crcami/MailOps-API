"""Application settings."""
from __future__ import annotations

import json
from typing import Literal, Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings model."""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = "dev"
    app_name: str = "MailOps AI API"
    api_cors_origins: list[str] = ["http://localhost:5173"]

    database_url: str = "sqlite:///./mailops.db"

    secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 120
    reset_token_expire_minutes: int = 15

    frontend_base_url: str = "http://localhost:5173"

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from: str = "MailOps AI <no-reply@mailops.ai>"

    company_name: str = "MailOps AI"
    hr_email: str = "rh@mailops.ai"
    sac_email: str = "sac@mailops.ai"

    ai_provider: Literal["mock", "local_ml"] = "local_ml"

    public_api_key: str = ""

    @field_validator("api_cors_origins", mode="before")
    @classmethod
    def _parse_cors_origins(cls, value: Any) -> Any:
        """Parse cors origins from env."""
        if isinstance(value, str):
            raw = value.strip()

            if raw.startswith("["):
                try:
                    parsed = json.loads(raw)
                    if isinstance(parsed, list):
                        return [str(v).strip() for v in parsed if str(v).strip()]
                except json.JSONDecodeError:
                    pass

            items = [v.strip() for v in raw.split(",")]
            return [v for v in items if v]

        return value


settings = Settings()
