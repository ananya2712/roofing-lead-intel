"""Flask app factory."""
import logging

from flask import Flask

from .config import load_config
from .db import close_session, init_db
from .errors import register_error_handlers


def create_app(config=None) -> Flask:
    """Create the Flask app: database, error handlers, /api/v1 routes and CLI commands."""
    cfg = config or load_config()
    app = Flask(__name__)
    app.config["APP_CONFIG"] = cfg
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

    init_db(cfg.database_url)
    app.teardown_appcontext(close_session)
    register_error_handlers(app)

    from .api import api_bp
    from .cli import register_cli

    app.register_blueprint(api_bp, url_prefix="/api/v1")
    register_cli(app)
    return app
