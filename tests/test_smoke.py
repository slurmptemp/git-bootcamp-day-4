"""Минимальные smoke-тесты webapp-notes.

Запуск: `pytest -q` из корня проекта (`hometasks/day4/starter/webapp-notes/`).
Тесты используют тестовый конфиг — БД в памяти, никаких внешних зависимостей.
"""

from __future__ import annotations

import pytest

from webapp import create_app


@pytest.fixture()
def app(tmp_path):
    db_path = tmp_path / "notes-test.db"
    return create_app(config_overrides={"TESTING": True, "DATABASE_PATH": str(db_path)})


@pytest.fixture()
def client(app):
    return app.test_client()


def test_healthz_returns_ok(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"
    assert payload["notes"] == 0


def test_index_renders_empty_state(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Заметок пока нет" in response.get_data(as_text=True)


def test_create_and_list_note(client):
    response = client.post(
        "/notes",
        data={"title": "Первая заметка", "body": "Текст заметки", "tags": "idea, todo"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Первая заметка" in body
    assert "#idea" in body and "#todo" in body


def test_search_finds_note_by_title(client):
    client.post(
        "/notes",
        data={"title": "Сходить за молоком", "body": "обязательно завтра", "tags": "todo"},
    )

    response = client.get("/?q=молоком")
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Сходить за молоком" in body
    assert "match: title" in body


def test_api_notes_returns_json(client):
    client.post("/notes", data={"title": "API check", "body": "", "tags": ""})

    response = client.get("/api/notes")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert any(n["title"] == "API check" for n in data)
