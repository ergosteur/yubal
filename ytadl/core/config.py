"""Application configuration paths."""

from pathlib import Path

# APP_ROOT: project root from ytadl/core/config.py
APP_ROOT = Path(__file__).parent.parent.parent

# Default directories (can be overridden via CLI options)
DATA_DIR = APP_ROOT / "data"
CONFIG_DIR = APP_ROOT / "config"

DEFAULT_BEETS_CONFIG = CONFIG_DIR / "config.yaml"
DEFAULT_BEETS_DB = CONFIG_DIR / "beets.db"
DEFAULT_LIBRARY_DIR = DATA_DIR
