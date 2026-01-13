"""Thumbnail selection utilities."""

from yubal.models.ytmusic import Thumbnail


def get_square_thumbnail(thumbnails: list[Thumbnail]) -> str | None:
    """Get the largest square thumbnail URL.

    Args:
        thumbnails: List of Thumbnail objects.

    Returns:
        URL of the largest square thumbnail, or last thumbnail if no square found.
    """
    if not thumbnails:
        return None

    # Filter for square thumbnails and get largest
    square = [t for t in thumbnails if t.width == t.height]
    if square:
        return max(square, key=lambda t: t.width).url

    # Fallback to last thumbnail
    return thumbnails[-1].url
