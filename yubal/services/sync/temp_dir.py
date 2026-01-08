"""Temporary directory management for sync operations."""

import shutil
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def job_temp_dir(base_temp_dir: Path, job_id: str) -> Iterator[Path]:
    """Context manager for job temporary directory with automatic cleanup.

    Creates a temporary directory for a job and ensures it's cleaned up
    when the context exits, regardless of success or failure.

    Args:
        base_temp_dir: Base directory for temporary files
        job_id: Unique job identifier (used as subdirectory name)

    Yields:
        Path to the job's temporary directory
    """
    job_dir = base_temp_dir / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    try:
        yield job_dir
    finally:
        if job_dir.exists():
            shutil.rmtree(job_dir, ignore_errors=True)
