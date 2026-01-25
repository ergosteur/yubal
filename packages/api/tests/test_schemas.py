"""Tests for API schemas."""

import pytest
from pydantic import ValidationError
from yubal_api.schemas.jobs import CreateJobRequest, validate_youtube_music_url


class TestValidateYouTubeMusicUrl:
    """Tests for YouTube Music URL validation."""

    # Valid playlist URLs
    def test_accepts_music_youtube_playlist(self) -> None:
        """Should accept YouTube Music playlist URL."""
        url = "https://music.youtube.com/playlist?list=OLAK5uy_test123"
        assert validate_youtube_music_url(url) == url

    def test_accepts_youtube_playlist(self) -> None:
        """Should accept standard YouTube playlist URL."""
        url = "https://www.youtube.com/playlist?list=PLtest123"
        assert validate_youtube_music_url(url) == url

    def test_accepts_music_youtube_browse(self) -> None:
        """Should accept YouTube Music browse URL."""
        url = "https://music.youtube.com/browse/MPREb_test123"
        assert validate_youtube_music_url(url) == url

    # Valid single track URLs
    def test_accepts_music_youtube_watch(self) -> None:
        """Should accept YouTube Music single track URL."""
        url = "https://music.youtube.com/watch?v=Vgpv5PtWsn4"
        assert validate_youtube_music_url(url) == url

    def test_accepts_youtube_watch(self) -> None:
        """Should accept standard YouTube single track URL."""
        url = "https://www.youtube.com/watch?v=GkTWxDB21cA"
        assert validate_youtube_music_url(url) == url

    def test_accepts_youtube_watch_without_www(self) -> None:
        """Should accept YouTube watch URL without www."""
        url = "https://youtube.com/watch?v=GkTWxDB21cA"
        assert validate_youtube_music_url(url) == url

    def test_accepts_watch_with_extra_params(self) -> None:
        """Should accept watch URL with extra parameters."""
        url = "https://music.youtube.com/watch?v=abc123&si=xyz789"
        assert validate_youtube_music_url(url) == url

    def test_accepts_watch_with_list_param(self) -> None:
        """Should accept watch URL with list param (treated as playlist by backend)."""
        url = "https://music.youtube.com/watch?v=abc123&list=PLtest123"
        assert validate_youtube_music_url(url) == url

    # Invalid URLs
    def test_rejects_random_url(self) -> None:
        """Should reject non-YouTube URLs."""
        with pytest.raises(ValueError, match="Invalid URL"):
            validate_youtube_music_url("https://example.com/test")

    def test_rejects_empty_url(self) -> None:
        """Should reject empty URLs."""
        with pytest.raises(ValueError, match="Invalid URL"):
            validate_youtube_music_url("")

    def test_rejects_youtube_homepage(self) -> None:
        """Should reject YouTube homepage."""
        with pytest.raises(ValueError, match="Invalid URL"):
            validate_youtube_music_url("https://music.youtube.com/")

    def test_rejects_watch_without_video_id(self) -> None:
        """Should reject watch URL without video ID."""
        with pytest.raises(ValueError, match="Invalid URL"):
            validate_youtube_music_url("https://music.youtube.com/watch")

    def test_strips_whitespace(self) -> None:
        """Should strip whitespace from URL."""
        url = "  https://music.youtube.com/watch?v=abc123  "
        assert validate_youtube_music_url(url) == url.strip()


class TestCreateJobRequest:
    """Tests for CreateJobRequest schema."""

    def test_valid_playlist_url(self) -> None:
        """Should accept valid playlist URL."""
        request = CreateJobRequest(
            url="https://music.youtube.com/playlist?list=OLAK5uy_test123"
        )
        assert request.url == "https://music.youtube.com/playlist?list=OLAK5uy_test123"

    def test_valid_single_track_url(self) -> None:
        """Should accept valid single track URL."""
        request = CreateJobRequest(url="https://music.youtube.com/watch?v=Vgpv5PtWsn4")
        assert request.url == "https://music.youtube.com/watch?v=Vgpv5PtWsn4"

    def test_invalid_url_raises_validation_error(self) -> None:
        """Should raise ValidationError for invalid URL."""
        with pytest.raises(ValidationError) as exc_info:
            CreateJobRequest(url="https://example.com/test")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("url",)
        assert "Invalid URL" in str(errors[0]["msg"])

    def test_max_items_optional(self) -> None:
        """Should allow max_items to be omitted."""
        request = CreateJobRequest(
            url="https://music.youtube.com/watch?v=abc123"
        )
        assert request.max_items is None

    def test_max_items_valid_range(self) -> None:
        """Should accept max_items within valid range."""
        request = CreateJobRequest(
            url="https://music.youtube.com/watch?v=abc123",
            max_items=10,
        )
        assert request.max_items == 10

    def test_max_items_minimum(self) -> None:
        """Should reject max_items less than 1."""
        with pytest.raises(ValidationError):
            CreateJobRequest(
                url="https://music.youtube.com/watch?v=abc123",
                max_items=0,
            )

    def test_max_items_maximum(self) -> None:
        """Should reject max_items greater than 10000."""
        with pytest.raises(ValidationError):
            CreateJobRequest(
                url="https://music.youtube.com/watch?v=abc123",
                max_items=10001,
            )
