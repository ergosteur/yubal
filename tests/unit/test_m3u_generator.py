"""Tests for M3U playlist generator."""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from yubal.services.m3u_generator import generate_m3u, sanitize_filename
from yubal.services.metadata_enricher import TrackMetadata


class TestSanitizeFilename:
    """Tests for sanitize_filename function."""

    @pytest.mark.parametrize(
        ("input_name", "expected"),
        [
            # Removes invalid characters
            ('Test<>:"/\\|?*Name', "TestName"),
            # Strips whitespace
            ("  Test Name  ", "Test Name"),
            # Removes leading dots (prevents hidden files)
            (".hidden", "hidden"),
            ("...dots", "dots"),
            # Path traversal prevention
            ("../../../etc/passwd", "etcpasswd"),
            ("..\\..\\windows", "windows"),
            # Preserves valid characters
            ("Valid Name 123 (Remix)", "Valid Name 123 (Remix)"),
        ],
    )
    def test_sanitizes_filenames(self, input_name: str, expected: str) -> None:
        assert sanitize_filename(input_name) == expected

    def test_truncates_long_names(self) -> None:
        long_name = "x" * 150
        result = sanitize_filename(long_name)
        assert len(result) == 100

    @pytest.mark.parametrize(
        "input_name",
        [
            "<>:",  # Only special characters
            "   ",  # Only whitespace
            "",  # Empty string
        ],
    )
    def test_returns_untitled_for_empty_result(self, input_name: str) -> None:
        assert sanitize_filename(input_name) == "untitled"


class TestGenerateM3u:
    """Tests for generate_m3u function."""

    def _make_track(
        self, video_id: str, title: str, artist: str, track_number: int
    ) -> TrackMetadata:
        return TrackMetadata(
            video_id=video_id,
            title=title,
            artist=artist,
            album="Test Album",
            thumbnail_url=None,
            track_number=track_number,
            is_available=True,
        )

    def test_generates_valid_m3u(self) -> None:
        with TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            track_files = [
                output_dir / "01 - Artist - Song One.opus",
                output_dir / "02 - Artist - Song Two.opus",
            ]
            # Create the files
            for f in track_files:
                f.touch()

            track_metadata = [
                self._make_track("id1", "Song One", "Artist", 1),
                self._make_track("id2", "Song Two", "Artist", 2),
            ]

            result = generate_m3u(
                playlist_name="Test Playlist",
                track_files=track_files,
                track_metadata=track_metadata,
                output_dir=output_dir,
            )

            assert result.exists()
            assert result.name == "Test Playlist.m3u"

            content = result.read_text()
            assert "#EXTM3U" in content
            assert "#PLAYLIST:Test Playlist" in content
            assert "#EXTINF:-1,Artist - Song One" in content
            assert "01 - Artist - Song One.opus" in content

    def test_handles_mismatched_counts_gracefully(self) -> None:
        """When file count doesn't match metadata, generate M3U with available pairs."""
        with TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            track_files = [
                output_dir / "01 - Artist - Song.opus",
                output_dir / "02 - Artist - Song2.opus",
            ]
            # Create the files
            for f in track_files:
                f.touch()

            track_metadata = [
                self._make_track("id1", "Song", "Artist", 1),
                # Missing second metadata - will be skipped
            ]

            # Should not raise, just log warning and generate with 1 track
            result = generate_m3u(
                playlist_name="Test",
                track_files=track_files,
                track_metadata=track_metadata,
                output_dir=output_dir,
            )

            assert result.exists()
            content = result.read_text()
            # Only one EXTINF entry (matched pair)
            assert content.count("#EXTINF") == 1
            assert "Artist - Song" in content

    def test_sanitizes_playlist_name(self) -> None:
        with TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            track_files = [output_dir / "track.opus"]
            track_files[0].touch()
            track_metadata = [self._make_track("id1", "Song", "Artist", 1)]

            result = generate_m3u(
                playlist_name="Invalid<>Name:Here",
                track_files=track_files,
                track_metadata=track_metadata,
                output_dir=output_dir,
            )

            assert result.name == "InvalidNameHere.m3u"

    def test_handles_empty_playlist_name(self) -> None:
        with TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            track_files = [output_dir / "track.opus"]
            track_files[0].touch()
            track_metadata = [self._make_track("id1", "Song", "Artist", 1)]

            result = generate_m3u(
                playlist_name="",
                track_files=track_files,
                track_metadata=track_metadata,
                output_dir=output_dir,
            )

            assert result.name == "untitled.m3u"
