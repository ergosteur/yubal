"""Core utilities shared across CLI and API."""

from app.core.config import (
    APP_ROOT,
    CONFIG_DIR,
    DATA_DIR,
    DEFAULT_BEETS_CONFIG,
    DEFAULT_BEETS_DB,
    DEFAULT_LIBRARY_DIR,
)
from app.core.models import (
    AlbumInfo,
    DownloadResult,
    LibraryHealth,
    SyncResult,
    TagResult,
    TrackInfo,
)
from app.core.progress import ProgressCallback, ProgressEvent, ProgressStep

__all__ = [
    "APP_ROOT",
    "CONFIG_DIR",
    "DATA_DIR",
    "DEFAULT_BEETS_CONFIG",
    "DEFAULT_BEETS_DB",
    "DEFAULT_LIBRARY_DIR",
    "AlbumInfo",
    "DownloadResult",
    "LibraryHealth",
    "ProgressCallback",
    "ProgressEvent",
    "ProgressStep",
    "SyncResult",
    "TagResult",
    "TrackInfo",
]
