"""Tests for cover art fetching."""

from unittest.mock import MagicMock, patch

import pytest

from ytmeta.utils.cover import clear_cover_cache, fetch_cover, get_cover_cache_size


@pytest.fixture(autouse=True)
def clear_cache() -> None:
    """Clear cover cache before each test."""
    clear_cover_cache()


class TestFetchCover:
    """Tests for fetch_cover function."""

    def test_returns_none_for_none_url(self) -> None:
        """Should return None when URL is None."""
        result = fetch_cover(None)
        assert result is None

    def test_returns_none_for_empty_url(self) -> None:
        """Should return None when URL is empty."""
        result = fetch_cover("")
        assert result is None

    def test_fetches_cover_successfully(self) -> None:
        """Should fetch and return cover bytes."""
        mock_response = MagicMock()
        mock_response.read.return_value = b"fake image data"
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch(
            "ytmeta.utils.cover.urllib.request.urlopen", return_value=mock_response
        ):
            result = fetch_cover("https://example.com/cover.jpg")

        assert result == b"fake image data"

    def test_caches_cover(self) -> None:
        """Should cache fetched cover and return from cache on second call."""
        mock_response = MagicMock()
        mock_response.read.return_value = b"cached image"
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch(
            "ytmeta.utils.cover.urllib.request.urlopen", return_value=mock_response
        ) as mock_urlopen:
            # First call - fetches
            result1 = fetch_cover("https://example.com/cover.jpg")
            # Second call - should use cache
            result2 = fetch_cover("https://example.com/cover.jpg")

        assert result1 == b"cached image"
        assert result2 == b"cached image"
        # urlopen should only be called once
        assert mock_urlopen.call_count == 1

    def test_different_urls_not_cached_together(self) -> None:
        """Should cache different URLs separately."""
        mock_response1 = MagicMock()
        mock_response1.read.return_value = b"image 1"
        mock_response1.__enter__ = MagicMock(return_value=mock_response1)
        mock_response1.__exit__ = MagicMock(return_value=False)

        mock_response2 = MagicMock()
        mock_response2.read.return_value = b"image 2"
        mock_response2.__enter__ = MagicMock(return_value=mock_response2)
        mock_response2.__exit__ = MagicMock(return_value=False)

        with patch("ytmeta.utils.cover.urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = [mock_response1, mock_response2]
            result1 = fetch_cover("https://example.com/cover1.jpg")
            result2 = fetch_cover("https://example.com/cover2.jpg")

        assert result1 == b"image 1"
        assert result2 == b"image 2"
        assert mock_urlopen.call_count == 2

    def test_handles_http_error(self) -> None:
        """Should return None on HTTP error."""
        from urllib.error import HTTPError

        with patch("ytmeta.utils.cover.urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = HTTPError(
                "https://example.com/cover.jpg", 404, "Not Found", {}, None
            )
            result = fetch_cover("https://example.com/cover.jpg")

        assert result is None

    def test_handles_url_error(self) -> None:
        """Should return None on URL error."""
        from urllib.error import URLError

        with patch("ytmeta.utils.cover.urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = URLError("Connection refused")
            result = fetch_cover("https://example.com/cover.jpg")

        assert result is None

    def test_handles_timeout(self) -> None:
        """Should return None on timeout."""
        with patch("ytmeta.utils.cover.urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = TimeoutError("Connection timed out")
            result = fetch_cover("https://example.com/cover.jpg")

        assert result is None


class TestClearCoverCache:
    """Tests for clear_cover_cache function."""

    def test_clears_cache(self) -> None:
        """Should clear all cached covers."""
        mock_response = MagicMock()
        mock_response.read.return_value = b"image"
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch(
            "ytmeta.utils.cover.urllib.request.urlopen", return_value=mock_response
        ):
            fetch_cover("https://example.com/cover.jpg")
            assert get_cover_cache_size() == 1

            clear_cover_cache()
            assert get_cover_cache_size() == 0


class TestGetCoverCacheSize:
    """Tests for get_cover_cache_size function."""

    def test_returns_zero_when_empty(self) -> None:
        """Should return 0 for empty cache."""
        assert get_cover_cache_size() == 0

    def test_returns_correct_count(self) -> None:
        """Should return correct number of cached items."""
        mock_response = MagicMock()
        mock_response.read.return_value = b"image"
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch(
            "ytmeta.utils.cover.urllib.request.urlopen", return_value=mock_response
        ):
            fetch_cover("https://example.com/cover1.jpg")
            assert get_cover_cache_size() == 1

            fetch_cover("https://example.com/cover2.jpg")
            assert get_cover_cache_size() == 2
