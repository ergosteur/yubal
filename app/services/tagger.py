"""Music tagging and organization using beets CLI."""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import subprocess
import os


@dataclass
class TagResult:
    """Result of a tagging operation."""

    success: bool
    source_dir: Path
    dest_dir: Optional[Path] = None
    album_name: Optional[str] = None
    artist_name: Optional[str] = None
    track_count: int = 0
    error: Optional[str] = None
    stdout: str = ""
    stderr: str = ""


class Tagger:
    """Handles music tagging and organization via beets CLI."""

    def __init__(self, beets_config: Path, library_dir: Path, beets_db: Path):
        self.beets_config = beets_config
        self.library_dir = library_dir
        self.beets_db = beets_db

    def tag_album(self, source_dir: Path) -> TagResult:
        """
        Tag and organize an album using beets.

        Runs beets import in quiet mode to automatically tag
        and move files to the organized library.

        Args:
            source_dir: Directory containing downloaded audio files

        Returns:
            TagResult with success status and final location
        """
        # Check source directory has files
        audio_files = self._find_audio_files(source_dir)
        if not audio_files:
            return TagResult(
                success=False,
                source_dir=source_dir,
                error="No audio files found in source directory",
            )

        try:
            result = self._run_beets_import(source_dir)

            if result.returncode != 0:
                return TagResult(
                    success=False,
                    source_dir=source_dir,
                    error=f"Beets import failed: {result.stderr}",
                    stdout=result.stdout,
                    stderr=result.stderr,
                )

            # Find where the album was imported
            dest_dir = self._find_imported_album(source_dir)
            track_count = len(audio_files)

            return TagResult(
                success=True,
                source_dir=source_dir,
                dest_dir=dest_dir,
                track_count=track_count,
                stdout=result.stdout,
                stderr=result.stderr,
            )

        except subprocess.TimeoutExpired:
            return TagResult(
                success=False,
                source_dir=source_dir,
                error="Beets import timed out after 5 minutes",
            )
        except FileNotFoundError:
            return TagResult(
                success=False,
                source_dir=source_dir,
                error="Beets command not found. Please install beets: pip install beets",
            )
        except Exception as e:
            return TagResult(
                success=False,
                source_dir=source_dir,
                error=f"Unexpected error during tagging: {str(e)}",
            )

    def _run_beets_import(self, source_dir: Path) -> subprocess.CompletedProcess:
        """
        Execute beets import command.

        Uses quiet mode (-q) for non-interactive import.
        Uses move mode to relocate files to library.
        """
        # Set BEETSDIR to use our config
        env = os.environ.copy()
        env["BEETSDIR"] = str(self.beets_config.parent)

        cmd = [
            "beet",
            "--config",
            str(self.beets_config),
            "import",
            "-q",  # Quiet mode - no prompts
            str(source_dir),
        ]

        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            env=env,
            cwd=str(self.beets_config.parent.parent),  # Project root
        )

    def _find_audio_files(self, directory: Path) -> list[Path]:
        """Find all audio files in a directory."""
        audio_extensions = {".mp3", ".m4a", ".opus", ".ogg", ".flac", ".wav", ".aac"}
        return [
            f for f in directory.iterdir()
            if f.is_file() and f.suffix.lower() in audio_extensions
        ]

    def _find_imported_album(self, source_dir: Path) -> Optional[Path]:
        """
        Find where beets moved the album in the library.

        Since beets organizes by artist/album, we look for recently
        modified directories in the library.
        """
        if not self.library_dir.exists():
            return None

        # Find the most recently modified album directory
        newest_dir = None
        newest_time = 0

        for artist_dir in self.library_dir.iterdir():
            if not artist_dir.is_dir():
                continue
            for album_dir in artist_dir.iterdir():
                if not album_dir.is_dir():
                    continue
                mtime = album_dir.stat().st_mtime
                if mtime > newest_time:
                    newest_time = mtime
                    newest_dir = album_dir

        return newest_dir
