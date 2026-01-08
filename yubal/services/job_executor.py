"""Job execution orchestration service."""

import asyncio
from datetime import UTC, datetime
from typing import Any

from yubal.core.callbacks import ProgressCallback, ProgressEvent
from yubal.core.enums import ImportType, JobStatus
from yubal.core.models import AlbumInfo, Job, SyncResult
from yubal.core.utils import detect_import_type
from yubal.services.protocols import JobExecutionStore
from yubal.services.sync import (
    AlbumSyncService,
    CallbackProgressEmitter,
    CancelToken,
    PlaylistSyncService,
)

PROGRESS_COMPLETE = 100.0


class JobExecutor:
    """Orchestrates job execution lifecycle.

    Manages:
    - Background task tracking (prevents GC)
    - Cancel token registry
    - Job queue continuation
    - Progress callback wiring

    Uses JobExecutionStore protocol for persistence (narrow interface).
    CancelToken is the single source of truth for cancellation signaling.
    """

    def __init__(
        self,
        job_store: JobExecutionStore,
        album_sync_service: AlbumSyncService,
        playlist_sync_service: PlaylistSyncService,
    ) -> None:
        self._job_store = job_store
        self._album_sync_service = album_sync_service
        self._playlist_sync_service = playlist_sync_service

        # Internal state
        self._background_tasks: set[asyncio.Task[Any]] = set()
        self._cancel_tokens: dict[str, CancelToken] = {}

    def start_job(self, job: Job) -> None:
        """Start a job as a background task with proper cleanup."""
        task = asyncio.create_task(self._run_job(job.id, job.url))
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)

    def cancel_job(self, job_id: str) -> bool:
        """Signal cancellation for a running job.

        Returns True if a cancel token existed (job was running).
        """
        if job_id in self._cancel_tokens:
            self._cancel_tokens[job_id].cancel()
            return True
        return False

    async def _run_job(self, job_id: str, url: str) -> None:
        """Background task that runs the sync operation."""
        cancel_token = CancelToken()
        self._cancel_tokens[job_id] = cancel_token

        try:
            # Check cancellation before starting (CancelToken is single source of truth)
            if cancel_token.is_cancelled():
                return

            self._job_store.transition_job(
                job_id,
                JobStatus.FETCHING_INFO,
                f"Starting sync from: {url}",
                started_at=datetime.now(UTC),
            )

            progress_callback = self._create_progress_callback(job_id, cancel_token)
            progress_emitter = CallbackProgressEmitter(progress_callback)

            import_type = detect_import_type(url)
            sync_service = (
                self._album_sync_service
                if import_type == ImportType.ALBUM
                else self._playlist_sync_service
            )

            result = await asyncio.to_thread(
                sync_service.execute,
                url,
                job_id,
                progress_emitter,
                cancel_token,
            )

            if cancel_token.is_cancelled():
                self._job_store.transition_job(
                    job_id, JobStatus.CANCELLED, "Job cancelled by user"
                )
                return

            self._finalize_job(job_id, result)

        except Exception as e:
            self._job_store.transition_job(job_id, JobStatus.FAILED, str(e))

        finally:
            self._cancel_tokens.pop(job_id, None)
            self._start_next_pending()

    def _create_progress_callback(
        self, job_id: str, cancel_token: CancelToken
    ) -> ProgressCallback:
        """Create thread-safe progress callback for a job.

        Progress updates from worker threads are scheduled on the event loop.
        """
        loop = asyncio.get_running_loop()

        def callback(event: ProgressEvent) -> None:
            # CancelToken is single source of truth for cancellation
            if cancel_token.is_cancelled():
                return

            # Schedule the update on the event loop (thread-safe)
            loop.call_soon_threadsafe(
                self._update_job_from_event, job_id, event, cancel_token
            )

        return callback

    @staticmethod
    def _map_event_to_status(event: ProgressEvent) -> JobStatus:
        """Map progress event step to job status."""
        status_map = {
            "fetching_info": JobStatus.FETCHING_INFO,
            "downloading": JobStatus.DOWNLOADING,
            "importing": JobStatus.IMPORTING,
            "completed": JobStatus.COMPLETED,
            "failed": JobStatus.FAILED,
        }
        return status_map.get(event.step.value, JobStatus.DOWNLOADING)

    def _update_job_from_event(
        self,
        job_id: str,
        event: ProgressEvent,
        cancel_token: CancelToken,
    ) -> None:
        """Update job state from progress event. Called from event loop."""
        if cancel_token.is_cancelled():
            return

        # Skip completed/failed from callback - final result handles those
        if event.step.value in ("completed", "failed"):
            return

        new_status = self._map_event_to_status(event)
        album_info = self._parse_album_info(event)

        self._job_store.transition_job(
            job_id,
            new_status,
            event.message,
            progress=event.progress if event.progress is not None else None,
            album_info=album_info,
        )

    @staticmethod
    def _parse_album_info(event: ProgressEvent) -> AlbumInfo | None:
        """Extract album info from event details if present."""
        details = event.details or {}
        album_info_data = details.get("album_info")
        if album_info_data and isinstance(album_info_data, dict):
            try:
                return AlbumInfo(**album_info_data)
            except Exception:  # noqa: S110
                pass
        return None

    def _finalize_job(self, job_id: str, result: SyncResult) -> None:
        """Update job with final sync result."""
        if result.success:
            if result.destination:
                complete_msg = f"Sync complete: {result.destination}"
            elif result.album_info:
                complete_msg = f"Sync complete: {result.album_info.title}"
            else:
                complete_msg = "Sync complete"

            self._job_store.transition_job(
                job_id,
                JobStatus.COMPLETED,
                complete_msg,
                progress=PROGRESS_COMPLETE,
                album_info=result.album_info,
            )
        else:
            self._job_store.transition_job(
                job_id, JobStatus.FAILED, result.error or "Sync failed"
            )

    def _start_next_pending(self) -> None:
        """Start the next pending job if any."""
        if next_job := self._job_store.pop_next_pending():
            self.start_job(next_job)
