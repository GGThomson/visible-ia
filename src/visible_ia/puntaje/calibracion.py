"""Calibration of the API against the consumer apps (PRD §5.4).

Each month, per active market, the operator pastes one answer per question from the ChatGPT
app and the Gemini app (manual run). Reported for each app:
- coincidence: % of the market clinics the app named that the API also named that month;
- whether the "leader" (most named clinic) is the same.
Alert: if the ChatGPT coincidence is below 50 % two months in a row, the report warns and the
method is reviewed. Manual answers marked excluir_calibracion (phase-1 "Lima") never count.
"""

from collections import Counter
from dataclasses import dataclass
from datetime import date

import psycopg

from visible_ia.puntaje.indice import month_shift

ALERT_BELOW = 50.0
APPS = {"chatgpt_app_manual": "ChatGPT (app)", "gemini_app_manual": "Gemini (app)"}


@dataclass(frozen=True)
class Calibration:
    app: str
    answers: int
    app_clinics: int
    shared: int
    coincidence: float | None  # %
    leader_app: str | None
    leader_api: str | None

    @property
    def same_leader(self) -> bool | None:
        if self.leader_app is None or self.leader_api is None:
            return None
        return self.leader_app == self.leader_api


def compare(
    app_mentions: list[int], api_mentions: list[int], names: dict[int, str], app: str, answers: int
) -> Calibration:
    """app_mentions / api_mentions: clinic ids, one per (answer, clinic) appearance."""
    app_set, api_set = set(app_mentions), set(api_mentions)
    shared = len(app_set & api_set)
    coincidence = round(100 * shared / len(app_set), 1) if app_set else None

    def leader(ids: list[int]) -> str | None:
        return names.get(Counter(ids).most_common(1)[0][0]) if ids else None

    return Calibration(
        app, answers, len(app_set), shared, coincidence, leader(app_mentions), leader(api_mentions)
    )


def _appearances(
    conn: psycopg.Connection, market_id: int, month: date, kind: str, surfaces: list[str]
) -> tuple[list[int], int]:
    with conn.cursor() as cur:
        cur.execute(
            "select r.id, m.clinic_id from public.responses r "
            "join public.runs ru on ru.id = r.run_id "
            "left join public.mentions m on m.response_id = r.id and m.status <> 'discarded' "
            "and m.clinic_id is not null "
            "where ru.market_id = %s and ru.month = %s and ru.kind = %s and r.surface = any(%s) "
            "and coalesce(r.raw->>'excluir_calibracion', 'false') <> 'true'"
            + (" and ru.status = 'reviewed'" if kind == "api" else ""),
            (market_id, month, kind, surfaces),
        )
        rows = cur.fetchall()
    per_answer = {(rid, cid) for rid, cid in rows if cid is not None}
    return [cid for _, cid in per_answer], len({rid for rid, _ in rows})


def calibrate(conn: psycopg.Connection, market_id: int, month: date) -> list[Calibration]:
    """One Calibration per app with manual answers that month (empty list if none)."""
    with conn.cursor() as cur:
        cur.execute(
            "select c.id, c.name from public.clinics c join public.clinic_markets cm "
            "on cm.clinic_id = c.id where cm.market_id = %s",
            (market_id,),
        )
        names = dict(cur.fetchall())
    out = []
    for surface, label in APPS.items():
        app_ids, answers = _appearances(conn, market_id, month, "manual", [surface])
        if not answers:
            continue
        api_surface = (
            ["chatgpt_api"]
            if surface == "chatgpt_app_manual"
            else ["chatgpt_api", "google_ai_mode"]
        )
        api_ids, _ = _appearances(conn, market_id, month, "api", api_surface)
        out.append(compare(app_ids, api_ids, names, label, answers))
    return out


def chatgpt_alert(current: list[Calibration], previous: list[Calibration]) -> bool:
    """True when the ChatGPT coincidence was below 50 % this month and the previous one."""

    def low(items: list[Calibration]) -> bool:
        c = next((x for x in items if x.app == APPS["chatgpt_app_manual"]), None)
        return c is not None and c.coincidence is not None and c.coincidence < ALERT_BELOW

    return low(current) and low(previous)


def calibration_with_alert(
    conn: psycopg.Connection, market_id: int, month: date
) -> tuple[list[Calibration], bool]:
    current = calibrate(conn, market_id, month)
    previous = calibrate(conn, market_id, month_shift(month, -1))
    return current, chatgpt_alert(current, previous)
