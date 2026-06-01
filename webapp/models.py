"""Простой слой доступа к SQLite без ORM.

Хранилище — две таблицы: `notes` (заметки) и `tags` (теги, многие-ко-многим через `note_tags`).
Используем `sqlite3` из стандартной библиотеки — чтобы не плодить зависимости и оставить
учебный пример прозрачным.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS notes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT    NOT NULL,
    body        TEXT    NOT NULL DEFAULT '',
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS tags (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS note_tags (
    note_id  INTEGER NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    tag_id   INTEGER NOT NULL REFERENCES tags(id)  ON DELETE CASCADE,
    PRIMARY KEY (note_id, tag_id)
);

CREATE INDEX IF NOT EXISTS idx_notes_created_at ON notes(created_at DESC);
"""


@dataclass
class Note:
    id: int
    title: str
    body: str
    created_at: str
    updated_at: str
    tags: list[str]


_DB_PATH: str | None = None


def init_db(database_path: str) -> None:
    """Создать схему (если ещё не создана) и запомнить путь к БД для последующих connect()."""
    global _DB_PATH
    _DB_PATH = database_path

    if database_path != ":memory:":
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)

    with _connect() as conn:
        conn.executescript(SCHEMA_SQL)
        conn.commit()


@contextmanager
def _connect() -> Iterator[sqlite3.Connection]:
    if _DB_PATH is None:
        raise RuntimeError("init_db() ещё не вызван — нет пути к БД")
    conn = sqlite3.connect(_DB_PATH, timeout=5.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# CRUD-операции с заметками
# ---------------------------------------------------------------------------

def create_note(title: str, body: str, tags: Iterable[str] = ()) -> int:
    title = title.strip()
    if not title:
        raise ValueError("Заголовок заметки не может быть пустым")

    with _connect() as conn:
        cursor = conn.execute(
            "INSERT INTO notes (title, body) VALUES (?, ?)",
            (title, body),
        )
        note_id = int(cursor.lastrowid or 0)
        _attach_tags(conn, note_id, tags)
        conn.commit()
        return note_id


def get_note(note_id: int) -> Note | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT id, title, body, created_at, updated_at FROM notes WHERE id = ?",
            (note_id,),
        ).fetchone()
        if row is None:
            return None
        tags = [r["name"] for r in conn.execute(
            "SELECT t.name FROM tags t JOIN note_tags nt ON nt.tag_id = t.id WHERE nt.note_id = ? ORDER BY t.name",
            (note_id,),
        )]
        return _row_to_note(row, tags)


def list_notes(limit: int = 50) -> list[Note]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, title, body, created_at, updated_at FROM notes ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        notes: list[Note] = []
        for row in rows:
            tags = [r["name"] for r in conn.execute(
                "SELECT t.name FROM tags t JOIN note_tags nt ON nt.tag_id = t.id WHERE nt.note_id = ? ORDER BY t.name",
                (row["id"],),
            )]
            notes.append(_row_to_note(row, tags))
        return notes


def delete_note(note_id: int) -> bool:
    with _connect() as conn:
        cursor = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
        return cursor.rowcount > 0


def count_notes() -> int:
    with _connect() as conn:
        row = conn.execute("SELECT COUNT(*) AS n FROM notes").fetchone()
        return int(row["n"])


def list_tags_with_counts() -> list[tuple[str, int]]:
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT t.name AS name, COUNT(nt.note_id) AS n
            FROM tags t
            LEFT JOIN note_tags nt ON nt.tag_id = t.id
            GROUP BY t.id
            ORDER BY n DESC, t.name ASC
            """,
        ).fetchall()
        return [(r["name"], int(r["n"])) for r in rows]


# ---------------------------------------------------------------------------
# Внутренние вспомогательные функции
# ---------------------------------------------------------------------------

def _attach_tags(conn: sqlite3.Connection, note_id: int, tags: Iterable[str]) -> None:
    for raw in tags:
        name = raw.strip().lower()
        if not name:
            continue
        conn.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (name,))
        tag_id = conn.execute("SELECT id FROM tags WHERE name = ?", (name,)).fetchone()["id"]
        conn.execute(
            "INSERT OR IGNORE INTO note_tags (note_id, tag_id) VALUES (?, ?)",
            (note_id, tag_id),
        )


def _row_to_note(row: sqlite3.Row, tags: list[str]) -> Note:
    return Note(
        id=int(row["id"]),
        title=str(row["title"]),
        body=str(row["body"]),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
        tags=tags,
    )


# Маркер времени, чтобы явно показывать в логах когда пересоздавалась БД.
_INIT_TIMESTAMP = datetime.now(timezone.utc).isoformat()
