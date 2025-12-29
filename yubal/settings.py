"""Application settings using pydantic-settings."""

import tempfile
from datetime import tzinfo
from functools import lru_cache
from pathlib import Path
from zoneinfo import ZoneInfo

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_ROOT = Path(__file__).parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="YUBAL_",
        env_file=_PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Server settings
    host: str = Field(default="127.0.0.1", description="Server host")
    port: int = Field(default=8000, description="Server port")
    reload: bool = Field(default=False, description="Enable auto-reload")
    debug: bool = Field(default=False, description="Enable debug mode")

    # Path settings
    data_dir: Path = Field(
        default=_PROJECT_ROOT / "data",
        description="Music library directory",
    )
    beets_dir: Path = Field(
        default=_PROJECT_ROOT / "beets",
        description="Beets directory",
    )
    ytdlp_dir: Path = Field(
        default=_PROJECT_ROOT / "ytdlp",
        description="yt-dlp config directory (cookies, etc.)",
    )

    # Audio settings (opus = best quality/size, no transcoding when source matches)
    audio_format: str = Field(default="opus", description="Audio format")
    audio_quality: str = Field(default="0", description="Audio quality (0 = best)")

    # Temp directory for job downloads (cleaned up on shutdown)
    temp_dir: Path = Field(
        default=Path(tempfile.gettempdir()) / "yubal",
        description="Temp directory for downloads",
    )

    # CORS settings
    cors_origins: list[str] = Field(default=["*"], description="Allowed CORS origins")

    # Timezone for timestamps (IANA format, e.g., "UTC", "America/New_York")
    tz: str = Field(default="UTC", description="Timezone for timestamps")

    @property
    def timezone(self) -> tzinfo:
        """Get timezone object from tz string."""
        return ZoneInfo(self.tz)

    @property
    def beets_config(self) -> Path:
        return self.beets_dir / "config.yaml"

    @property
    def beets_db(self) -> Path:
        return self.beets_dir / "beets.db"

    @property
    def library_dir(self) -> Path:
        return self.data_dir

    @property
    def cookies_file(self) -> Path:
        return self.ytdlp_dir / "cookies.txt"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
