"""YouTube Music downloader using yt-dlp Python API."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

import yt_dlp
from yt_dlp.postprocessor.metadataparser import MetadataParserPP

from app.constants import AUDIO_EXTENSIONS
from app.core import (
    AlbumInfo,
    DownloadResult,
    ProgressCallback,
    ProgressEvent,
    ProgressStep,
    TrackInfo,
)


class Downloader:
    """Handles YouTube Music album downloads via yt-dlp."""

    def __init__(self, audio_format: str = "mp3", audio_quality: str = "0"):
        self.audio_format = audio_format
        self.audio_quality = audio_quality

    def extract_info(self, url: str) -> AlbumInfo:
        """
        Extract album/playlist metadata without downloading.

        Args:
            url: YouTube Music playlist URL

        Returns:
            AlbumInfo with album and track metadata

        Raises:
            ValueError: If URL is not a valid playlist
            yt_dlp.DownloadError: If extraction fails
        """
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                raise ValueError("Could not extract info from URL")
            return self._parse_album_info(info, url)

    def _extract_year(self, info: dict[str, Any]) -> int | None:
        """Extract year from upload_date or release_year."""
        if info.get("release_year"):
            return info["release_year"]
        upload_date = info.get("upload_date", "")
        if upload_date and len(upload_date) >= 4:
            try:
                return int(upload_date[:4])
            except ValueError:
                pass
        return None

    def _create_progress_hook(
        self,
        downloaded_files: list[Path],
        progress_callback: ProgressCallback | None = None,
    ) -> Callable[[dict[str, Any]], None]:
        """Create a progress hook that tracks downloaded files."""

        def hook(d: dict[str, Any]) -> None:
            if d["status"] == "downloading":
                percent_str = d.get("_percent_str", "").strip()
                speed = d.get("_speed_str", "").strip()
                # Parse percentage for callback
                percent_value: float | None = None
                if percent_str:
                    try:
                        percent_value = float(percent_str.rstrip("%"))
                    except ValueError:
                        pass

                if progress_callback and percent_value is not None:
                    progress_callback(
                        ProgressEvent(
                            step=ProgressStep.DOWNLOADING,
                            message=f"Downloading: {percent_str} at {speed}",
                            progress=percent_value,
                            details={"speed": speed},
                        )
                    )
                elif percent_str:
                    print(
                        f"\r  Downloading: {percent_str} at {speed}", end="", flush=True
                    )
            elif d["status"] == "finished":
                print()  # New line after progress
                filename = d.get("info_dict", {}).get("filepath") or d.get("filename")
                if filename:
                    downloaded_files.append(Path(filename))
                    msg = f"Completed: {Path(filename).name}"
                    if progress_callback:
                        progress_callback(
                            ProgressEvent(
                                step=ProgressStep.DOWNLOADING,
                                message=msg,
                                progress=100.0,
                                details={"filename": Path(filename).name},
                            )
                        )
                    else:
                        print(f"  {msg}")

        return hook

    def download_album(
        self,
        url: str,
        output_dir: Path,
        progress_callback: ProgressCallback | None = None,
    ) -> DownloadResult:
        """
        Download all tracks from a YouTube Music album.

        Args:
            url: YouTube Music playlist URL
            output_dir: Directory to save downloaded files
            progress_callback: Optional callback for progress updates

        Returns:
            DownloadResult with success status and file paths
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        downloaded_files: list[Path] = []
        album_info: AlbumInfo | None = None

        ydl_opts = self._get_ydl_opts(
            output_dir,
            self._create_progress_hook(downloaded_files, progress_callback),
        )

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                album_info = self._parse_album_info(info, url)

            # Find all audio files in output directory
            all_files = [
                f
                for f in output_dir.iterdir()
                if f.is_file() and f.suffix.lower() in AUDIO_EXTENSIONS
            ]

            return DownloadResult(
                success=True,
                album_info=album_info,
                output_dir=str(output_dir),
                downloaded_files=[str(f) for f in all_files],
            )

        except yt_dlp.DownloadError as e:
            return DownloadResult(
                success=False,
                album_info=album_info,
                output_dir=str(output_dir),
                error=str(e),
            )
        except Exception as e:
            return DownloadResult(
                success=False,
                album_info=album_info,
                output_dir=str(output_dir),
                error=f"Unexpected error: {e!s}",
            )

    def _parse_album_info(self, info: dict[str, Any], url: str) -> AlbumInfo:
        """Parse album info from yt-dlp extraction result."""
        if not info:
            return AlbumInfo(
                title="Unknown",
                artist="Unknown",
                year=None,
                track_count=0,
                url=url,
            )

        if "entries" in info:
            entries = list(info.get("entries", []))
            tracks = []
            for i, entry in enumerate(entries, 1):
                if entry:
                    tracks.append(
                        TrackInfo(
                            title=entry.get("title", f"Track {i}"),
                            artist=entry.get(
                                "artist", entry.get("uploader", "Unknown")
                            ),
                            track_number=i,
                            duration=entry.get("duration", 0),
                        )
                    )

            return AlbumInfo(
                title=info.get("title", "Unknown Album"),
                artist=info.get("uploader", info.get("channel", "Unknown")),
                year=self._extract_year(info),
                track_count=len(tracks),
                tracks=tracks,
                playlist_id=info.get("id", ""),
                url=url,
            )

        # Single track
        return AlbumInfo(
            title=info.get("album", info.get("title", "Unknown")),
            artist=info.get("artist", info.get("uploader", "Unknown")),
            year=self._extract_year(info),
            track_count=1,
            tracks=[
                TrackInfo(
                    title=info.get("title", "Unknown"),
                    artist=info.get("artist", "Unknown"),
                    track_number=1,
                    duration=info.get("duration", 0),
                )
            ],
            playlist_id=info.get("id", ""),
            url=url,
        )

    def _get_ydl_opts(
        self, output_dir: Path, progress_hook: Callable[[dict[str, Any]], None]
    ) -> dict[str, Any]:
        """Build yt-dlp options dictionary."""
        return {
            "format": "bestaudio/best",
            "remote_components": ["ejs:github"],
            "outtmpl": str(output_dir / "%(playlist_index|0)02d - %(title)s.%(ext)s"),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": self.audio_format,
                    "preferredquality": self.audio_quality,
                },
                # Set track number from playlist index, use release_date
                {
                    "key": "MetadataParser",
                    "when": "pre_process",
                    "actions": [
                        (
                            MetadataParserPP.Actions.INTERPRET,
                            "playlist_index",
                            "%(meta_track)s",
                        ),
                        (
                            MetadataParserPP.Actions.INTERPRET,
                            "release_date",
                            "%(meta_date)s",
                        ),
                        (
                            MetadataParserPP.Actions.INTERPRET,
                            "%(artists.0)s",
                            "%(meta_artist)s",
                        ),
                    ],
                },
                {
                    "key": "FFmpegMetadata",
                    "add_metadata": True,
                },
                {
                    "key": "EmbedThumbnail",
                },
            ],
            "writethumbnail": True,
            "progress_hooks": [progress_hook],
            "ignoreerrors": True,  # Continue on individual track errors
            "no_warnings": False,
            "quiet": False,
        }
