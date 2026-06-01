"""Бизнес-логика поверх моделей: поиск и статистика.

Сервисы намеренно живут в отдельном файле — их крупный код удобно использовать как
учебную «зону конфликтов» при слиянии веток.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import models


@dataclass
class SearchHit:
    note: models.Note
    score: float
    matched_in: str  # "title" | "body" | "tag"


@dataclass
class Stats:
    total_notes: int
    total_tags: int
    top_tags: list[tuple[str, int]]
    avg_body_length: float


def search_notes(query: str, limit: int = 50) -> list[SearchHit]:
    """Найти заметки, у которых в title/body/tag встречается подстрока query.

    Алгоритм простой — учебный. Реальный поиск делается через FTS, но цель файла —
    дать осязаемый кусок логики, который удобно править в учебных конфликтах.
    """
    query_norm = (query or "").strip().lower()
    if not query_norm:
        return []

    notes = models.list_notes(limit=500)
    hits: list[SearchHit] = []
    for note in notes:
        title_l = note.title.lower()
        body_l = note.body.lower()
        tags_l = [t.lower() for t in note.tags]

        if query_norm in title_l:
            score = 1.0 + (1.0 if title_l.startswith(query_norm) else 0.0)
            hits.append(SearchHit(note=note, score=score, matched_in="title"))
            continue

        if any(query_norm == tag for tag in tags_l):
            hits.append(SearchHit(note=note, score=0.9, matched_in="tag"))
            continue

        if query_norm in body_l:
            occurrences = body_l.count(query_norm)
            score = 0.5 + min(0.4, 0.1 * occurrences)
            hits.append(SearchHit(note=note, score=score, matched_in="body"))

    hits.sort(key=lambda h: h.score, reverse=True)
    return hits[:limit]


def compute_stats() -> Stats:
    """Собрать сводную статистику по заметкам и тегам."""
    notes = models.list_notes(limit=10_000)
    total_notes = len(notes)
    total_tags = len({t for note in notes for t in note.tags})
    top_tags = models.list_tags_with_counts()[:5]
    avg_len = (sum(len(n.body) for n in notes) / total_notes) if total_notes else 0.0
    return Stats(
        total_notes=total_notes,
        total_tags=total_tags,
        top_tags=top_tags,
        avg_body_length=round(avg_len, 1),
    )
