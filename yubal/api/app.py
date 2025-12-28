import shutil
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from yubal.api.exceptions import register_exception_handlers
from yubal.api.routes import cookies, health, jobs
from yubal.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup/shutdown."""
    # Startup: initialize resources
    yield
    # Shutdown: cleanup temp directory
    temp_dir = get_settings().temp_dir
    if temp_dir.exists():
        logger.info("Cleaning up temp directory: {}", temp_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)


def create_api() -> FastAPI:
    """Create the API sub-application."""
    api = FastAPI(
        title="yubal API",
        description="YouTube Album Downloader API",
        version="0.1.0",
    )

    # Register exception handlers
    register_exception_handlers(api)

    # API routes
    api.include_router(health.router)
    api.include_router(jobs.router, tags=["jobs"])
    api.include_router(cookies.router)

    return api


def create_app() -> FastAPI:
    """Create and configure the main FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="yubal",
        lifespan=lifespan,
        debug=settings.debug,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,  # type: ignore[arg-type]
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount API sub-app at /api
    app.mount("/api", create_api())

    # Static files
    web_build = Path(__file__).parent.parent.parent / "web" / "dist"
    if web_build.exists():
        app.mount("/", StaticFiles(directory=web_build, html=True), name="static")

    return app


# Create app instance for uvicorn
app = create_app()
