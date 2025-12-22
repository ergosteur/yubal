"""Flask application factory."""
from flask import Flask
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.secret_key = settings.SECRET_KEY
    app.debug = settings.DEBUG

    # Ensure data directories exist
    settings.DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    settings.LIBRARY_DIR.mkdir(parents=True, exist_ok=True)

    # Register blueprints
    from .routes import main
    app.register_blueprint(main)

    return app
