"""Jobs API endpoints."""

import asyncio
from datetime import UTC, datetime

from fastapi import APIRouter, BackgroundTasks, HTTPException, status

from yubal.api.dependencies import AudioFormatDep, JobStoreDep, SyncServiceDep
from yubal.core.callbacks import ProgressEvent
from yubal.core.enums import JobStatus
from yubal.core.models import AlbumInfo
from yubal.schemas.jobs import (
    CancelJobResponse,
    ClearJobsResponse,
    CreateJobRequest,
    JobConflictError,
    JobCreatedResponse,
    JobListResponse,
)
from yubal.services.job_store import JobStore
from yubal.services.sync import SyncService

router = APIRouter()


async def run_sync_job(
    job_id: str,
    url: str,
    job_store: JobStore,
    sync_service: SyncService,
) -> None:
    """Background task that runs the sync operation."""
    # Check if cancelled before starting
    if job_store.is_cancelled(job_id):
        return

    # Update job to started (fetching info status)
    await job_store.update_job(
        job_id,
        status=JobStatus.FETCHING_INFO,
        started_at=datetime.now(UTC),
    )
    await job_store.add_log(job_id, "fetching_info", f"Starting sync from: {url}")

    # Capture the event loop BEFORE entering the thread
    loop = asyncio.get_running_loop()

    def cancel_check() -> bool:
        """Check if job has been cancelled."""
        return job_store.is_cancelled(job_id)

    def progress_callback(event: ProgressEvent) -> None:
        """Thread-safe callback that updates job state."""
        # Skip updates for cancelled jobs
        if job_store.is_cancelled(job_id):
            return

        # Map ProgressStep value to JobStatus enum
        status_map = {
            "fetching_info": JobStatus.FETCHING_INFO,
            "downloading": JobStatus.DOWNLOADING,
            "importing": JobStatus.IMPORTING,
            "completed": JobStatus.COMPLETED,
            "failed": JobStatus.FAILED,
        }

        new_status = status_map.get(event.step.value, JobStatus.DOWNLOADING)

        # Schedule async update using the captured loop
        loop.call_soon_threadsafe(
            lambda: asyncio.create_task(
                _update_job_from_event(job_id, new_status, event, job_store)
            )
        )

    try:
        result = await asyncio.to_thread(
            sync_service.sync_album,
            url,
            job_id,
            progress_callback,
            cancel_check,
        )

        # Check if job was cancelled
        if job_store.is_cancelled(job_id):
            await job_store.add_log(job_id, "cancelled", "Job cancelled by user")
            return

        # Update job with final result
        if result.success:
            # Build completion message
            if result.destination:
                complete_msg = f"Sync complete: {result.destination}"
            elif result.album_info:
                complete_msg = f"Sync complete: {result.album_info.title}"
            else:
                complete_msg = "Sync complete"

            await job_store.update_job(
                job_id,
                status=JobStatus.COMPLETED,
                progress=100.0,
                album_info=result.album_info,
            )
            await job_store.add_log(job_id, "completed", complete_msg)
        else:
            await job_store.update_job(
                job_id,
                status=JobStatus.FAILED,
            )
            await job_store.add_log(job_id, "failed", result.error or "Sync failed")

    except Exception as e:
        await job_store.update_job(
            job_id,
            status=JobStatus.FAILED,
        )
        await job_store.add_log(job_id, "failed", str(e))

    # Start next pending job if any (fire-and-forget, no blocking)
    next_job = await job_store.pop_next_pending()
    if next_job:
        task = asyncio.create_task(
            run_sync_job(next_job.id, next_job.url, job_store, sync_service)
        )
        del task  # Fire-and-forget


async def _update_job_from_event(
    job_id: str, new_status: JobStatus, event: ProgressEvent, job_store: JobStore
) -> None:
    """Helper to update job from progress event."""
    # Don't update cancelled jobs - prevents race condition with status overwrite
    if job_store.is_cancelled(job_id):
        return

    # Skip completed/failed from callback - final result handles those
    if event.step.value in ("completed", "failed"):
        return

    # Parse album_info if provided as dict (from FETCHING_INFO event)
    details = event.details or {}
    album_info_data = details.get("album_info")
    album_info = None
    if album_info_data and isinstance(album_info_data, dict):
        try:
            album_info = AlbumInfo(**album_info_data)
        except Exception:  # noqa: S110
            pass  # Ignore invalid album_info - non-critical data

    await job_store.update_job(
        job_id,
        status=new_status,
        progress=event.progress if event.progress is not None else None,
        album_info=album_info,
    )
    await job_store.add_log(job_id, event.step.value, event.message)


@router.post(
    "/jobs",
    response_model=JobCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": JobConflictError, "description": "Queue is full"}},
)
async def create_job(
    request: CreateJobRequest,
    background_tasks: BackgroundTasks,
    audio_format: AudioFormatDep,
    job_store: JobStoreDep,
    sync_service: SyncServiceDep,
) -> JobCreatedResponse:
    """
    Create a new sync job.

    Jobs are queued and executed sequentially. Returns 409 only if queue is full.
    """
    result = await job_store.create_job(request.url, audio_format)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "Queue is full", "active_job_id": None},
        )

    job, should_start = result

    if should_start:
        background_tasks.add_task(
            run_sync_job,
            job.id,
            request.url,
            job_store,
            sync_service,
        )

    return JobCreatedResponse(id=job.id)


@router.get("/jobs", response_model=JobListResponse)
async def list_jobs(job_store: JobStoreDep) -> JobListResponse:
    """
    List all jobs (oldest first, FIFO order).

    Returns up to 50 jobs with their current status and all logs.
    """
    jobs = await job_store.get_all_jobs()
    logs = await job_store.get_all_logs()

    return JobListResponse(jobs=jobs, logs=logs)


@router.post("/jobs/{job_id}/cancel", response_model=CancelJobResponse)
async def cancel_job(
    job_id: str, job_store: JobStoreDep, sync_service: SyncServiceDep
) -> CancelJobResponse:
    """
    Cancel a running or queued job.

    Returns 404 if job not found, 409 if job already finished.
    """
    job = await job_store.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found",
        )

    if job.status.is_finished:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Job already finished",
        )

    success = await job_store.cancel_job(job_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not cancel job",
        )

    # Start next pending job if any
    next_job = await job_store.pop_next_pending()
    if next_job:
        task = asyncio.create_task(
            run_sync_job(next_job.id, next_job.url, job_store, sync_service)
        )
        del task  # Fire-and-forget

    return CancelJobResponse()


@router.delete("/jobs", response_model=ClearJobsResponse)
async def clear_jobs(job_store: JobStoreDep) -> ClearJobsResponse:
    """
    Clear all completed/failed jobs.

    Running jobs are not affected.
    """
    count = await job_store.clear_completed()
    return ClearJobsResponse(cleared=count)


@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(job_id: str, job_store: JobStoreDep) -> None:
    """
    Delete a completed, failed, or cancelled job.

    Running jobs cannot be deleted (returns 409).
    """
    job = await job_store.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found",
        )

    if not job.status.is_finished:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete a running job",
        )

    await job_store.delete_job(job_id)
