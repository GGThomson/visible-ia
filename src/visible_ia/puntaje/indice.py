"""Monthly presence index of a market (HU-10, HU-11; PRD §5.2).

For each clinic of the market and each surface (ChatGPT API, Google AI Mode):
- index = % of that surface's answers where the clinic appears (after aliases), with Wilson;
- average position when it appears (1 = first name in the answer, discarded names skipped);
- share of mentions = its appearances / appearances of all the market's clinics.
The combined index is the plain average of the surfaces' indexes; its interval uses the
pooled answers (both surfaces have 30 answers, so it is the same proportion).

Only API answers of a *reviewed* run count: manual samples never enter the index.
"""

from collections import defaultdict
from dataclasses import dataclass
from datetime import date

import psycopg

from visible_ia.puntaje.estadistica import wilson

SURFACES = ("chatgpt_api", "google_ai_mode")
COMBINED = "combined"


class ScoreError(ValueError):
    pass


@dataclass(frozen=True)
class Answer:
    response_id: int
    surface: str


@dataclass(frozen=True)
class MentionRow:
    response_id: int
    position: int
    clinic_id: int | None


@dataclass(frozen=True)
class Score:
    clinic_id: int
    surface: str
    n_responses: int
    appearances: int
    presence_index: float  # 0–100
    ci_low: float | None
    ci_high: float | None
    avg_position: float | None
    mention_share: float | None  # 0–100


def _pct(x: float | None) -> float | None:
    return None if x is None else round(100 * x, 2)


def compute_scores(
    answers: list[Answer], mentions: list[MentionRow], clinic_ids: list[int]
) -> list[Score]:
    """Pure computation: one Score per clinic and surface, plus the combined one."""
    by_surface = {s: {a.response_id for a in answers if a.surface == s} for s in SURFACES}
    # Rank of each clinic in each answer: order of the (non-discarded) names, first one wins.
    ranks: dict[tuple[int, int], int] = {}
    per_response: dict[int, list[MentionRow]] = defaultdict(list)
    for m in mentions:
        per_response[m.response_id].append(m)
    for response_id, rows in per_response.items():
        for rank, m in enumerate(sorted(rows, key=lambda r: r.position), start=1):
            if m.clinic_id is not None:
                ranks.setdefault((response_id, m.clinic_id), rank)

    scores: list[Score] = []
    totals: dict[str, int] = {}
    counts: dict[tuple[int, str], tuple[int, list[int]]] = {}
    for surface in SURFACES:
        responses = by_surface[surface]
        total = 0
        for clinic_id in clinic_ids:
            positions = [ranks[(r, clinic_id)] for r in responses if (r, clinic_id) in ranks]
            counts[(clinic_id, surface)] = (len(positions), positions)
            total += len(positions)
        totals[surface] = total

    for clinic_id in clinic_ids:
        indexes, all_positions, k_sum, n_sum = [], [], 0, 0
        for surface in SURFACES:
            n = len(by_surface[surface])
            k, positions = counts[(clinic_id, surface)]
            interval = wilson(k, n)
            scores.append(
                Score(
                    clinic_id=clinic_id,
                    surface=surface,
                    n_responses=n,
                    appearances=k,
                    presence_index=_pct(k / n) if n else 0.0,
                    ci_low=_pct(interval[0]) if interval else None,
                    ci_high=_pct(interval[1]) if interval else None,
                    avg_position=round(sum(positions) / k, 2) if k else None,
                    mention_share=_pct(k / totals[surface]) if totals[surface] else None,
                )
            )
            if n:
                indexes.append(k / n)
            all_positions += positions
            k_sum += k
            n_sum += n
        interval = wilson(k_sum, n_sum)
        combined_total = sum(totals.values())
        scores.append(
            Score(
                clinic_id=clinic_id,
                surface=COMBINED,
                n_responses=n_sum,
                appearances=k_sum,
                presence_index=_pct(sum(indexes) / len(indexes)) if indexes else 0.0,
                ci_low=_pct(interval[0]) if interval else None,
                ci_high=_pct(interval[1]) if interval else None,
                avg_position=round(sum(all_positions) / len(all_positions), 2)
                if all_positions
                else None,
                mention_share=_pct(k_sum / combined_total) if combined_total else None,
            )
        )
    return scores


# --- database ------------------------------------------------------------------------------


def load_run(conn: psycopg.Connection, run_id: int) -> tuple[int, date]:
    """(market_id, month) of a reviewed API run; a clear error otherwise."""
    with conn.cursor() as cur:
        cur.execute(
            "select market_id, month, kind, status from public.runs where id = %s", (run_id,)
        )
        row = cur.fetchone()
    if row is None:
        raise ScoreError(f"No existe la corrida {run_id}")
    market_id, month, kind, status = row
    if kind != "api":
        raise ScoreError(
            f"La corrida {run_id} es manual: las muestras manuales no entran al índice"
        )
    if status != "reviewed":
        raise ScoreError(
            f"La corrida {run_id} está '{status}': primero revísala y ciérrala "
            f"(visible-ia revisar cerrar {run_id})"
        )
    return market_id, month


def load_inputs(
    conn: psycopg.Connection, run_id: int, market_id: int
) -> tuple[list[Answer], list[MentionRow], list[int]]:
    with conn.cursor() as cur:
        cur.execute(
            "select id, surface from public.responses where run_id = %s and surface = any(%s)",
            (run_id, list(SURFACES)),
        )
        answers = [Answer(*row) for row in cur.fetchall()]
        cur.execute(
            "select m.response_id, m.position, m.clinic_id from public.mentions m "
            "join public.responses r on r.id = m.response_id "
            "where r.run_id = %s and r.surface = any(%s) and m.status <> 'discarded'",
            (run_id, list(SURFACES)),
        )
        mentions = [MentionRow(*row) for row in cur.fetchall()]
        cur.execute(
            "select clinic_id from public.clinic_markets where market_id = %s order by clinic_id",
            (market_id,),
        )
        clinic_ids = [row[0] for row in cur.fetchall()]
    return answers, mentions, clinic_ids


def save_scores(conn: psycopg.Connection, market_id: int, month: date, scores: list[Score]) -> None:
    with conn.transaction(), conn.cursor() as cur:
        cur.executemany(
            "insert into public.monthly_scores (market_id, month, clinic_id, surface, n_responses, "
            "appearances, presence_index, ci_low, ci_high, avg_position, mention_share) "
            "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
            "on conflict (market_id, month, clinic_id, surface) do update set "
            "n_responses = excluded.n_responses, appearances = excluded.appearances, "
            "presence_index = excluded.presence_index, ci_low = excluded.ci_low, "
            "ci_high = excluded.ci_high, avg_position = excluded.avg_position, "
            "mention_share = excluded.mention_share, created_at = now()",
            [
                (market_id, month, s.clinic_id, s.surface, s.n_responses, s.appearances,
                 s.presence_index, s.ci_low, s.ci_high, s.avg_position, s.mention_share)
                for s in scores
            ],
        )  # fmt: skip


def calculate(conn: psycopg.Connection, run_id: int) -> tuple[int, date, list[Score]]:
    market_id, month = load_run(conn, run_id)
    answers, mentions, clinic_ids = load_inputs(conn, run_id, market_id)
    if not clinic_ids:
        raise ScoreError(f"El mercado {market_id} no tiene clínicas: impórtalas primero")
    scores = compute_scores(answers, mentions, clinic_ids)
    save_scores(conn, market_id, month, scores)
    return market_id, month, scores


@dataclass(frozen=True)
class RankingRow:
    clinic_id: int
    name: str
    combined: float
    ci_low: float | None
    ci_high: float | None
    chatgpt: float | None
    google: float | None
    avg_position: float | None
    mention_share: float | None


def ranking(
    conn: psycopg.Connection, market_id: int, month: date | None = None
) -> tuple[date, list[RankingRow]]:
    """The market's ranking by combined index (latest month by default)."""
    with conn.cursor() as cur:
        if month is None:
            cur.execute(
                "select max(month) from public.monthly_scores where market_id = %s", (market_id,)
            )
            month = cur.fetchone()[0]
            if month is None:
                raise ScoreError(
                    f"El mercado {market_id} no tiene puntajes: calcula una corrida primero"
                )
        cur.execute(
            "select c.id, c.name, "
            "max(s.presence_index) filter (where s.surface = 'combined'), "
            "max(s.ci_low) filter (where s.surface = 'combined'), "
            "max(s.ci_high) filter (where s.surface = 'combined'), "
            "max(s.presence_index) filter (where s.surface = 'chatgpt_api'), "
            "max(s.presence_index) filter (where s.surface = 'google_ai_mode'), "
            "max(s.avg_position) filter (where s.surface = 'combined'), "
            "max(s.mention_share) filter (where s.surface = 'combined') "
            "from public.monthly_scores s join public.clinics c on c.id = s.clinic_id "
            "where s.market_id = %s and s.month = %s group by c.id, c.name",
            (market_id, month),
        )
        rows = [
            RankingRow(clinic_id, name, *(None if v is None else float(v) for v in values))
            for clinic_id, name, *values in cur.fetchall()
        ]
    rows.sort(key=lambda r: (-(r.combined or 0), r.name.lower()))
    return month, rows
