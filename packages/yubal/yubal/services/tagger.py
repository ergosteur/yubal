"""Audio file tagging service using mediafile."""

from __future__ import annotations

import logging
from pathlib import Path

from mediafile import Image, MediaFile

from yubal.models.domain import TrackMetadata

logger = logging.getLogger(__name__)


def tag_track(path: Path, track: TrackMetadata, cover: bytes | None = None) -> None:
    """Apply metadata tags to audio file.

    Args:
        path: Path to the audio file.
        track: Track metadata to apply.
        cover: Optional cover art bytes (JPEG or PNG).

    Raises:
        Exception: If tagging fails (caller should handle gracefully).
    """
    audio = MediaFile(path)

    # Basic metadata
    audio.title = track.title
    audio.artist = track.artist  # Already joined with "; "
    audio.album = track.album
    audio.albumartist = track.album_artist  # Already joined with "; "

    # Track numbering
    if track.track_number is not None:
        audio.track = track.track_number
    if track.total_tracks is not None:
        audio.tracktotal = track.total_tracks

    # Year (parse from string if present)
    if track.year:
        try:
            audio.year = int(track.year)
        except ValueError:
            logger.debug("Could not parse year: %s", track.year)

    # Cover art (Image auto-detects MIME type from magic bytes)
    if cover:
        audio.images = [Image(data=cover)]

    audio.save()
    logger.debug("Tagged: %s", path)
