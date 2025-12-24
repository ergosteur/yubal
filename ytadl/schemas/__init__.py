"""Pydantic schemas for API requests and responses."""

from ytadl.core import AlbumInfo, SyncResult
from ytadl.schemas.progress import ProgressEventSchema
from ytadl.schemas.sync import SyncRequest, SyncResponse

__all__ = [
    "AlbumInfo",
    "ProgressEventSchema",
    "SyncRequest",
    "SyncResponse",
    "SyncResult",
]
