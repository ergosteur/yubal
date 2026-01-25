"""Jobs API endpoints.

Handles job lifecycle: creation, listing, cancellation, and deletion.
Jobs are processed sequentially in FIFO order.
"""

from fastapi import APIRouter, status

from yubal_api.api.dependencies import (
    AudioFormatDep,
    JobExecutorDep,
    JobStoreDep,
)
from yubal_api.api.exceptions import (
    ErrorResponse,
    JobConflictError,
    JobNotFoundError,
    QueueFullError,
)
from yubal_api.core.models import Job
from yubal_api.schemas.jobs import (
    CancelJobResponse,
    ClearJobsResponse,
    CreateJobRequest,
    JobCreatedResponse,
    JobsResponse,
)
from yubal_api.services.job_store import JobStore

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _get_job_or_raise(job_store: JobStore, job_id: str) -> Job:
    """Get job by ID or raise JobNotFoundError."""
    if not (job := job_store.get(job_id)):
        raise JobNotFoundError(job_id)
    return job


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": ErrorResponse, "description": "Queue is full"}},
)
async def create_job(
    request: CreateJobRequest,
    audio_format: AudioFormatDep,
    job_store: JobStoreDep,
    job_executor: JobExecutorDep,
) -> JobCreatedResponse:
    """Create a new sync job.

    Jobs are queued and executed sequentially. Returns 409 if queue is full.
    """
    result = job_store.create(request.url, audio_format, request.max_items)

    if result is None:
        raise QueueFullError()

    job, should_start = result

    if should_start:
        job_executor.start_job(job)

    return JobCreatedResponse(id=job.id)


@router.get("")
async def list_jobs(job_store: JobStoreDep) -> JobsResponse:
    """List all jobs (oldest first, FIFO order)."""
    jobs = job_store.get_all()
    return JobsResponse(jobs=jobs)


@router.post(
    "/{job_id}/cancel",
    responses={
        404: {"model": ErrorResponse, "description": "Job not found"},
        409: {"model": ErrorResponse, "description": "Job already finished"},
    },
)
async def cancel_job(
    job_id: str,
    job_store: JobStoreDep,
    job_executor: JobExecutorDep,
) -> CancelJobResponse:
    """Cancel a running or queued job."""
    job = _get_job_or_raise(job_store, job_id)

    if job.status.is_finished:
        raise JobConflictError("Job already finished", job_id=job_id)

    # Signal cancellation via cancel token if job is running
    job_executor.cancel_job(job_id)

    success = job_store.cancel(job_id)
    if not success:
        raise JobConflictError("Could not cancel job", job_id=job_id)

    return CancelJobResponse()


@router.delete("")
async def clear_jobs(job_store: JobStoreDep) -> ClearJobsResponse:
    """Clear all completed/failed/cancelled jobs.

    Running and queued jobs are not affected.
    """
    count = job_store.clear_finished()
    return ClearJobsResponse(cleared=count)


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": ErrorResponse, "description": "Job not found"},
        409: {"model": ErrorResponse, "description": "Cannot delete running job"},
    },
)
async def delete_job(job_id: str, job_store: JobStoreDep) -> None:
    """Delete a completed, failed, or cancelled job.

    Running or queued jobs cannot be deleted.
    """
    job = _get_job_or_raise(job_store, job_id)

    if not job.status.is_finished:
        raise JobConflictError("Cannot delete a running or queued job", job_id=job_id)

    job_store.delete(job_id)
