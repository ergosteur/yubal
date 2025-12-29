import uuid
from datetime import datetime
from pathlib import Path
from typing import Annotated

from fastapi import Depends

from yubal.services.downloader import Downloader
from yubal.services.job_store import JobStore
from yubal.services.sync import SyncService
from yubal.services.tagger import Tagger
from yubal.settings import get_settings

# Get settings for timezone configuration
_settings = get_settings()

# Global singleton instance
job_store = JobStore(
    clock=lambda: datetime.now(_settings.timezone),
    id_generator=lambda: str(uuid.uuid4()),
)


def get_job_store() -> JobStore:
    return job_store


def get_audio_format() -> str:
    """Get audio format from settings."""
    return get_settings().audio_format


def get_cookies_file() -> Path:
    """Get cookies file path from settings."""
    return get_settings().cookies_file


def get_ytdlp_dir() -> Path:
    """Get yt-dlp directory from settings."""
    return get_settings().ytdlp_dir


def get_sync_service() -> SyncService:
    """Factory for creating SyncService with injected dependencies."""
    settings = get_settings()
    return SyncService(
        library_dir=settings.library_dir,
        beets_config=settings.beets_config,
        audio_format=settings.audio_format,
        temp_dir=settings.temp_dir,
        downloader=Downloader(
            audio_format=settings.audio_format,
            cookies_file=settings.cookies_file,
        ),
        tagger=Tagger(
            beets_config=settings.beets_config,
            library_dir=settings.library_dir,
            beets_db=settings.beets_db,
        ),
    )


SyncServiceDep = Annotated[SyncService, Depends(get_sync_service)]
CookiesFileDep = Annotated[Path, Depends(get_cookies_file)]
YtdlpDirDep = Annotated[Path, Depends(get_ytdlp_dir)]
JobStoreDep = Annotated[JobStore, Depends(get_job_store)]
AudioFormatDep = Annotated[str, Depends(get_audio_format)]
