"""Review of extracted mentions (HU-08, HU-09), from the terminal or from a CSV.

Every change marks the mention as `corrected` (or `discarded`), so the score (C5), which is
always computed from the mentions, reflects it. A run becomes `reviewed` only when no mention
is left in `review`.
"""

import csv
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import psycopg

from visible_ia.mercados.alias import add_alias, add_derived_aliases, fold

ACTIONS = ("", "ok", "asociar", "nueva", "descartar", "unir")
EXPORT_COLUMNS = (
    "mention_id", "response_id", "surface", "template_id", "repetition", "position",
    "raw_name", "clinic_id", "clinic_name", "status",
    "accion", "clinica_destino", "unir_con", "nombre_nueva", "extracto",
)  # fmt: skip


class ReviewError(ValueError):
    pass


@dataclass
class ApplyResult:
    by_action: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    errors: list[str] = field(default_factory=list)
    clinics_created: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class MentionRow:
    mention_id: int
    response_id: int
    surface: str
    template_id: str
    repetition: int
    position: int
    raw_name: str
    clinic_id: int | None
    clinic_name: str | None
    status: str
    text: str


def run_mentions(conn: psycopg.Connection, run_id: int) -> list[MentionRow]:
    with conn.cursor() as cur:
        cur.execute(
            "select m.id, r.id, r.surface, q.template_id, r.repetition, m.position, m.raw_name, "
            "m.clinic_id, c.name, m.status, coalesce(r.text, '') "
            "from public.mentions m "
            "join public.responses r on r.id = m.response_id "
            "join public.questions q on q.id = r.question_id "
            "left join public.clinics c on c.id = m.clinic_id "
            "where r.run_id = %s "
            "order by r.surface, q.template_id, r.repetition, m.position",
            (run_id,),
        )
        return [MentionRow(*row) for row in cur.fetchall()]


def _mention_in_run(conn: psycopg.Connection, run_id: int, mention_id: int) -> tuple[int, int]:
    """(response_id, market_id) of a mention, checking it belongs to the run."""
    with conn.cursor() as cur:
        cur.execute(
            "select r.id, ru.market_id from public.mentions m "
            "join public.responses r on r.id = m.response_id "
            "join public.runs ru on ru.id = r.run_id where m.id = %s and ru.id = %s",
            (mention_id, run_id),
        )
        row = cur.fetchone()
    if row is None:
        raise ReviewError(f"La mención {mention_id} no es de la corrida {run_id}")
    return row


def _set(cur, mention_id: int, *, status: str, clinic_id=..., note: str | None = None) -> None:
    sets, values = (
        ["status = %s", "updated_at = now()", "note = coalesce(%s, note)"],
        [status, note],
    )
    if clinic_id is not ...:
        sets.append("clinic_id = %s")
        values.append(clinic_id)
    cur.execute(
        f"update public.mentions set {', '.join(sets)} where id = %s", (*values, mention_id)
    )


def associate(conn: psycopg.Connection, run_id: int, mention_id: int, clinic_id: int) -> None:
    _, market_id = _mention_in_run(conn, run_id, mention_id)
    with conn.transaction(), conn.cursor() as cur:
        cur.execute(
            "select 1 from public.clinic_markets where clinic_id = %s and market_id = %s",
            (clinic_id, market_id),
        )
        if cur.fetchone() is None:
            raise ReviewError(f"La clínica {clinic_id} no es del mercado {market_id}")
        _set(cur, mention_id, status="corrected", clinic_id=clinic_id)


def create_clinic_for(
    conn: psycopg.Connection, run_id: int, mention_id: int, name: str | None = None
) -> int:
    """HU-09: turn a 'new' mention into a clinic of the market (with aliases)."""
    _, market_id = _mention_in_run(conn, run_id, mention_id)
    with conn.cursor() as cur:
        cur.execute("select raw_name from public.mentions where id = %s", (mention_id,))
        (raw_name,) = cur.fetchone()
    name = (name or raw_name).strip()
    with conn.transaction(), conn.cursor() as cur:
        cur.execute("insert into public.clinics (name) values (%s) returning id", (name,))
        (clinic_id,) = cur.fetchone()
        cur.execute(
            "insert into public.clinic_markets (clinic_id, market_id) values (%s, %s)",
            (clinic_id, market_id),
        )
        _set(cur, mention_id, status="corrected", clinic_id=clinic_id, note="clínica creada")
    add_derived_aliases(conn, clinic_id, name)
    if fold(raw_name) != fold(name):
        add_alias(conn, clinic_id, raw_name)
    return clinic_id


def discard(conn: psycopg.Connection, run_id: int, mention_id: int) -> None:
    _mention_in_run(conn, run_id, mention_id)
    with conn.transaction(), conn.cursor() as cur:
        _set(cur, mention_id, status="discarded")


def merge(conn: psycopg.Connection, run_id: int, mention_id: int, into_id: int) -> None:
    """Two mentions of the same clinic in one answer: keep `into_id` at the earlier position."""
    response_a, _ = _mention_in_run(conn, run_id, mention_id)
    response_b, _ = _mention_in_run(conn, run_id, into_id)
    if response_a != response_b or mention_id == into_id:
        raise ReviewError("Solo se unen dos menciones distintas de la misma respuesta")
    with conn.transaction(), conn.cursor() as cur:
        cur.execute(
            "select id, position from public.mentions where id in (%s, %s)", (mention_id, into_id)
        )
        positions = dict(cur.fetchall())
        if positions[mention_id] < positions[into_id]:
            # The kept mention takes the earlier position; the merged one is discarded.
            cur.execute(
                "update public.mentions set position = case id when %s then %s else %s end "
                "where id in (%s, %s)",
                (into_id, positions[mention_id], positions[into_id], mention_id, into_id),
            )
        _set(cur, mention_id, status="discarded", note=f"unida con {into_id}")
        cur.execute(
            "update public.mentions set status = 'corrected', updated_at = now() "
            "where id = %s and status = 'review'",
            (into_id,),
        )


def confirm(conn: psycopg.Connection, run_id: int, mention_id: int) -> None:
    """Accept the automatic result; a mention in review needs a clinic first."""
    _mention_in_run(conn, run_id, mention_id)
    with conn.cursor() as cur:
        cur.execute("select status from public.mentions where id = %s", (mention_id,))
        (status,) = cur.fetchone()
    if status == "review":
        raise ReviewError(
            f"La mención {mention_id} está en revisión: asóciala, créala o descártala"
        )


# --- CSV (review in Excel) -----------------------------------------------------------------


def export_csv(conn: psycopg.Connection, run_id: int, path: Path) -> int:
    rows = run_mentions(conn, run_id)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=EXPORT_COLUMNS)
        writer.writeheader()
        for r in rows:
            writer.writerow(
                {
                    "mention_id": r.mention_id,
                    "response_id": r.response_id,
                    "surface": r.surface,
                    "template_id": r.template_id,
                    "repetition": r.repetition,
                    "position": r.position,
                    "raw_name": r.raw_name,
                    "clinic_id": r.clinic_id or "",
                    "clinic_name": r.clinic_name or "",
                    "status": r.status,
                    "accion": "",
                    "clinica_destino": "",
                    "unir_con": "",
                    "nombre_nueva": "",
                    "extracto": _excerpt(r.text, r.raw_name),
                }
            )
    return len(rows)


def apply_csv(conn: psycopg.Connection, run_id: int, path: Path) -> ApplyResult:
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    return apply_corrections(conn, run_id, rows)


def apply_corrections(conn: psycopg.Connection, run_id: int, rows: list[dict]) -> ApplyResult:
    """Apply the 'accion' column: ok, asociar (clinica_destino), nueva (nombre_nueva
    optional), descartar, unir (unir_con). Empty rows are left as they are."""
    result = ApplyResult()
    for n, row in enumerate(rows, start=2):
        action = (row.get("accion") or "").strip().lower()
        if not action:
            continue
        try:
            mention_id = int(row["mention_id"])
            if action == "ok":
                confirm(conn, run_id, mention_id)
            elif action == "asociar":
                associate(conn, run_id, mention_id, int(row["clinica_destino"]))
            elif action == "nueva":
                clinic_id = create_clinic_for(conn, run_id, mention_id, row.get("nombre_nueva"))
                result.clinics_created.append(
                    f"{clinic_id}: {row.get('nombre_nueva') or row.get('raw_name')}"
                )
            elif action == "descartar":
                discard(conn, run_id, mention_id)
            elif action == "unir":
                merge(conn, run_id, mention_id, int(row["unir_con"]))
            else:
                raise ReviewError(f"acción desconocida '{action}' (usa {', '.join(ACTIONS[1:])})")
        except (ReviewError, ValueError, KeyError) as exc:
            result.errors.append(f"fila {n}: {exc}")
            continue
        result.by_action[action] += 1
    return result


# --- HU-09 and closing ---------------------------------------------------------------------


def new_clinics(conn: psycopg.Connection, market_id: int) -> list[tuple[str, int, int]]:
    """Unmatched names in the market's runs: (name, answers where it appears, mentions)."""
    with conn.cursor() as cur:
        cur.execute(
            "select m.raw_name, m.response_id from public.mentions m "
            "join public.responses r on r.id = m.response_id "
            "join public.runs ru on ru.id = r.run_id "
            "where ru.market_id = %s and m.clinic_id is null and m.status = 'auto'",
            (market_id,),
        )
        rows = cur.fetchall()
    groups: dict[str, dict] = {}
    for raw_name, response_id in rows:
        g = groups.setdefault(fold(raw_name), {"name": raw_name, "responses": set(), "n": 0})
        g["responses"].add(response_id)
        g["n"] += 1
    out = [(g["name"], len(g["responses"]), g["n"]) for g in groups.values()]
    return sorted(out, key=lambda t: (-t[1], fold(t[0])))


def pending_review(conn: psycopg.Connection, run_id: int) -> int:
    with conn.cursor() as cur:
        cur.execute(
            "select count(*) from public.mentions m join public.responses r "
            "on r.id = m.response_id where r.run_id = %s and m.status = 'review'",
            (run_id,),
        )
        return cur.fetchone()[0]


def close_review(conn: psycopg.Connection, run_id: int) -> None:
    left = pending_review(conn, run_id)
    if left:
        raise ReviewError(f"Quedan {left} menciones en revisión")
    with conn.cursor() as cur:
        cur.execute(
            "select count(*) from public.responses where run_id = %s and extracted_at is null",
            (run_id,),
        )
        (not_extracted,) = cur.fetchone()
    if not_extracted:
        raise ReviewError(f"Quedan {not_extracted} respuestas sin extraer")
    with conn.transaction(), conn.cursor() as cur:
        cur.execute("update public.runs set status = 'reviewed' where id = %s", (run_id,))


def _excerpt(text: str, name: str, width: int = 90) -> str:
    flat = " ".join(text.split())
    where = flat.lower().find(name.lower()) if name else -1
    if where < 0:
        return flat[:width]
    start = max(where - width // 3, 0)
    return flat[start : start + width]
