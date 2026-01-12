"""Metadata extraction from YouTube Music playlists."""

import re

from ytmusicapi import YTMusic

from ytmeta.models import TrackMetadata, VideoType


def parse_playlist_id(url: str) -> str:
    """Extract playlist ID from YouTube Music URL."""
    if match := re.search(r"list=([A-Za-z0-9_-]+)", url):
        return match.group(1)
    raise ValueError(f"Could not extract playlist ID from: {url}")


def format_artists(artists: list[dict] | None) -> str:
    """Format artists list as 'Artist One; Artist Two'."""
    if not artists:
        return ""
    return "; ".join(a.get("name", "") for a in artists if a.get("name"))


def get_square_thumbnail(thumbnails: list[dict] | None) -> str | None:
    """Get the largest square thumbnail URL."""
    if not thumbnails:
        return None
    # Filter for square thumbnails and get largest
    square = [t for t in thumbnails if t.get("width") == t.get("height")]
    if square:
        return max(square, key=lambda t: t.get("width", 0)).get("url")
    # Fallback to any thumbnail
    return thumbnails[-1].get("url") if thumbnails else None


def find_track_in_album(album: dict, track: dict) -> dict | None:
    """Find a track in album by title or duration."""
    target_title = track.get("title", "").lower().strip()
    target_duration = track.get("duration_seconds")
    album_tracks = album.get("tracks", [])

    # First try: match by title
    for album_track in album_tracks:
        if album_track.get("title", "").lower().strip() == target_title:
            return album_track

    # Second try: match by duration if unique
    if target_duration:
        matches = [
            t for t in album_tracks if t.get("duration_seconds") == target_duration
        ]
        if len(matches) == 1:
            return matches[0]

    return None


def extract_metadata(ytm: YTMusic, url: str) -> list[TrackMetadata]:
    """Extract metadata for all tracks in a playlist."""
    playlist = ytm.get_playlist(parse_playlist_id(url), limit=None)
    tracks = playlist.get("tracks", []) or []
    results = []

    for track in tracks:
        if not track:
            continue

        video_id = track.get("videoId")
        if not video_id:
            continue

        video_type_raw = track.get("videoType", "")
        video_type = VideoType.ATV if "ATV" in video_type_raw else VideoType.OMV
        album_id = (track.get("album") or {}).get("id")
        search_atv_id = None  # ATV found via search (for OMV tracks)

        # For OMV without album, search for the track
        if not album_id:
            artists = format_artists(track.get("artists"))
            title = track.get("title", "")
            query = f"{artists} {title}".strip()
            if query:
                search_results = ytm.search(
                    query, filter="songs", limit=1, ignore_spelling=True
                )
                # Find first result with album info
                for result in search_results:
                    if result.get("album", {}).get("id"):
                        album_id = result["album"]["id"]
                        # Capture ATV videoId from search result
                        if result.get("videoType") == "MUSIC_VIDEO_TYPE_ATV":
                            search_atv_id = result.get("videoId")
                        break

        # Get album details
        album = ytm.get_album(album_id) if album_id else None

        if album:
            # Try to find track in album for track number
            album_track = find_track_in_album(album, track)

            # Use album track info if found, otherwise use original track info
            track_title = (
                album_track.get("title", "") if album_track else track.get("title", "")
            )
            track_artists = (
                album_track.get("artists") if album_track else track.get("artists")
            )
            track_number = album_track.get("trackNumber") if album_track else None

            # OMV from album track, ATV from playlist (if ATV) or search
            omv_id = album_track.get("videoId") if album_track else None
            atv_id = video_id if video_type == VideoType.ATV else search_atv_id

            meta = TrackMetadata(
                omv_video_id=omv_id or video_id,  # Fallback to source if no match
                atv_video_id=atv_id,
                title=track_title,
                artist=format_artists(track_artists),
                album=album.get("title", ""),
                albumartist=format_artists(album.get("artists")),
                tracknumber=track_number,
                year=album.get("year"),
                cover_url=get_square_thumbnail(album.get("thumbnails")),
                video_type=video_type,
            )
        else:
            # Fallback: use track info directly (must be OMV since ATV has album)
            meta = TrackMetadata(
                omv_video_id=video_id,
                atv_video_id=None,
                title=track.get("title", ""),
                artist=format_artists(track.get("artists")),
                album=(track.get("album") or {}).get("name", ""),
                albumartist=format_artists(track.get("artists")),
                tracknumber=None,
                year=None,
                cover_url=get_square_thumbnail(track.get("thumbnails")),
                video_type=video_type,
            )

        results.append(meta)

    return results
