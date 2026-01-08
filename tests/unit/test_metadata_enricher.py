"""Tests for MetadataEnricher class."""

from unittest.mock import MagicMock, patch

from yubal.services.metadata_enricher import (
    MetadataEnricher,
    PlaylistMetadata,
    TrackMetadata,
)


class TestMetadataEnricher:
    """Tests for MetadataEnricher class."""

    @patch("yubal.services.metadata_enricher.YTMusic")
    def test_get_playlist_returns_metadata(self, mock_ytmusic_class: MagicMock) -> None:
        mock_yt = mock_ytmusic_class.return_value
        mock_yt.get_playlist.return_value = {
            "title": "Test Playlist",
            "tracks": [
                {
                    "videoId": "abc123",
                    "title": "Test Song",
                    "artists": [{"name": "Test Artist"}],
                    "album": {"id": "album123", "name": "Test Album"},
                    "isAvailable": True,
                    "thumbnails": [{"url": "http://example.com/thumb.jpg"}],
                }
            ],
        }

        enricher = MetadataEnricher(request_delay=0)
        result = enricher.get_playlist("PLxxx123")

        assert isinstance(result, PlaylistMetadata)
        assert result.title == "Test Playlist"
        assert result.playlist_id == "PLxxx123"
        assert result.track_count == 1
        assert len(result.tracks) == 1

        track = result.tracks[0]
        assert track.video_id == "abc123"
        assert track.title == "Test Song"
        assert track.artist == "Test Artist"
        assert track.album == "Test Album"
        assert track.track_number == 1
        assert track.is_available is True

    @patch("yubal.services.metadata_enricher.YTMusic")
    def test_get_playlist_skips_unavailable_tracks(
        self, mock_ytmusic_class: MagicMock
    ) -> None:
        mock_yt = mock_ytmusic_class.return_value
        mock_yt.get_playlist.return_value = {
            "title": "Mixed Playlist",
            "tracks": [
                {
                    "videoId": "available1",
                    "title": "Available Track",
                    "artists": [{"name": "Artist"}],
                    "album": {"id": "album1", "name": "Album"},
                    "isAvailable": True,
                    "thumbnails": [],
                },
                {
                    "videoId": "unavailable",
                    "title": "Unavailable Track",
                    "artists": [{"name": "Artist"}],
                    "isAvailable": False,
                    "thumbnails": [],
                },
                {
                    "videoId": None,  # No video ID
                    "title": "No ID Track",
                    "artists": [{"name": "Artist"}],
                    "isAvailable": True,
                    "thumbnails": [],
                },
            ],
        }

        enricher = MetadataEnricher(request_delay=0)
        result = enricher.get_playlist("PLxxx")

        # Only the first track should be included
        assert result.track_count == 1
        assert result.tracks[0].video_id == "available1"

    @patch("yubal.services.metadata_enricher.YTMusic")
    def test_get_playlist_searches_for_album_when_missing(
        self, mock_ytmusic_class: MagicMock
    ) -> None:
        mock_yt = mock_ytmusic_class.return_value
        mock_yt.get_playlist.return_value = {
            "title": "Music Video Playlist",
            "tracks": [
                {
                    "videoId": "mv123",
                    "title": "Hit Song",
                    "artists": [{"name": "Popular Artist"}],
                    "album": None,  # No album (music video)
                    "isAvailable": True,
                    "thumbnails": [],
                }
            ],
        }
        mock_yt.search.return_value = [
            {
                "artists": [{"name": "Popular Artist"}],
                "album": {"name": "Greatest Hits"},
                "thumbnails": [{"url": "http://example.com/album.jpg"}],
            }
        ]

        enricher = MetadataEnricher(request_delay=0)
        result = enricher.get_playlist("PLxxx")

        assert result.tracks[0].album == "Greatest Hits"
        mock_yt.search.assert_called_once_with(
            "Popular Artist Hit Song", filter="songs", limit=3
        )

    @patch("yubal.services.metadata_enricher.YTMusic")
    def test_get_playlist_handles_search_failure(
        self, mock_ytmusic_class: MagicMock
    ) -> None:
        mock_yt = mock_ytmusic_class.return_value
        mock_yt.get_playlist.return_value = {
            "title": "Test Playlist",
            "tracks": [
                {
                    "videoId": "mv123",
                    "title": "Some Song",
                    "artists": [{"name": "Artist"}],
                    "album": None,
                    "isAvailable": True,
                    "thumbnails": [],
                }
            ],
        }
        mock_yt.search.side_effect = Exception("API Error")

        enricher = MetadataEnricher(request_delay=0)
        result = enricher.get_playlist("PLxxx")

        # Should still return the track, just without album info
        assert result.track_count == 1
        assert result.tracks[0].album is None

    @patch("yubal.services.metadata_enricher.YTMusic")
    def test_search_album_filters_by_artist(
        self, mock_ytmusic_class: MagicMock
    ) -> None:
        mock_yt = mock_ytmusic_class.return_value
        mock_yt.search.return_value = [
            {
                "artists": [{"name": "Wrong Artist"}],
                "album": {"name": "Wrong Album"},
                "thumbnails": [],
            },
            {
                "artists": [{"name": "Correct Artist"}],
                "album": {"name": "Correct Album"},
                "thumbnails": [],
            },
        ]

        enricher = MetadataEnricher(request_delay=0)
        result = enricher._search_album("Correct Artist", "Song Title")

        assert result is not None
        assert result["album"] == "Correct Album"

    @patch("yubal.services.metadata_enricher.YTMusic")
    def test_search_album_returns_none_when_no_match(
        self, mock_ytmusic_class: MagicMock
    ) -> None:
        mock_yt = mock_ytmusic_class.return_value
        mock_yt.search.return_value = [
            {
                "artists": [{"name": "Different Artist"}],
                "album": {"name": "Some Album"},
                "thumbnails": [],
            }
        ]

        enricher = MetadataEnricher(request_delay=0)
        result = enricher._search_album("Target Artist", "Song Title")

        assert result is None


class TestTrackMetadata:
    """Tests for TrackMetadata dataclass."""

    def test_track_metadata_creation(self) -> None:
        track = TrackMetadata(
            video_id="abc123",
            title="Test Title",
            artist="Test Artist",
            album="Test Album",
            thumbnail_url="http://example.com/thumb.jpg",
            track_number=1,
            is_available=True,
        )

        assert track.video_id == "abc123"
        assert track.title == "Test Title"
        assert track.artist == "Test Artist"
        assert track.album == "Test Album"
        assert track.track_number == 1
        assert track.is_available is True

    def test_track_metadata_with_none_album(self) -> None:
        track = TrackMetadata(
            video_id="abc123",
            title="Music Video",
            artist="Artist",
            album=None,
            thumbnail_url=None,
            track_number=1,
            is_available=True,
        )

        assert track.album is None
        assert track.thumbnail_url is None
