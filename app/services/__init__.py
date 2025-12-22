"""Services module."""
from .downloader import Downloader, AlbumInfo, DownloadResult
from .tagger import Tagger, TagResult
from .pipeline import Pipeline, ProcessResult

__all__ = [
    "Downloader",
    "AlbumInfo",
    "DownloadResult",
    "Tagger",
    "TagResult",
    "Pipeline",
    "ProcessResult",
]
