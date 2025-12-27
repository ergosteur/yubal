"""Job API schemas."""

from pydantic import BaseModel

from yubal.core.models import Job, LogEntry


class CreateJobRequest(BaseModel):
    """Request to create a new sync job."""

    url: str
    audio_format: str = "mp3"


class JobListResponse(BaseModel):
    """Response for listing jobs."""

    jobs: list[Job]
    logs: list[LogEntry] = []


class JobCreatedResponse(BaseModel):
    """Response when a job is created."""

    id: str
    message: str = "Job created"


class JobConflictError(BaseModel):
    """Error response when job creation is rejected."""

    error: str = "A job is already running"
    active_job_id: str | None = None


class ClearJobsResponse(BaseModel):
    """Response when jobs are cleared."""

    cleared: int


class CancelJobResponse(BaseModel):
    """Response when a job is cancelled."""

    message: str = "Job cancelled"
