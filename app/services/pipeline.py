"""Orchestrates the download -> tag -> organize pipeline."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import uuid
import shutil

from .downloader import Downloader, AlbumInfo
from .tagger import Tagger


@dataclass
class ProcessResult:
    """Final result of processing an album."""

    success: bool
    url: str
    album_info: Optional[AlbumInfo] = None
    final_path: Optional[Path] = None
    track_count: int = 0
    error: Optional[str] = None
    stage_failed: Optional[str] = None  # "download" | "tag" | None
    details: dict = field(default_factory=dict)


class Pipeline:
    """Orchestrates the full album processing workflow."""

    def __init__(
        self,
        downloader: Downloader,
        tagger: Tagger,
        download_dir: Path,
    ):
        self.downloader = downloader
        self.tagger = tagger
        self.download_dir = download_dir

    def process_album(self, url: str) -> ProcessResult:
        """
        Process a YouTube Music album URL through the full pipeline.

        Steps:
        1. Create temporary directory for this job
        2. Download all tracks from the playlist
        3. Tag and organize with beets
        4. Clean up temporary directory
        5. Return result with final location

        Args:
            url: YouTube Music playlist/album URL

        Returns:
            ProcessResult with success status and final path
        """
        job_id = str(uuid.uuid4())[:8]
        temp_dir = self.download_dir / job_id

        try:
            # Step 1: Create temp directory
            temp_dir.mkdir(parents=True, exist_ok=True)

            # Step 2: Download
            download_result = self.downloader.download_album(url, temp_dir)

            if not download_result.success:
                return ProcessResult(
                    success=False,
                    url=url,
                    album_info=download_result.album_info,
                    final_path=None,
                    track_count=0,
                    error=download_result.error,
                    stage_failed="download",
                )

            if not download_result.downloaded_files:
                return ProcessResult(
                    success=False,
                    url=url,
                    album_info=download_result.album_info,
                    final_path=None,
                    track_count=0,
                    error="No files were downloaded",
                    stage_failed="download",
                )

            # Step 3: Tag and organize
            tag_result = self.tagger.tag_album(temp_dir)

            if not tag_result.success:
                return ProcessResult(
                    success=False,
                    url=url,
                    album_info=download_result.album_info,
                    final_path=None,
                    track_count=len(download_result.downloaded_files),
                    error=tag_result.error,
                    stage_failed="tag",
                    details={
                        "stdout": tag_result.stdout,
                        "stderr": tag_result.stderr,
                    },
                )

            # Step 4: Success
            return ProcessResult(
                success=True,
                url=url,
                album_info=download_result.album_info,
                final_path=tag_result.dest_dir,
                track_count=tag_result.track_count or len(download_result.downloaded_files),
                details={
                    "album_name": tag_result.album_name,
                    "artist_name": tag_result.artist_name,
                },
            )

        finally:
            # Step 5: Cleanup temp directory
            if temp_dir.exists():
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except Exception:
                    pass  # Best effort cleanup
