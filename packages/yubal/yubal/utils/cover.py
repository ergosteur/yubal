"""Cover art fetching with caching."""

from __future__ import annotations

import logging
import urllib.request
from importlib.metadata import version
from urllib.error import HTTPError, URLError

logger = logging.getLogger(__name__)

_cover_cache: dict[str, bytes] = {}

# Get version from package metadata for User-Agent
_VERSION = version("yubal")


def fetch_cover(url: str | None, timeout: float = 30.0) -> bytes | None:
    """Fetch cover art from URL with caching.

    Args:
        url: Cover art URL.
        timeout: Request timeout in seconds.

    Returns:
        Cover image bytes or None if unavailable.
    """
    if not url:
        return None

    if url in _cover_cache:
        logger.debug("Cover cache hit: %s", url)
        return _cover_cache[url]

    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": f"yubal/{_VERSION}"},
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = response.read()
            _cover_cache[url] = data
            logger.debug("Fetched and cached cover: %s (%d bytes)", url, len(data))
            return data
    except (HTTPError, URLError, OSError, TimeoutError) as e:
        logger.warning("Failed to fetch cover from %s: %s", url, e)
        return None


def clear_cover_cache() -> None:
    """Clear the cover art cache."""
    _cover_cache.clear()


def get_cover_cache_size() -> int:
    """Get the number of cached cover images.

    Returns:
        Number of URLs currently cached.
    """
    return len(_cover_cache)
