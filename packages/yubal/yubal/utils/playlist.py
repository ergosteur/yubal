"""Playlist type utilities."""


def is_album_playlist(playlist_id: str) -> bool:
    """Check if a playlist ID represents an album playlist.

    Album playlists in YouTube Music have IDs that start with 'OLAK5uy_'.
    These are auto-generated playlists for album releases.

    Args:
        playlist_id: The playlist ID to check.

    Returns:
        True if the playlist is an album playlist, False otherwise.

    Example:
        >>> is_album_playlist("OLAK5uy_abc123")
        True
        >>> is_album_playlist("PLabc123")
        False
    """
    return playlist_id.startswith("OLAK5uy_")
