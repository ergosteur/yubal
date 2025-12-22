"""Application configuration and paths."""
from pathlib import Path
from dataclasses import dataclass, field
import os


@dataclass
class Settings:
    """Application settings with sensible defaults."""

    # Base paths
    BASE_DIR: Path = field(default_factory=lambda: Path(__file__).parent.parent)

    @property
    def DATA_DIR(self) -> Path:
        return self.BASE_DIR / "data"

    @property
    def DOWNLOAD_DIR(self) -> Path:
        return self.DATA_DIR / "downloads"

    @property
    def LIBRARY_DIR(self) -> Path:
        return self.DATA_DIR / "library"

    @property
    def BEETS_DB(self) -> Path:
        return self.DATA_DIR / "beets.db"

    @property
    def BEETS_CONFIG(self) -> Path:
        return self.BASE_DIR / "config" / "beets_config.yaml"

    # yt-dlp settings
    AUDIO_FORMAT: str = "mp3"
    AUDIO_QUALITY: str = "0"  # 0 = best quality (VBR)

    # URL validation
    ALLOWED_DOMAINS: tuple = (
        "youtube.com",
        "www.youtube.com",
        "music.youtube.com",
        "youtu.be",
    )

    # Flask settings
    SECRET_KEY: str = field(
        default_factory=lambda: os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
    )
    DEBUG: bool = field(
        default_factory=lambda: os.environ.get("FLASK_DEBUG", "1") == "1"
    )


settings = Settings()
