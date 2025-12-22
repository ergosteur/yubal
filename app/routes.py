"""Flask route definitions."""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from urllib.parse import urlparse
import re

from config.settings import settings
from .services.pipeline import Pipeline
from .services.downloader import Downloader
from .services.tagger import Tagger

main = Blueprint("main", __name__)


def create_pipeline() -> Pipeline:
    """Factory function to create pipeline with dependencies."""
    downloader = Downloader(
        audio_format=settings.AUDIO_FORMAT,
        audio_quality=settings.AUDIO_QUALITY,
    )
    tagger = Tagger(
        beets_config=settings.BEETS_CONFIG,
        library_dir=settings.LIBRARY_DIR,
        beets_db=settings.BEETS_DB,
    )
    return Pipeline(
        downloader=downloader,
        tagger=tagger,
        download_dir=settings.DOWNLOAD_DIR,
    )


def validate_url(url: str) -> tuple[bool, str]:
    """
    Validate that URL is a YouTube Music playlist/album.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url:
        return False, "URL is required"

    url = url.strip()

    try:
        parsed = urlparse(url)

        # Check domain
        if parsed.netloc not in settings.ALLOWED_DOMAINS:
            return False, "URL must be from YouTube or YouTube Music"

        # Check for playlist/album indicators
        is_playlist = (
            "list=" in url
            or "/playlist" in url
            or "OLAK5uy_" in url
            or "RDCLAK5uy_" in url
            or "/browse/MPREb_" in url
        )

        if not is_playlist:
            return False, "URL must be a playlist or album URL (should contain 'list=' parameter)"

        return True, ""

    except Exception:
        return False, "Invalid URL format"


def is_youtube_music_album(url: str) -> bool:
    """Check if URL matches YouTube Music album patterns."""
    patterns = [
        r"https?://music\.youtube\.com/playlist\?list=OLAK5uy_",
        r"https?://music\.youtube\.com/browse/MPREb_",
        r"https?://(www\.)?youtube\.com/playlist\?list=",
    ]
    return any(re.match(pattern, url) for pattern in patterns)


@main.route("/", methods=["GET"])
def index():
    """Display the main form."""
    return render_template("index.html")


@main.route("/download", methods=["POST"])
def download():
    """Process album download request."""
    url = request.form.get("url", "").strip()

    # Validate URL
    is_valid, error = validate_url(url)
    if not is_valid:
        flash(error, "error")
        return redirect(url_for("main.index"))

    # Process album
    pipeline = create_pipeline()
    result = pipeline.process_album(url)

    return render_template("result.html", result=result)
