"""Playlist sync service for downloading and organizing playlists."""

import re
from dataclasses import dataclass
from pathlib import Path

from loguru import logger

from yubal.core.enums import ProgressStep
from yubal.core.models import AlbumInfo, DownloadResult, SyncResult
from yubal.core.utils import extract_playlist_id
from yubal.services.downloader import Downloader
from yubal.services.file_organizer import FileOrganizer
from yubal.services.m3u_generator import generate_m3u
from yubal.services.metadata_enricher import MetadataEnricher
from yubal.services.metadata_patcher import MetadataPatcher
from yubal.services.sync.cancel import CancelToken
from yubal.services.sync.progress import ProgressEmitter
from yubal.services.sync.temp_dir import job_temp_dir

# Progress thresholds for playlist sync
PLAYLIST_PROGRESS_START = 0.0
PLAYLIST_PROGRESS_FETCH_DONE = 10.0
PLAYLIST_PROGRESS_DOWNLOAD_DONE = 60.0
PLAYLIST_PROGRESS_PATCH_DONE = 70.0
PLAYLIST_PROGRESS_ORGANIZE_DONE = 75.0
PLAYLIST_PROGRESS_BEETS_DONE = 90.0
PLAYLIST_PROGRESS_COMPLETE = 100.0

# Pattern to extract track number from filename (e.g., "01 - Title.opus" -> 1)
_TRACK_NUM_PATTERN = re.compile(r"^(\d+)\s*-")


@dataclass
class PlaylistSyncService:
    """Service for syncing playlists from YouTube Music.

    Orchestrates the download -> enrich -> patch -> organize workflow
    for playlist imports. Unlike albums, playlists keep files in a
    dedicated Playlists/ directory structure.

    Attributes:
        downloader: Service for downloading from YouTube
        enricher: Service for fetching rich metadata via ytmusicapi
        patcher: Service for patching audio file metadata
        file_organizer: Service for organizing files into playlist directories
        temp_dir: Base directory for temporary download files
        playlists_dir: Directory for final playlist outputs
    """

    downloader: Downloader
    enricher: MetadataEnricher
    patcher: MetadataPatcher
    file_organizer: FileOrganizer
    temp_dir: Path
    playlists_dir: Path

    def execute(
        self,
        url: str,
        job_id: str,
        progress: ProgressEmitter,
        cancel: CancelToken,
    ) -> SyncResult:
        """Download and organize a playlist with metadata enrichment.

        Progress phases:
        - 0% -> 10%: Enriching metadata via ytmusicapi
        - 10% -> 60%: Downloading tracks via yt-dlp
        - 60% -> 70%: Patching metadata with enriched data
        - 70% -> 75%: Organizing files to Playlists/{name}/
        - 75% -> 90%: Reserved for future beets integration
        - 90% -> 100%: Generating M3U playlist

        Args:
            url: YouTube Music playlist URL
            job_id: Unique job identifier (used for temp directory)
            progress: Emitter for progress updates
            cancel: Token for checking/signaling cancellation

        Returns:
            SyncResult with success status and details
        """
        album_info: AlbumInfo | None = None

        with job_temp_dir(self.temp_dir, job_id) as temp_path:
            try:
                # Phase 1: Enrich metadata via ytmusicapi (0% -> 10%)
                progress.emit(
                    ProgressStep.FETCHING_INFO,
                    "Enriching playlist metadata...",
                    PLAYLIST_PROGRESS_START,
                )

                playlist_id = extract_playlist_id(url)
                if not playlist_id:
                    return SyncResult(
                        success=False,
                        error="Could not extract playlist ID from URL",
                    )

                try:
                    playlist_meta = self.enricher.get_playlist(playlist_id)
                except Exception as e:
                    logger.error("Failed to enrich playlist metadata: {}", e)
                    return SyncResult(
                        success=False,
                        error=f"Failed to fetch playlist metadata: {e}",
                    )

                if not playlist_meta.tracks:
                    return SyncResult(
                        success=False,
                        error="No available tracks in playlist",
                    )

                album_info = AlbumInfo(
                    title=playlist_meta.title,
                    artist="Various Artists",
                    track_count=playlist_meta.track_count,
                    playlist_id=playlist_id,
                    url=url,
                )

                progress.emit(
                    ProgressStep.FETCHING_INFO,
                    f"Found {playlist_meta.track_count} tracks: {playlist_meta.title}",
                    PLAYLIST_PROGRESS_FETCH_DONE,
                    {"album_info": album_info.model_dump()},
                )

                if cancel.is_cancelled():
                    return SyncResult(
                        success=False,
                        album_info=album_info,
                        error="Cancelled",
                    )

                # Phase 2: Download via yt-dlp (10% -> 60%)
                # Extract video IDs from ytmusicapi metadata - this ensures we only
                # download tracks that ytmusicapi knows about, avoiding non-music videos
                video_ids = [t.video_id for t in playlist_meta.tracks]

                download_wrapper = progress.create_download_wrapper(
                    playlist_meta.track_count,
                    PLAYLIST_PROGRESS_FETCH_DONE,
                    PLAYLIST_PROGRESS_DOWNLOAD_DONE,
                )

                progress.emit(
                    ProgressStep.DOWNLOADING,
                    f"Downloading {len(video_ids)} tracks...",
                    PLAYLIST_PROGRESS_FETCH_DONE,
                )

                download_result = self.downloader.download_tracks(
                    video_ids,
                    temp_path,
                    progress_callback=download_wrapper,
                    cancel_check=cancel.is_cancelled,
                )

                # Check for failure/cancellation
                if failure := self._handle_download_result(
                    download_result, album_info, progress
                ):
                    return failure

                # Files are already in order (matching video_ids sequence)
                downloaded_files = [Path(f) for f in download_result.downloaded_files]

                # Filter metadata to match only successfully downloaded files
                # Files are named "01 - Title.opus", track number = original index
                track_indices = self._extract_track_indices(downloaded_files)
                filtered_metadata = [
                    playlist_meta.tracks[i]
                    for i in track_indices
                    if i < len(playlist_meta.tracks)
                ]

                if len(filtered_metadata) != len(downloaded_files):
                    logger.warning(
                        "Metadata count mismatch: {} files, {} metadata entries",
                        len(downloaded_files),
                        len(filtered_metadata),
                    )

                progress.emit(
                    ProgressStep.DOWNLOADING,
                    f"Downloaded {len(downloaded_files)}/{len(video_ids)} tracks",
                    PLAYLIST_PROGRESS_DOWNLOAD_DONE,
                )

                # Phase 3: Patch metadata (60% -> 70%)
                progress.emit(
                    ProgressStep.IMPORTING,
                    "Patching track metadata...",
                    PLAYLIST_PROGRESS_DOWNLOAD_DONE,
                )

                self.patcher.patch_files(
                    file_paths=downloaded_files,
                    track_metadata=filtered_metadata,
                    playlist_name=playlist_meta.title,
                )

                progress.emit(
                    ProgressStep.IMPORTING,
                    "Metadata patched",
                    PLAYLIST_PROGRESS_PATCH_DONE,
                )

                # Phase 4: Organize files to Playlists/{name}/ (70% -> 75%)
                progress.emit(
                    ProgressStep.IMPORTING,
                    "Organizing files...",
                    PLAYLIST_PROGRESS_PATCH_DONE,
                )

                final_files = self.file_organizer.organize(
                    downloaded_files,
                    playlist_meta,
                )

                progress.emit(
                    ProgressStep.IMPORTING,
                    f"Files organized to {final_files[0].parent.name}/",
                    PLAYLIST_PROGRESS_ORGANIZE_DONE,
                )

                # Phase 5: Skip beets for playlists (metadata already patched)
                # TODO: Consider adding MusicBrainz enrichment without beets import
                progress.emit(
                    ProgressStep.IMPORTING,
                    "Metadata ready",
                    PLAYLIST_PROGRESS_BEETS_DONE,
                )

                # Phase 6: Generate M3U (90% -> 100%)
                playlist_dir = final_files[0].parent
                progress.emit(
                    ProgressStep.IMPORTING,
                    "Generating playlist file...",
                    PLAYLIST_PROGRESS_BEETS_DONE,
                )

                generate_m3u(
                    playlist_name=playlist_meta.title,
                    track_files=final_files,
                    track_metadata=playlist_meta.tracks,
                    output_dir=playlist_dir,
                )

                progress.complete(
                    f"Sync complete: {playlist_dir}",
                    str(playlist_dir),
                )

                return SyncResult(
                    success=True,
                    download_result=download_result,
                    album_info=album_info,
                    destination=str(playlist_dir),
                )

            except Exception as e:
                logger.exception("Playlist sync failed")
                progress.fail(str(e))
                return SyncResult(
                    success=False,
                    album_info=album_info,
                    error=str(e),
                )

    def _handle_download_result(
        self,
        download_result: DownloadResult,
        album_info: AlbumInfo | None,
        progress: ProgressEmitter,
    ) -> SyncResult | None:
        """Check download result and return SyncResult if complete failure.

        Returns None if processing should continue (full or partial success).
        Partial downloads (some files downloaded) are allowed to continue.
        """
        if download_result.cancelled:
            return SyncResult(
                success=False,
                download_result=download_result,
                album_info=album_info,
                error="Download cancelled",
            )

        # Allow partial downloads to continue if we have any files
        if not download_result.downloaded_files:
            progress.fail(download_result.error or "Download failed")
            return SyncResult(
                success=False,
                download_result=download_result,
                album_info=album_info,
                error=download_result.error or "Download failed",
            )

        return None

    @staticmethod
    def _extract_track_indices(files: list[Path]) -> list[int]:
        """Extract 0-based track indices from filenames.

        Files are named "01 - Title.opus", so track number 01 = index 0.
        """
        indices = []
        for f in files:
            match = _TRACK_NUM_PATTERN.match(f.name)
            if match:
                # Convert 1-based track number to 0-based index
                indices.append(int(match.group(1)) - 1)
            else:
                logger.warning("Could not extract track number from: {}", f.name)
        return indices
