"""Flask-приложение «Notes»: фабрика create_app() и регистрация blueprint'ов."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from flask import Flask

from .config import load_config
from .models import init_db
from .routes import bp as notes_bp


def create_app(config_overrides: dict | None = None) -> Flask:
    """Собрать и вернуть готовое приложение.

    `config_overrides` нужен в первую очередь для тестов: переопределить путь к БД,
    включить TESTING и т.п. без переменных окружения.
    """
    app = Flask(__name__, instance_relative_config=False)

    config = load_config(env=os.environ.get("WEBAPP_ENV", "development"))
    app.config.update(config.as_flask_dict())
    if config_overrides:
        app.config.update(config_overrides)

    _configure_logging(app)
    _ensure_data_dir(app)

    init_db(app.config["DATABASE_PATH"])

    app.register_blueprint(notes_bp)

    return app


def _configure_logging(app: Flask) -> None:
    level = getattr(logging, str(app.config.get("LOG_LEVEL", "INFO")).upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    app.logger.setLevel(level)


def _ensure_data_dir(app: Flask) -> None:
    db_path = Path(app.config["DATABASE_PATH"])
    db_path.parent.mkdir(parents=True, exist_ok=True)
