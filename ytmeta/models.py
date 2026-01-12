"""Pydantic models for track metadata."""

from enum import StrEnum

from pydantic import BaseModel


class VideoType(StrEnum):
    """YouTube Music video types."""

    ATV = "ATV"  # Audio Track Video (album version)
    OMV = "OMV"  # Official Music Video


class TrackMetadata(BaseModel):
    """Metadata for a single track."""

    omv_video_id: str  # Canonical ID (OMV from album)
    atv_video_id: str | None = None  # ATV video ID if available
    title: str
    artist: str  # "Artist One; Artist Two"
    album: str
    albumartist: str  # "Artist One; Artist Two"
    tracknumber: int | None = None
    year: str | None = None
    cover_url: str | None = None
    video_type: VideoType  # Source track type
