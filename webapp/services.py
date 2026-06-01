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


def search_notes(query: str, limit: int = 25) -> list[SearchHit]:
    """Поиск под продакшен: точный scoring, приоритет тегов перед телом.

    На небольшой выдаче (limit=25) важна релевантность: точное совпадение по
    тегу — 1.0, начало title — 0.95, подстрока в title — 0.7, тело — 0.4 с
    бонусом за частоту, но не выше 0.6.
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

        if any(query_norm == tag for tag in tags_l):
            hits.append(SearchHit(note=note, score=1.0, matched_in="tag"))
            continue
        if title_l.startswith(query_norm):
            hits.append(SearchHit(note=note, score=0.95, matched_in="title"))
            continue
        if query_norm in title_l:
            hits.append(SearchHit(note=note, score=0.7, matched_in="title"))
            continue
        if query_norm in body_l:
            occurrences = body_l.count(query_norm)
            score = min(0.6, 0.4 + 0.05 * occurrences)
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
