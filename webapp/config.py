"""Конфигурация приложения «Notes».

Файл сознательно разбит на тематические секции — это упрощает диффы и точечные
изменения в учебных сценариях слияния и rebase. Каждый раздел отвечает за свою
зону ответственности и не должен «течь» в соседние.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


# ---------------------------------------------------------------------------
# Секция 1 — Flask: базовые параметры приложения
# ---------------------------------------------------------------------------

@dataclass
class FlaskSection:
    DEBUG: bool = False
    SECRET_KEY: str = "dev-secret-change-me"
    TEMPLATES_AUTO_RELOAD: bool = False
    JSON_SORT_KEYS: bool = False


# ---------------------------------------------------------------------------
# Секция 2 — Database: путь к SQLite и параметры подключения
# ---------------------------------------------------------------------------

@dataclass
class DatabaseSection:
    DATABASE_PATH: str = str(Path(__file__).resolve().parent.parent / "data" / "notes.db")
    DATABASE_TIMEOUT_SEC: float = 5.0
    DATABASE_FOREIGN_KEYS: bool = True


# ---------------------------------------------------------------------------
# Секция 3 — Performance: лимиты, таймауты, пулы (главная зона конфликтов в ДЗ)
# ---------------------------------------------------------------------------

@dataclass
class PerformanceSection:
    REQUEST_TIMEOUT_SEC: int = 120
    DB_POOL_SIZE: int = 20
    SEARCH_RESULTS_LIMIT: int = 200
    CACHE_TTL_SEC: int = 300
    GUNICORN_WORKERS: int = 8


# ---------------------------------------------------------------------------
# Секция 4 — Security: безопасность транспорта и сессий
# ---------------------------------------------------------------------------

@dataclass
class SecuritySection:
    SESSION_COOKIE_SECURE: bool = False
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"
    CSRF_PROTECTION: bool = False


# ---------------------------------------------------------------------------
# Секция 5 — Logging: уровень и формат логов
# ---------------------------------------------------------------------------

@dataclass
class LoggingSection:
    LOG_LEVEL: str = "INFO"
    LOG_REQUESTS: bool = True
    LOG_SQL: bool = False


# ---------------------------------------------------------------------------
# Сборка финального конфига
# ---------------------------------------------------------------------------

@dataclass
class AppConfig:
    flask: FlaskSection = field(default_factory=FlaskSection)
    database: DatabaseSection = field(default_factory=DatabaseSection)
    performance: PerformanceSection = field(default_factory=PerformanceSection)
    security: SecuritySection = field(default_factory=SecuritySection)
    logging: LoggingSection = field(default_factory=LoggingSection)

    def as_flask_dict(self) -> dict:
        """Сплющить все секции в плоский dict под `app.config.update()`."""
        result: dict = {}
        for section in (self.flask, self.database, self.performance, self.security, self.logging):
            for key, value in section.__dict__.items():
                result[key] = value
        return result


def load_config(env: str = "development") -> AppConfig:
    """Собрать конфиг под выбранное окружение.

    Поддерживаемые окружения: `development` (дефолт), `production`, `testing`.
    """
    cfg = AppConfig()

    if env == "production":
        cfg.flask.DEBUG = False
        cfg.flask.TEMPLATES_AUTO_RELOAD = False
        cfg.security.SESSION_COOKIE_SECURE = True
        cfg.logging.LOG_LEVEL = "WARNING"
        cfg.logging.LOG_REQUESTS = False
    elif env == "testing":
        cfg.flask.DEBUG = False
        cfg.flask.TESTING = True  # type: ignore[attr-defined]
        cfg.logging.LOG_LEVEL = "ERROR"
    else:
        cfg.flask.DEBUG = True
        cfg.flask.TEMPLATES_AUTO_RELOAD = True

    secret_from_env = os.environ.get("WEBAPP_SECRET_KEY")
    if secret_from_env:
        cfg.flask.SECRET_KEY = secret_from_env

    db_from_env = os.environ.get("WEBAPP_DATABASE_PATH")
    if db_from_env:
        cfg.database.DATABASE_PATH = db_from_env

    return cfg
