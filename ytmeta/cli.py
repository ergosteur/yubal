#!/usr/bin/env python3
"""Extract metadata from YouTube Music playlists."""

import json
import re
import sys

import click

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


@click.command()
@click.argument("url", required=False)
@click.option("--full", is_flag=True, help="Include all keys (unfiltered).")
@click.pass_context
def main(ctx: click.Context, url: str | None, full: bool) -> None:
    """Extract metadata from a YouTube Music playlist URL."""
    if not url:
        click.echo(ctx.get_help())
        return

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
