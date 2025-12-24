"""Application configuration paths.

This module re-exports from ytadl.core.config for backward compatibility.
"""

from ytadl.core.config import (
    APP_ROOT,
    CONFIG_DIR,
    DATA_DIR,
    DEFAULT_BEETS_CONFIG,
    DEFAULT_BEETS_DB,
    DEFAULT_LIBRARY_DIR,
)

__all__ = [
    "APP_ROOT",
    "CONFIG_DIR",
    "DATA_DIR",
    "DEFAULT_BEETS_CONFIG",
    "DEFAULT_BEETS_DB",
    "DEFAULT_LIBRARY_DIR",
]
