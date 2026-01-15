"""FastAPI application entrypoint."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.analyze import router as analyze_router
from app.api.routers.auth import router as auth_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.base import init_db


def create_app() -> FastAPI:
    """Create the FastAPI application."""
    configure_logging()
    init_db()

    app = FastAPI(title=settings.app_name)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api_cors_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    def health() -> dict:
        """Return a simple health check."""
        return {"status": "ok"}

    app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
    app.include_router(analyze_router, prefix="/api", tags=["analyze"])

    return app


app = create_app()
