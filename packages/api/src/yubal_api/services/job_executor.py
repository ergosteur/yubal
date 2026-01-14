"""Job execution orchestration service."""

import asyncio
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from yubal_api.core.enums import JobStatus, ProgressStep
from yubal_api.core.models import AlbumInfo, Job
from yubal_api.services.protocols import JobExecutionStore
from yubal_api.services.sync.cancel import CancelToken
from yubal_api.services.sync_service import SyncService

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
        base_path: Path,
        audio_format: str = "opus",
        cookies_path: Path | None = None,
    ) -> None:
        self._job_store = job_store
        self._base_path = base_path
        self._audio_format = audio_format
        self._cookies_path = cookies_path

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
            if cancel_token.is_cancelled:
                return

            self._job_store.transition_job(
                job_id,
                JobStatus.FETCHING_INFO,
                f"Starting sync from: {url}",
                started_at=datetime.now(UTC),
            )

            # Create progress callback that updates job store
            loop = asyncio.get_running_loop()

            def on_progress(
                step: ProgressStep,
                message: str,
                progress: float | None,
                details: dict[str, Any] | None,
            ) -> None:
                if cancel_token.is_cancelled:
                    return

                status = self._step_to_status(step)
                album_info = self._parse_album_info(details) if details else None

                # Skip terminal states - handled by result
                if status in (JobStatus.COMPLETED, JobStatus.FAILED):
                    return

                loop.call_soon_threadsafe(
                    self._job_store.transition_job,
                    job_id,
                    status,
                    message,
                    progress,
                    album_info,
                )

            # Run sync in thread pool
            sync_service = SyncService(
                self._base_path, self._audio_format, self._cookies_path
            )
            result = await asyncio.to_thread(
                sync_service.execute,
                url,
                on_progress,
                cancel_token,
            )

            # Handle result
            if cancel_token.is_cancelled:
                self._job_store.transition_job(
                    job_id, JobStatus.CANCELLED, "Job cancelled by user"
                )
            elif result.success:
                self._job_store.transition_job(
                    job_id,
                    JobStatus.COMPLETED,
                    f"Sync complete: {result.destination}",
                    progress=PROGRESS_COMPLETE,
                    album_info=result.album_info,
                )
            else:
                self._job_store.transition_job(
                    job_id, JobStatus.FAILED, result.error or "Sync failed"
                )

        except Exception as e:
            self._job_store.transition_job(job_id, JobStatus.FAILED, str(e))

        finally:
            self._cancel_tokens.pop(job_id, None)
            self._start_next_pending()

    @staticmethod
    def _step_to_status(step: ProgressStep) -> JobStatus:
        """Map progress step to job status."""
        return {
            ProgressStep.FETCHING_INFO: JobStatus.FETCHING_INFO,
            ProgressStep.DOWNLOADING: JobStatus.DOWNLOADING,
            ProgressStep.IMPORTING: JobStatus.IMPORTING,
            ProgressStep.COMPLETED: JobStatus.COMPLETED,
            ProgressStep.FAILED: JobStatus.FAILED,
        }.get(step, JobStatus.DOWNLOADING)

    @staticmethod
    def _parse_album_info(details: dict[str, Any]) -> AlbumInfo | None:
        """Extract album info from details dict."""
        if data := details.get("album_info"):
            try:
                return AlbumInfo(**data)
            except Exception:
                pass
        return None

    def _start_next_pending(self) -> None:
        """Start the next pending job if any."""
        if next_job := self._job_store.pop_next_pending():
            self.start_job(next_job)
