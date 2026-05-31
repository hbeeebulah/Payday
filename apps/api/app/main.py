"""FastAPI application entrypoint for the Payday backend."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.core.config import get_settings
from app.routes import api_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Place startup/shutdown hooks here (warm pools, health checks, etc.).
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.project_name,
        version=__version__,
        description=(
            "Payday backend — orchestrates simultaneous salary disbursement "
            "for small businesses via ALATPay."
        ),
        lifespan=lifespan,
    )

    if settings.backend_cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.backend_cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.include_router(api_router, prefix=settings.api_prefix)

    @app.get("/")
    async def root() -> dict[str, str]:
        return {"service": settings.project_name, "version": __version__}

    return app


app = create_app()
