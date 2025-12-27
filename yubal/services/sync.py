import shutil
import tempfile
from collections.abc import Callable
from pathlib import Path

from yubal.core.enums import ProgressStep
from yubal.core.models import AlbumInfo, SyncResult
from yubal.core.progress import ProgressCallback, ProgressEvent
from yubal.services.downloader import Downloader
from yubal.services.tagger import Tagger

# Type for cancellation check function
CancelCheck = Callable[[], bool]


class SyncService:
    """Orchestrates the download → tag workflow."""

    def __init__(
        self,
        library_dir: Path,
        beets_config: Path,
        audio_format: str = "mp3",
    ):
        """
        Initialize the sync service.

        Args:
            library_dir: Directory for the organized music library
            beets_config: Path to beets configuration file
            audio_format: Audio format for downloads (mp3, m4a, opus, etc.)
        """
        self.library_dir = library_dir
        self.beets_config = beets_config
        self.audio_format = audio_format

    def sync_album(
        self,
        url: str,
        progress_callback: ProgressCallback | None = None,
        cancel_check: CancelCheck | None = None,
    ) -> SyncResult:
        """
        Download and tag an album in one operation.

        Progress is calculated as:
        - 0% → 10%: Fetching info phase
        - 10% → 90%: Download phase (proportional to tracks)
        - 90% → 100%: Import/tagging phase

        Args:
            url: YouTube Music album/playlist URL
            progress_callback: Optional callback for progress updates
            cancel_check: Function returning True if operation should cancel

        Returns:
            SyncResult with success status and details
        """
        temp_dir = Path(tempfile.mkdtemp(prefix="yubal_"))
        album_info: AlbumInfo | None = None

        try:
            # Phase 1: Extract album info (0% → 10%)
            if progress_callback:
                progress_callback(
                    ProgressEvent(
                        step=ProgressStep.FETCHING_INFO,
                        message="Fetching album info...",
                        progress=0.0,
                    )
                )

            downloader = Downloader(audio_format=self.audio_format)

            try:
                album_info = downloader.extract_info(url)
                total_tracks = album_info.track_count or 1  # Fallback to 1
            except Exception as e:
                if progress_callback:
                    progress_callback(
                        ProgressEvent(
                            step=ProgressStep.FAILED,
                            message=f"Failed to fetch album info: {e}",
                        )
                    )
                return SyncResult(
                    success=False,
                    error=f"Failed to fetch album info: {e}",
                )

            # Notify with album info - fetching complete at 10%
            if progress_callback:
                progress_callback(
                    ProgressEvent(
                        step=ProgressStep.FETCHING_INFO,
                        message=f"Found {total_tracks} tracks: {album_info.title}",
                        progress=10.0,
                        details={"album_info": album_info.model_dump()},
                    )
                )

            # Phase 2: Download (10% → 90%)
            def download_progress_wrapper(event: ProgressEvent) -> None:
                """Wrapper that calculates album-wide progress for download phase."""
                if not progress_callback:
                    return

                # If no progress info, pass through as-is
                if event.progress is None:
                    progress_callback(event)
                    return

                # Get track index from details (0-based)
                track_idx = 0
                if event.details:
                    track_idx = event.details.get("track_index", 0)

                track_progress = event.progress

                # Calculate album-wide progress: 10 + (tracks_done / total) * 80
                # This maps download progress to the 10-90% range
                album_progress = (
                    10 + ((track_idx + track_progress / 100) / total_tracks) * 80
                )

                progress_callback(
                    ProgressEvent(
                        step=ProgressStep.DOWNLOADING,
                        message=event.message,
                        progress=album_progress,
                    )
                )

            if progress_callback:
                progress_callback(
                    ProgressEvent(
                        step=ProgressStep.DOWNLOADING,
                        message="Starting download...",
                        progress=10.0,
                    )
                )

            download_result = downloader.download_album(
                url,
                temp_dir,
                progress_callback=download_progress_wrapper,
                cancel_check=cancel_check,
            )

            # Check if cancelled
            if download_result.cancelled:
                return SyncResult(
                    success=False,
                    download_result=download_result,
                    album_info=album_info,
                    error="Download cancelled",
                )

            if not download_result.success:
                if progress_callback:
                    progress_callback(
                        ProgressEvent(
                            step=ProgressStep.FAILED,
                            message=download_result.error or "Download failed",
                        )
                    )
                return SyncResult(
                    success=False,
                    download_result=download_result,
                    album_info=album_info,
                    error=download_result.error or "Download failed",
                )

            # Download complete - progress at 90%
            if progress_callback:
                track_count = len(download_result.downloaded_files)
                progress_callback(
                    ProgressEvent(
                        step=ProgressStep.DOWNLOADING,
                        message=f"Downloaded {track_count} tracks",
                        progress=90.0,
                    )
                )

            # Phase 3: Import/Tag (90% → 100%)
            if progress_callback:
                progress_callback(
                    ProgressEvent(
                        step=ProgressStep.IMPORTING,
                        message="Starting import...",
                        progress=90.0,
                    )
                )

            tagger = Tagger(
                beets_config=self.beets_config,
                library_dir=self.library_dir,
                beets_db=self.beets_config.parent / "beets.db",
            )
            tag_result = tagger.tag_album(temp_dir, progress_callback=progress_callback)

            if not tag_result.success:
                if progress_callback:
                    progress_callback(
                        ProgressEvent(
                            step=ProgressStep.FAILED,
                            message=tag_result.error or "Import failed",
                        )
                    )
                return SyncResult(
                    success=False,
                    download_result=download_result,
                    tag_result=tag_result,
                    album_info=album_info,
                    error=tag_result.error or "Import failed",
                )

            # Success - progress at 100%
            if progress_callback:
                progress_callback(
                    ProgressEvent(
                        step=ProgressStep.COMPLETED,
                        message=f"Sync complete: {tag_result.dest_dir}",
                        progress=100.0,
                    )
                )

            return SyncResult(
                success=True,
                download_result=download_result,
                tag_result=tag_result,
                album_info=album_info,
                destination=tag_result.dest_dir,
            )

        except Exception as e:
            # Cleanup on any unexpected failure
            if progress_callback:
                progress_callback(
                    ProgressEvent(
                        step=ProgressStep.FAILED,
                        message=str(e),
                    )
                )
            return SyncResult(
                success=False,
                album_info=album_info,
                error=str(e),
            )

        finally:
            # Cleanup temp directory
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
