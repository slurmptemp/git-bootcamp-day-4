# webapp-notes

Учебный мини-сервис «Заметки» на Flask + SQLite. Используется как стартер для домашнего задания дня 4 курса [«Интенсив по погружению в GIT»](https://slurm.io/git-intensive).

Цель проекта — дать студенту реалистичный по объёму код, в котором будет интересно разрешать конфликты слияния. Само приложение умеет немного: создавать заметки с тегами, искать их и показывать сводную статистику.

## Что внутри

```
webapp-notes/
├── webapp/                # Python-пакет с Flask-приложением
│   ├── __init__.py        # фабрика create_app()
│   ├── __main__.py        # точка входа `python -m webapp`
│   ├── config.py          # 5 секций конфига (Flask, DB, Performance, Security, Logging)
│   ├── models.py          # SQLite + CRUD + init_db()
│   ├── services.py        # поиск + статистика
│   ├── routes.py          # blueprint с HTML-страницами и /api/notes
│   ├── templates/         # Jinja2-шаблоны
│   └── static/            # style.css + app.js
├── tests/test_smoke.py    # минимальные smoke-тесты pytest
├── data/                  # каталог под SQLite-БД (volume в Docker)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── README.md
```

## Запуск локально (без Docker)

```bash
make run            # создаст .venv, установит зависимости и запустит приложение
```

Откроется на `http://127.0.0.1:8000`.

По шагам (если нужен активированный shell в venv):

```bash
make install        # .venv + pip install -r requirements.txt
source .venv/bin/activate
make run            # python -m webapp
```

Запустить тесты:

```bash
make test           # install + pytest (зависимости ставятся автоматически)
```

## Запуск в Docker

Если у вас установлен Docker с плагином `docker compose`:

```bash
make up             # build + поднимет на http://localhost:8000
make logs           # хвост логов
make down           # остановить
make clean          # удалить БД, venv, кэши, docker-образ и контейнеры проекта
```

SQLite-БД пробрасывается через `volume` в каталог `./data`, поэтому переживёт пересоздание контейнера.

## Маршруты

| Метод | URL                           | Что делает                          |
|-------|-------------------------------|-------------------------------------|
| GET   | `/`                           | список заметок и форма поиска       |
| POST  | `/notes`                      | создать заметку                     |
| GET   | `/notes/<id>`                 | страница одной заметки              |
| POST  | `/notes/<id>/delete`          | удалить заметку                     |
| GET   | `/stats`                      | сводная статистика                  |
| GET   | `/api/notes`                  | JSON-список заметок                 |
| GET   | `/healthz`                    | health-check                        |

## Конфигурация

Поведение приложения переключается через переменную `WEBAPP_ENV`: `development` (по умолчанию), `production`, `testing`. Дополнительно поддерживаются переменные `WEBAPP_HOST`, `WEBAPP_PORT`, `WEBAPP_DATABASE_PATH`, `WEBAPP_SECRET_KEY`.

## Это не курс по Docker

Запускать приложение для зачёта по дню 4 **не обязательно** — это учебный фон, чтобы было где разворачивать сюжеты слияний. Если интересно — поднимите и потыкайте; если нет — просто работайте с кодом и git-историей.
