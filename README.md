# ytad

YouTube Album Downloader - a self-hosted tool for downloading YouTube Music albums with automatic tagging and organization via beets.

## Features

- Download entire YouTube Music albums via URL
- Automatic audio extraction at highest quality (MP3)
- Auto-tagging via MusicBrainz
- Album art fetching and embedding
- Organized library structure: `Artist/Album/Track.mp3`

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [FFmpeg](https://ffmpeg.org/) (for audio extraction)

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd ytad

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

### Install FFmpeg

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Arch
sudo pacman -S ffmpeg
```

## Usage

```bash
# Build CSS and start server
make dev

# Or run separately
make css              # build CSS once
uv run python run.py  # start server
```

Open http://localhost:5001 in your browser.

1. Go to [YouTube Music](https://music.youtube.com)
2. Find an album and copy its URL (should contain `list=OLAK5uy_...`)
3. Paste the URL and click "Download Album"
4. Wait for download and auto-tagging to complete
5. Find your music in `data/library/`

## Project Structure

```
ytad/
├── app/
│   ├── services/
│   │   ├── downloader.py   # yt-dlp integration
│   │   ├── tagger.py       # beets integration
│   │   └── pipeline.py     # orchestration
│   ├── templates/          # Jinja2 templates
│   └── routes.py           # Flask routes
├── config/
│   ├── settings.py         # app configuration
│   └── beets_config.yaml   # beets tagging config
├── data/
│   ├── downloads/          # temporary staging
│   └── library/            # organized music library
└── run.py                  # entry point
```

## Configuration

### Beets

Edit `config/beets_config.yaml` to customize:

- `paths.default` - file organization pattern
- `match.strong_rec_thresh` - auto-match confidence threshold (lower = stricter)
- `fetchart.sources` - album art sources

### Application

Edit `config/settings.py` to customize:

- `AUDIO_FORMAT` - output format (default: mp3)
- `AUDIO_QUALITY` - quality level (0 = best)

## Development

### Tailwind CSS

The project uses Tailwind CSS v4 with the standalone CLI:

```bash
# Download Tailwind CLI (macOS ARM64)
curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-macos-arm64
chmod +x tailwindcss-macos-arm64 && mv tailwindcss-macos-arm64 tailwindcss

# Build CSS
make css

# Watch mode (auto-rebuild on changes)
make watch
```

Colors are defined in `styles.css` using the Flexoki palette.

## Tech Stack

- **Backend:** Flask + Python 3.12
- **Download:** yt-dlp
- **Tagging:** beets + MusicBrainz
- **Frontend:** Jinja2 + Tailwind CSS v4
- **Colors:** [Flexoki](https://stephango.com/flexoki)

## License

MIT
