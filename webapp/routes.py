"""Веб-роуты приложения «Notes»: HTML-страницы и небольшое JSON-API."""

from __future__ import annotations

from flask import Blueprint, abort, jsonify, redirect, render_template, request, url_for

from . import models, services


bp = Blueprint("notes", __name__)


@bp.get("/")
def index():
    notes = models.list_notes(limit=50)
    query = request.args.get("q", "").strip()
    hits = services.search_notes(query) if query else []
    return render_template("index.html", notes=notes, query=query, hits=hits)


@bp.get("/notes/<int:note_id>")
def show_note(note_id: int):
    note = models.get_note(note_id)
    if note is None:
        abort(404)
    return render_template("note.html", note=note)


@bp.post("/notes")
def create_note():
    title = request.form.get("title", "").strip()
    body = request.form.get("body", "").strip()
    tags_raw = request.form.get("tags", "")
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]

    if not title:
        return redirect(url_for("notes.index"))

    models.create_note(title=title, body=body, tags=tags)
    return redirect(url_for("notes.index"))


@bp.post("/notes/<int:note_id>/delete")
def delete_note(note_id: int):
    models.delete_note(note_id)
    return redirect(url_for("notes.index"))


@bp.get("/stats")
def stats():
    return render_template("stats.html", stats=services.compute_stats())


@bp.get("/api/notes")
def api_notes():
    notes = models.list_notes(limit=50)
    return jsonify([
        {
            "id": n.id,
            "title": n.title,
            "tags": n.tags,
            "created_at": n.created_at,
        }
        for n in notes
    ])


@bp.get("/healthz")
def healthz():
    return {"status": "ok", "notes": models.count_notes()}
