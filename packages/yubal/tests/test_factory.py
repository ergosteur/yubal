"""Tests for factory functions and public API."""

from yubal import (
    APIConfig,
    MetadataExtractorService,
    create_extractor,
)


class TestCreateExtractor:
    """Tests for create_extractor factory function."""

    def test_creates_extractor_with_defaults(self) -> None:
        """Should create extractor with default config."""
        extractor = create_extractor()

        assert isinstance(extractor, MetadataExtractorService)

    def test_creates_extractor_with_custom_config(self) -> None:
        """Should create extractor with custom config."""
        config = APIConfig(search_limit=5, ignore_spelling=False)
        extractor = create_extractor(config)

        assert isinstance(extractor, MetadataExtractorService)


class TestPublicAPI:
    """Tests for public API exports."""

    def test_all_expected_exports_available(self) -> None:
        """All documented exports should be available."""
        import yubal

        # Factory function
        assert hasattr(yubal, "create_extractor")

        # Client
        assert hasattr(yubal, "YTMusicClient")
        assert hasattr(yubal, "YTMusicProtocol")

        # Services
        assert hasattr(yubal, "MetadataExtractorService")

        # Models
        assert hasattr(yubal, "TrackMetadata")
        assert hasattr(yubal, "VideoType")

        # Config
        assert hasattr(yubal, "APIConfig")

        # Exceptions
        assert hasattr(yubal, "YTMetaError")
        assert hasattr(yubal, "PlaylistParseError")
        assert hasattr(yubal, "PlaylistNotFoundError")
        assert hasattr(yubal, "APIError")

    def test_version_available(self) -> None:
        """Version should be available."""
        import yubal

        assert hasattr(yubal, "__version__")
        assert yubal.__version__ == "0.1.0"
