"""FastAPI application entrypoint."""
from __future__ import annotations

import logging

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.deps import require_api_key
from app.api.routers.analyze import router as analyze_router
from app.api.routers.auth import router as auth_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.base import init_db
from app.services.ai.factory import build_ai_client

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create the FastAPI application."""
    configure_logging()
    init_db()

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description=(
            "## Autenticação\n"
            "Esta API usa duas camadas de autenticação:\n\n"
            "1) **Client API Key** (`X-API-Key`) — obrigatória em todas as rotas.\n"
            "2) **User Access Token (JWT)** (`Authorization: Bearer <token>`) — obrigatória em rotas protegidas "
            "(e.g. `/api/analyze`).\n\n"
            "### Fluxo de uso\n"
            "1. Clique em **Authorize** e defina a `X-API-Key`.\n"
            "2. Registre-se ou faça login via `/api/auth/login`.\n"
            "3. Clique em **Authorize** novamente e cole o JWT no campo Bearer.\n"
            "4. Teste as rotas protegidas.\n"
        ),
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api_cors_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def _warmup_ai_client() -> None:
        """Warm up the AI client to emit startup logs."""
        try:
            build_ai_client()
            logger.info("AI client warmup completed.")
        except Exception:
            logger.exception("AI client warmup failed.")

    @app.get("/", include_in_schema=False)
    def root() -> dict:
        """Return a simple root response."""
        return {"status": "ok", "docs": "/docs", "health": "/api/health"}

    @app.get("/api/health")
    def health() -> dict:
        """Return a simple health check."""
        return {"status": "ok"}

    app.include_router(
        auth_router,
        prefix="/api/auth",
        tags=["auth"],
        dependencies=[Depends(require_api_key)],
    )
    app.include_router(
        analyze_router,
        prefix="/api",
        tags=["analyze"],
        dependencies=[Depends(require_api_key)],
    )

    return app


app = create_app()
