"""FastAPI dependency injection factories."""

from pathlib import Path
from typing import TYPE_CHECKING, Annotated

from fastapi import Depends

from yubal.core.types import AudioFormat
from yubal.services.job_executor import JobExecutor
from yubal.services.job_store import JobStore
from yubal.services.sync import AlbumSyncService, PlaylistSyncService
from yubal.settings import get_settings

if TYPE_CHECKING:
    from yubal.api.app import Services

# Module-level services container, initialized by lifespan
_services: "Services | None" = None


def set_services(services: "Services") -> None:
    """Set the services container. Called by lifespan on startup."""
    global _services
    _services = services


def get_services() -> "Services":
    """Get the services container."""
    if _services is None:
        raise RuntimeError("Services not initialized. Is the app running?")
    return _services


def get_job_store() -> JobStore:
    """Get the job store from services container."""
    return get_services().job_store


def get_job_executor() -> JobExecutor:
    """Get the job executor from services container."""
    return get_services().job_executor


def get_album_sync_service() -> AlbumSyncService:
    """Get the album sync service from services container."""
    return get_services().album_sync_service


def get_playlist_sync_service() -> PlaylistSyncService:
    """Get the playlist sync service from services container."""
    return get_services().playlist_sync_service


def get_audio_format() -> AudioFormat:
    """Get audio format from settings."""
    return get_settings().audio_format


def get_cookies_file() -> Path:
    """Get cookies file path from settings."""
    return get_settings().cookies_file


def get_ytdlp_dir() -> Path:
    """Get yt-dlp directory from settings."""
    return get_settings().ytdlp_dir


# Type aliases for FastAPI dependency injection
CookiesFileDep = Annotated[Path, Depends(get_cookies_file)]
YtdlpDirDep = Annotated[Path, Depends(get_ytdlp_dir)]
JobStoreDep = Annotated[JobStore, Depends(get_job_store)]
AudioFormatDep = Annotated[AudioFormat, Depends(get_audio_format)]
AlbumSyncServiceDep = Annotated[AlbumSyncService, Depends(get_album_sync_service)]
PlaylistSyncServiceDep = Annotated[
    PlaylistSyncService, Depends(get_playlist_sync_service)
]
JobExecutorDep = Annotated[JobExecutor, Depends(get_job_executor)]
