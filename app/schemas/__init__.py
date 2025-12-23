"""Pydantic schemas for API requests and responses."""

from app.core import AlbumInfo, SyncResult
from app.schemas.progress import ProgressEventSchema
from app.schemas.sync import SyncRequest, SyncResponse

__all__ = [
    "AlbumInfo",
    "ProgressEventSchema",
    "SyncRequest",
    "SyncResponse",
    "SyncResult",
]
