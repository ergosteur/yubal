"""Tests for playlist utilities."""

from yubal.utils.playlist import is_album_playlist


class TestIsAlbumPlaylist:
    """Tests for is_album_playlist function."""

    def test_album_playlist_with_olak_prefix(self) -> None:
        """Should return True for playlist IDs starting with OLAK5uy_."""
        assert is_album_playlist("OLAK5uy_abc123def456") is True

    def test_album_playlist_with_minimal_olak_prefix(self) -> None:
        """Should return True even with minimal characters after prefix."""
        assert is_album_playlist("OLAK5uy_x") is True

    def test_album_playlist_exact_prefix_only(self) -> None:
        """Should return True for just the prefix (edge case)."""
        assert is_album_playlist("OLAK5uy_") is True

    def test_regular_playlist_with_pl_prefix(self) -> None:
        """Should return False for regular playlists starting with PL."""
        assert is_album_playlist("PLabc123def456") is False

    def test_regular_playlist_with_rdcl_prefix(self) -> None:
        """Should return False for radio playlists starting with RDCL."""
        assert is_album_playlist("RDCLabc123def456") is False

    def test_regular_playlist_random_id(self) -> None:
        """Should return False for arbitrary playlist IDs."""
        assert is_album_playlist("abc123xyz") is False

    def test_empty_string(self) -> None:
        """Should return False for empty string."""
        assert is_album_playlist("") is False

    def test_partial_prefix_olak(self) -> None:
        """Should return False for partial OLAK prefix."""
        assert is_album_playlist("OLAK") is False

    def test_partial_prefix_olak5(self) -> None:
        """Should return False for partial OLAK5 prefix."""
        assert is_album_playlist("OLAK5") is False

    def test_partial_prefix_olak5uy(self) -> None:
        """Should return False for partial OLAK5uy prefix (missing underscore)."""
        assert is_album_playlist("OLAK5uy") is False

    def test_case_sensitive_lowercase(self) -> None:
        """Should return False for lowercase prefix (case sensitive)."""
        assert is_album_playlist("olak5uy_abc123") is False

    def test_case_sensitive_mixed(self) -> None:
        """Should return False for mixed case prefix."""
        assert is_album_playlist("Olak5uy_abc123") is False

    def test_prefix_in_middle(self) -> None:
        """Should return False if prefix is not at the start."""
        assert is_album_playlist("xOLAK5uy_abc123") is False
