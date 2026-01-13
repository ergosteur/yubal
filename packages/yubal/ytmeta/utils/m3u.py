"""M3U playlist file generation utilities.

M3U files are written with UTF-8 encoding, which is the modern standard
supported by most media players.
"""

import os
from pathlib import Path

from ytmeta.models.domain import TrackMetadata
from ytmeta.utils.filename import clean_filename


def generate_m3u(tracks: list[tuple[TrackMetadata, Path]], m3u_path: Path) -> str:
    """Generate M3U playlist content with paths relative to the M3U file location.

    Creates an extended M3U format file with track duration and title information.

    Args:
        tracks: List of tuples containing (TrackMetadata, file_path) for each track.
        m3u_path: Path where the M3U file will be written (used for relative paths).

    Returns:
        M3U file content as a string.

    Example:
        >>> from pathlib import Path
        >>> tracks = [(track_meta, Path("/music/Artist/2024 - Album/01 - Song.opus"))]
        >>> m3u_path = Path("/music/Playlists/My Playlist.m3u")
        >>> content = generate_m3u(tracks, m3u_path)
        >>> print(content)
        #EXTM3U
        #EXTINF:-1,Artist One; Artist Two - Song Title
        ../Artist/2024 - Album/01 - Song.opus
    """
    lines = ["#EXTM3U"]

    for track, file_path in tracks:
        # Get duration from track metadata, use -1 if unknown
        # TrackMetadata doesn't have duration, so use -1
        duration = -1

        # Format: Artist - Title
        display_title = f"{track.artist} - {track.title}"

        # EXTINF line: #EXTINF:duration,display title
        lines.append(f"#EXTINF:{duration},{display_title}")

        # Relative path from M3U file location to track file
        try:
            relative_path = os.path.relpath(file_path, m3u_path.parent)
        except ValueError:
            relative_path = str(file_path)  # Fall back to absolute
        lines.append(relative_path)

    # Ensure trailing newline
    return "\n".join(lines) + "\n"


def write_m3u(
    base_path: Path,
    playlist_name: str,
    tracks: list[tuple[TrackMetadata, Path]],
) -> Path:
    """Write an M3U playlist file to the Playlists folder.

    Creates the Playlists directory if it doesn't exist.
    Sanitizes the playlist name for safe filesystem usage.

    Args:
        base_path: Base directory for downloads (e.g., /music or ./data).
        playlist_name: Name of the playlist (will be sanitized for filename).
        tracks: List of tuples containing (TrackMetadata, file_path) for each track.

    Returns:
        Path to the written M3U file.

    Example:
        >>> from pathlib import Path
        >>> tracks = [(track_meta, Path("/music/Artist/2024 - Album/01 - Song.opus"))]
        >>> m3u_path = write_m3u(Path("/music"), "My Favorites", tracks)
        >>> print(m3u_path)
        /music/Playlists/My Favorites.m3u
    """
    # Create Playlists directory
    playlists_dir = base_path / "Playlists"
    playlists_dir.mkdir(parents=True, exist_ok=True)

    # Sanitize playlist name for safe filename
    safe_name = clean_filename(playlist_name)
    if not safe_name or not safe_name.strip():
        safe_name = "Untitled Playlist"

    # Build M3U file path
    m3u_path = playlists_dir / f"{safe_name}.m3u"

    # Generate and write content
    content = generate_m3u(tracks, m3u_path)
    m3u_path.write_text(content, encoding="utf-8")

    return m3u_path
