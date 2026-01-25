"""URL parsing utilities."""

import re

from yubal.exceptions import PlaylistParseError

PLAYLIST_ID_PATTERN = re.compile(r"list=([A-Za-z0-9_-]+)")
VIDEO_ID_PATTERN = re.compile(r"v=([A-Za-z0-9_-]+)")

# Maximum URL length to prevent potential abuse (standard browser limit)
MAX_URL_LENGTH = 2048


def parse_playlist_id(url: str) -> str:
    """Extract playlist ID from YouTube Music URL.

    Args:
        url: Full YouTube Music playlist URL.

    Returns:
        The playlist ID string.

    Raises:
        PlaylistParseError: If playlist ID cannot be extracted or URL is too long.
    """
    if not url or len(url) > MAX_URL_LENGTH:
        raise PlaylistParseError(f"Could not extract playlist ID from: {url}")
    if match := PLAYLIST_ID_PATTERN.search(url):
        return match.group(1)
    raise PlaylistParseError(f"Could not extract playlist ID from: {url}")


def parse_video_id(url: str) -> str | None:
    """Extract video ID from YouTube watch URL.

    Returns None if a playlist ID is present (playlist URLs take priority).

    Args:
        url: Full YouTube or YouTube Music watch URL.

    Returns:
        The video ID string, or None if not found, URL is too long,
        or if a playlist ID is present.
    """
    # Validate URL length
    if not url or len(url) > MAX_URL_LENGTH:
        return None

    # Playlist URLs take priority - if list= is present, return None
    if PLAYLIST_ID_PATTERN.search(url):
        return None

    # Extract video ID from v= parameter
    if match := VIDEO_ID_PATTERN.search(url):
        return match.group(1)

    return None


def is_single_track_url(url: str) -> bool:
    """Check if URL is a single track (not a playlist).

    Args:
        url: YouTube or YouTube Music URL.

    Returns:
        True if the URL is a single track URL, False otherwise.
    """
    return parse_video_id(url) is not None


def is_supported_url(url: str) -> bool:
    """Check if URL is supported by yubal (playlist, album, or single track).

    Args:
        url: YouTube or YouTube Music URL.

    Returns:
        True if the URL can be processed by yubal, False otherwise.
    """
    if not url or len(url) > MAX_URL_LENGTH:
        return False

    url = url.strip()

    # Playlist URL (has list= parameter)
    if PLAYLIST_ID_PATTERN.search(url):
        return True

    # Single track URL (has v= parameter without list=)
    if VIDEO_ID_PATTERN.search(url):
        return True

    # Browse URL (album pages on music.youtube.com)
    if "/browse/" in url and "music.youtube.com" in url:
        return True

    return False
