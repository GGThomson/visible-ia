"""Sources the AI uses in a market (HU-12): top domains by type, with the share of answers.

Counted over the API answers of the market's reviewed runs of one month: a domain cited
several times in the same answer counts once for that answer.
"""

from collections import defaultdict
from dataclasses import dataclass
from datetime import date

import psycopg

from visible_ia.extractor.fuentes import SOURCE_TYPES
from visible_ia.puntaje.indice import SURFACES, ScoreError

TYPE_LABELS = {
    "google_profile": "Ficha de Google",
    "doctoralia": "Doctoralia",
    "own_website": "Web propia",
    "social": "Redes sociales",
    "directory": "Directorios y rankings",
    "press": "Prensa",
    "other": "Otras",
}


@dataclass(frozen=True)
class SourceRow:
    source_type: str
    domain: str
    answers: int
    share: float  # % of the month's answers that cite it
    by_surface: dict[str, int]


def top_sources(
    citations: list[tuple[int, str, str, str]], total_answers: int, per_type: int = 5
) -> dict[str, list[SourceRow]]:
    """citations: (response_id, surface, domain, source_type). Returns type -> top domains."""
    answers: dict[tuple[str, str], set[int]] = defaultdict(set)
    surfaces: dict[tuple[str, str], dict[str, set[int]]] = defaultdict(lambda: defaultdict(set))
    for response_id, surface, domain, source_type in citations:
        answers[(source_type, domain)].add(response_id)
        surfaces[(source_type, domain)][surface].add(response_id)
    grouped: dict[str, list[SourceRow]] = {t: [] for t in SOURCE_TYPES}
    for (source_type, domain), ids in answers.items():
        grouped[source_type].append(
            SourceRow(
                source_type=source_type,
                domain=domain,
                answers=len(ids),
                share=round(100 * len(ids) / total_answers, 1) if total_answers else 0.0,
                by_surface={s: len(surfaces[(source_type, domain)][s]) for s in SURFACES},
            )
        )
    for rows in grouped.values():
        rows.sort(key=lambda r: (-r.answers, r.domain))
        del rows[per_type:]
    return {t: rows for t, rows in grouped.items() if rows}


def type_shares(citations: list[tuple[int, str, str, str]], total_answers: int) -> dict[str, float]:
    """% of answers citing at least one source of each type."""
    per_type: dict[str, set[int]] = defaultdict(set)
    for response_id, _, _, source_type in citations:
        per_type[source_type].add(response_id)
    return {
        t: round(100 * len(ids) / total_answers, 1) if total_answers else 0.0
        for t, ids in sorted(per_type.items(), key=lambda kv: -len(kv[1]))
    }


def latest_reviewed_month(conn: psycopg.Connection, market_id: int) -> date:
    with conn.cursor() as cur:
        cur.execute(
            "select max(month) from public.runs where market_id = %s and kind = 'api' "
            "and status = 'reviewed'",
            (market_id,),
        )
        month = cur.fetchone()[0]
    if month is None:
        raise ScoreError(f"El mercado {market_id} no tiene corridas revisadas")
    return month


def load_citations(
    conn: psycopg.Connection, market_id: int, month: date
) -> tuple[list[tuple[int, str, str, str]], int]:
    with conn.cursor() as cur:
        cur.execute(
            "select count(*) from public.responses r join public.runs ru on ru.id = r.run_id "
            "where ru.market_id = %s and ru.month = %s and ru.kind = 'api' "
            "and ru.status = 'reviewed' and r.surface = any(%s)",
            (market_id, month, list(SURFACES)),
        )
        (total,) = cur.fetchone()
        cur.execute(
            "select r.id, r.surface, s.domain, s.source_type from public.sources s "
            "join public.responses r on r.id = s.response_id "
            "join public.runs ru on ru.id = r.run_id "
            "where ru.market_id = %s and ru.month = %s and ru.kind = 'api' "
            "and ru.status = 'reviewed' and r.surface = any(%s)",
            (market_id, month, list(SURFACES)),
        )
        return cur.fetchall(), total
