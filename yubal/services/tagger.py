import os
import subprocess
import sys
from pathlib import Path

from loguru import logger

from yubal.core.callbacks import ProgressCallback, ProgressEvent
from yubal.core.enums import ProgressStep
from yubal.core.models import TagResult


class Tagger:
    """Handles music tagging and organization via beets CLI."""

    def __init__(self, beets_config: Path, library_dir: Path, beets_db: Path):
        self.beets_config = beets_config
        self.library_dir = library_dir
        self.beets_db = beets_db

    def _get_beet_command(self) -> list[str]:
        """Get the command to run beets using the current Python."""
        # Use python -m to avoid shebang issues with venv scripts
        return [sys.executable, "-m", "beets"]

    def _get_beets_env(self) -> dict[str, str]:
        """Get environment variables for running beets commands."""
        env = os.environ.copy()
        env["BEETSDIR"] = str(self.beets_config.parent)
        return env

    def tag_album(
        self,
        audio_files: list[Path],
        copy: bool = False,
        progress_callback: ProgressCallback | None = None,
    ) -> TagResult:
        """
        Tag and organize an album using beets.

        Runs beets import in quiet mode to automatically tag
        and move files to the organized library.

        Args:
            audio_files: List of audio file paths to import
            copy: If True, copy files instead of moving (originals stay)
            progress_callback: Optional callback for progress updates

        Returns:
            TagResult with success status and final location
        """
        if not audio_files:
            return TagResult(
                success=False,
                source_dir="",
                error="No audio files provided",
            )

        # All files should be in the same directory (temp dir from downloader)
        source_dir = audio_files[0].parent

        try:
            result = self._run_beets_import(
                source_dir, copy=copy, progress_callback=progress_callback
            )

            if result.returncode != 0:
                error_msg = f"Beets failed (code {result.returncode}): {result.stdout}"
                logger.error(error_msg)
                return TagResult(
                    success=False,
                    source_dir=str(source_dir),
                    error=error_msg,
                )

            # Find where the album was imported
            dest_dir = self._find_imported_album(source_dir)
            track_count = len(audio_files)

            return TagResult(
                success=True,
                source_dir=str(source_dir),
                dest_dir=str(dest_dir) if dest_dir else None,
                track_count=track_count,
            )

        except subprocess.TimeoutExpired:
            return TagResult(
                success=False,
                source_dir=str(source_dir),
                error="Beets import timed out after 5 minutes",
            )
        except FileNotFoundError as e:
            return TagResult(
                success=False,
                source_dir=str(source_dir),
                error=f"Beets module not found. Error: {e}",
            )
        except Exception as e:
            return TagResult(
                success=False,
                source_dir=str(source_dir),
                error=f"Unexpected error during tagging: {e!s}",
            )

    def _run_beets_import(
        self,
        source_dir: Path,
        copy: bool = False,
        progress_callback: ProgressCallback | None = None,
    ) -> subprocess.CompletedProcess[str]:
        """
        Execute beets import command.

        Uses quiet mode (-q) for non-interactive import.
        Uses move mode to relocate files to library (unless copy is True).
        """
        # Ensure library directory exists (beets prompts otherwise)
        self.library_dir.mkdir(parents=True, exist_ok=True)
        self.beets_db.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            *self._get_beet_command(),
            "--config",
            str(self.beets_config),
            "--directory",
            str(self.library_dir),
            "import",
            "-q",  # Quiet mode - non-interactive
        ]

        # --copy: copy files instead of moving (originals stay in place)
        if copy:
            cmd.append("--copy")

        cmd.append(str(source_dir))

        msg = f"Running beets: {' '.join(cmd)}"
        logger.info(msg)
        if progress_callback:
            progress_callback(
                ProgressEvent(
                    step=ProgressStep.IMPORTING,
                    message=msg,
                )
            )

        # Use Popen to stream output in real-time
        # Pipe stdin with newlines to auto-accept prompts (beets -q needs stdin open)
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Combine stderr into stdout
            text=True,
            env=self._get_beets_env(),
            cwd=str(self.beets_config.parent.parent),
        )
        if process.stdin is None or process.stdout is None:
            raise RuntimeError("Process pipes not available")
        # Send newlines to accept any prompts, then close stdin
        process.stdin.write("\n" * 10)
        process.stdin.close()

        stdout_lines = []
        for line in process.stdout:
            line = line.rstrip()
            if "error" in line.lower():
                logger.error("[beets] {}", line)
            else:
                logger.info("[beets] {}", line)
            if progress_callback:
                progress_callback(
                    ProgressEvent(
                        step=ProgressStep.IMPORTING,
                        message=f"[beets] {line}",
                    )
                )
            stdout_lines.append(line)

        process.wait(timeout=300)

        msg = f"Beets returncode: {process.returncode}"
        logger.info(msg)
        if progress_callback:
            progress_callback(
                ProgressEvent(
                    step=ProgressStep.IMPORTING,
                    message=msg,
                    details={"returncode": process.returncode},
                )
            )

        # Return a CompletedProcess-like result for compatibility
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=process.returncode,
            stdout="\n".join(stdout_lines),
            stderr="",
        )

    def _find_imported_album(self, source_dir: Path) -> Path | None:
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
