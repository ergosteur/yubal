"""URL parsing utilities."""

import re

from yubal.exceptions import PlaylistParseError

PLAYLIST_ID_PATTERN = re.compile(r"list=([A-Za-z0-9_-]+)")


def parse_playlist_id(url: str) -> str:
    """Extract playlist ID from YouTube Music URL.

    Args:
        url: Full YouTube Music playlist URL.

    Returns:
        The playlist ID string.

    Raises:
        PlaylistParseError: If playlist ID cannot be extracted.
    """
    if match := PLAYLIST_ID_PATTERN.search(url):
        return match.group(1)
    raise PlaylistParseError(f"Could not extract playlist ID from: {url}")
