"""FastAPI application factory and configuration."""

import shutil
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from yubal.api.dependencies import set_services
from yubal.api.exceptions import register_exception_handlers
from yubal.api.routes import cookies, health, jobs
from yubal.services.downloader import Downloader
from yubal.services.file_organizer import FileOrganizer
from yubal.services.job_executor import JobExecutor
from yubal.services.job_store import JobStore
from yubal.services.metadata_enricher import MetadataEnricher
from yubal.services.metadata_patcher import MetadataPatcher
from yubal.services.sync import AlbumSyncService, PlaylistSyncService
from yubal.services.tagger import Tagger
from yubal.settings import get_settings


@dataclass
class Services:
    """Container for application services with proper lifecycle management.

    All services are created at startup and cleaned up at shutdown.
    This replaces the @cache singleton pattern with explicit lifecycle.
    """

    job_store: JobStore
    job_executor: JobExecutor
    album_sync_service: AlbumSyncService
    playlist_sync_service: PlaylistSyncService
    metadata_patcher: MetadataPatcher

    def close(self) -> None:
        """Clean up resources. Called at application shutdown."""
        self.metadata_patcher.close()
        logger.info("Services cleaned up")


def create_services() -> Services:
    """Create all application services with proper dependency wiring."""
    settings = get_settings()

    # Create base services
    downloader = Downloader(
        audio_format=settings.audio_format,
        cookies_file=settings.cookies_file,
    )

    tagger = Tagger(
        beets_config=settings.beets_config,
        library_dir=settings.library_dir,
        beets_db=settings.beets_db,
    )

    # Create metadata services (MetadataPatcher has HTTP client to manage)
    metadata_enricher = MetadataEnricher()
    metadata_patcher = MetadataPatcher()
    file_organizer = FileOrganizer(playlists_dir=settings.playlists_dir)

    # Create sync services
    album_sync_service = AlbumSyncService(
        downloader=downloader,
        tagger=tagger,
        temp_dir=settings.temp_dir,
    )

    playlist_sync_service = PlaylistSyncService(
        downloader=downloader,
        enricher=metadata_enricher,
        patcher=metadata_patcher,
        file_organizer=file_organizer,
        temp_dir=settings.temp_dir,
        playlists_dir=settings.playlists_dir,
    )

    # Create job management services
    job_store = JobStore(
        clock=lambda: datetime.now(settings.timezone),
        id_generator=lambda: str(uuid.uuid4()),
    )

    job_executor = JobExecutor(
        job_store=job_store,
        album_sync_service=album_sync_service,
        playlist_sync_service=playlist_sync_service,
    )

    return Services(
        job_store=job_store,
        job_executor=job_executor,
        album_sync_service=album_sync_service,
        playlist_sync_service=playlist_sync_service,
        metadata_patcher=metadata_patcher,
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup/shutdown."""
    # Startup: initialize services
    logger.info("Starting application...")
    services = create_services()
    set_services(services)
    app.state.services = services  # Also store in app.state for direct access
    logger.info("Services initialized")

    yield

    # Shutdown: cleanup
    logger.info("Shutting down...")
    app.state.services.close()

    temp_dir = get_settings().temp_dir
    if temp_dir.exists():
        logger.info("Cleaning up temp directory: {}", temp_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)

    logger.info("Shutdown complete")


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

    # CORS middleware (type ignore needed due to Starlette typing limitations)
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
