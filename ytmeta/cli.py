#!/usr/bin/env python3
"""Extract metadata from YouTube Music playlists."""

import json
import re
import sys

import click
from rich.console import Console
from rich.table import Table
from ytmusicapi import YTMusic

from ytmeta.extractor import extract_metadata
from ytmeta.models import TrackMetadata
from ytmeta.tracker import TrackedYTMusic

FILTERED_KEYS = {
    "playabilityStatus",
    "streamingData",
    "playbackTracking",
    "microformat",
    "related_recommendations",
}


def parse_playlist_id(url: str) -> str:
    """Extract playlist ID from YouTube Music URL."""
    if match := re.search(r"list=([A-Za-z0-9_-]+)", url):
        return match.group(1)
    raise ValueError(f"Could not extract playlist ID from: {url}")


def fetch_all(ytm: TrackedYTMusic, url: str) -> None:
    """Fetch playlist, songs, and albums."""
    playlist = ytm.get_playlist(parse_playlist_id(url), limit=None)

    for track in playlist.get("tracks", []) or []:
        if not track:
            continue
        if video_id := track.get("videoId"):
            ytm.get_song(video_id)
        if album_id := (track.get("album") or {}).get("id"):
            ytm.get_album(album_id)
        else:
            # Fallback search for tracks without album info (e.g., OMV)
            # Note: limit param is a minimum, not max (YT returns 20+ per page)
            artists = " ".join(a.get("name", "") for a in track.get("artists", []))
            title = track.get("title", "")
            if artists or title:
                query = f"{artists} {title}".strip()
                ytm.search(query, filter="songs", limit=1, ignore_spelling=True)


def print_rich_table(tracks: list[TrackMetadata]) -> None:
    """Print tracks as a Rich table."""
    console = Console()
    table = Table(show_header=True, header_style="bold")

    table.add_column("OMV ID")
    table.add_column("ATV ID")
    table.add_column("Title")
    table.add_column("Artist")
    table.add_column("Album")
    table.add_column("Year")
    table.add_column("#", justify="right")
    table.add_column("Type")

    for t in tracks:
        table.add_row(
            t.omv_video_id,
            t.atv_video_id or "",
            t.title,
            t.artist,
            t.album,
            t.year or "",
            str(t.tracknumber) if t.tracknumber else "",
            t.video_type,
        )

    console.print(table)
    console.print(f"\nExtracted {len(tracks)} track(s)")


@click.group()
def main() -> None:
    """Extract metadata from YouTube Music playlists."""


@main.command(name="meta")
@click.argument("url")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON.")
def meta_cmd(url: str, as_json: bool) -> None:
    """Extract structured metadata from a playlist."""
    try:
        ytm = YTMusic()
        tracks = extract_metadata(ytm, url)

        if as_json:
            data = [t.model_dump() for t in tracks]
            json.dump(data, sys.stdout, indent=2, ensure_ascii=False, default=str)
        else:
            print_rich_table(tracks)
    except Exception as e:
        raise click.ClickException(str(e)) from e


@main.command()
@click.argument("url")
@click.option("--full", is_flag=True, help="Include all keys (unfiltered).")
def dump(url: str, full: bool) -> None:
    """Dump raw API responses as JSON."""
    try:
        ytm = TrackedYTMusic()
        fetch_all(ytm, url)

        output = ytm.responses
        if not full:

            def filter_resp(r: dict) -> dict:
                resp = r["response"]
                if isinstance(resp, dict):
                    resp = {k: v for k, v in resp.items() if k not in FILTERED_KEYS}
                return {**r, "response": resp}

            output = [filter_resp(r) for r in output]

        json.dump(output, sys.stdout, indent=2, ensure_ascii=False, default=str)
    except Exception as e:
        raise click.ClickException(str(e)) from e


if __name__ == "__main__":
    main()
