"""Job API schemas."""

from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, Field
from yubal import AudioCodec, is_supported_url

from yubal_api.core.models import Job


def validate_youtube_music_url(url: str) -> str:
    """Validate that the URL is supported by yubal.

    Uses yubal's is_supported_url() as the source of truth to ensure
    the API accepts exactly what yubal can process.
    """
    url = url.strip()
    if not is_supported_url(url):
        raise ValueError(
            "Invalid URL. Expected a YouTube Music playlist or track URL "
            "(e.g., https://music.youtube.com/playlist?list=... or "
            "https://music.youtube.com/watch?v=...)"
        )
    return url


YouTubeMusicUrl = Annotated[str, AfterValidator(validate_youtube_music_url)]


class CreateJobRequest(BaseModel):
    """Request to create a new sync job."""

    url: YouTubeMusicUrl = Field(
        description="YouTube Music playlist, album, or single track URL",
        examples=[
            "https://music.youtube.com/playlist?list=OLAK5uy_...",
            "https://music.youtube.com/watch?v=VIDEO_ID",
        ],
    )
    audio_format: AudioCodec | None = Field(
        default=None,
        description="Audio format for downloads. Uses server default if not set.",
    )
    max_items: int | None = Field(
        default=None,
        ge=1,
        le=10000,
        description="Maximum number of tracks to download",
    )


class JobsResponse(BaseModel):
    """Response for listing jobs."""

    jobs: list[Job]


class JobCreatedResponse(BaseModel):
    """Response when a job is created."""

    id: str
    message: Literal["Job created"] = "Job created"


class ClearJobsResponse(BaseModel):
    """Response when jobs are cleared."""

    cleared: int


class CancelJobResponse(BaseModel):
    """Response when a job is cancelled."""

    message: Literal["Job cancelled"] = "Job cancelled"
