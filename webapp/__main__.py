"""Точка входа `python -m webapp` — поднимает встроенный Flask-сервер.

В проде используется gunicorn (см. `Dockerfile`); этот entry-point — для локальной разработки.
"""

from __future__ import annotations

import os

from . import create_app


def main() -> None:
    app = create_app()
    host = os.environ.get("WEBAPP_HOST", "127.0.0.1")
    port = int(os.environ.get("WEBAPP_PORT", "8000"))
    debug = app.config.get("DEBUG", False)
    app.run(host=host, port=port, debug=debug, use_reloader=False)


if __name__ == "__main__":
    main()
