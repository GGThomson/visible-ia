"""Monthly report of a site (C8-T02, HU-15): evolution, ADR-003 change, 3-month window,
competitors, sources, checklist, patients who came through the AI (C9-T02) and calibration
with the apps (PRD §5.4).

`build_monthly_context` is pure (tested with 1, 2 and 3 months of data); `load_monthly_data`
reads a site's scores from the database.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Any

import psycopg

from visible_ia.atribucion import load_counts
from visible_ia.informes.contexto import TREATMENT, load_brand, month_text
from visible_ia.puntaje.calibracion import Calibration, calibration_with_alert
from visible_ia.puntaje.fuentes import TYPE_LABELS, load_citations, top_sources, type_shares

CHANGE_TEXT = {
    "up": "subió frente al mes anterior",
    "down": "bajó frente al mes anterior",
    "no_clear_change": "no tuvo un cambio claro frente al mes anterior",
    "first_month": "es el primer mes medido",
}


@dataclass(frozen=True)
class MonthScore:
    month: date
    combined: float
    ci_low: float | None
    ci_high: float | None
    chatgpt: float | None
    google: float | None
    window3: float | None
    window3_low: float | None
    window3_high: float | None
    change: str | None
    detectable: float | None
    n_responses: int


@dataclass
class MonthlyData:
    site_id: int
    clinic_id: int
    clinic_name: str
    category: str
    district: str
    month: date
    history: list[MonthScore]  # this site, oldest first, up to `month`
    ranking: list[dict[str, Any]]  # this month: clinic_id, name, combined, previous
    citations: list[tuple[int, str, str, str]]
    total_answers: int
    tasks: list[dict[str, Any]]  # title, status
    calibration: list[Calibration] = field(default_factory=list)
    calibration_alert: bool = False
    ai_patients: dict[date, int] = field(default_factory=dict)  # month -> count, oldest first


def _pct(value: float | None) -> str:
    return "—" if value is None else f"{value:.0f}"


def build_monthly_context(data: MonthlyData, brand: dict[str, str] | None = None) -> dict[str, Any]:
    brand = brand or load_brand()
    current = next((h for h in data.history if h.month == data.month), None)
    if current is None:
        raise ValueError(f"La sede {data.site_id} no tiene puntaje en {data.month:%Y-%m}")
    previous = ([h for h in data.history if h.month < data.month] or [None])[-1]
    ranked = sorted(data.ranking, key=lambda r: -(r["combined"] or 0))
    position = [r["clinic_id"] for r in ranked].index(data.clinic_id) + 1
    mine = ranked[position - 1]
    competitors = [r for r in ranked if r["clinic_id"] != data.clinic_id][:3]
    shown = sorted([mine, *competitors], key=lambda r: -(r["combined"] or 0))

    change = CHANGE_TEXT.get(current.change or "", "")
    sentence = (
        f"Este mes la IA nombró a {data.clinic_name} en {_pct(current.combined)} % de las "
        f"respuestas (entre {_pct(current.ci_low)} % y {_pct(current.ci_high)} %): {change}."
    )
    if current.change == "no_clear_change" and current.detectable:
        sentence += (
            f" Con estos datos, un cambio menor a {_pct(current.detectable)} puntos no se "
            "distingue del azar."
        )

    shares = type_shares(data.citations, data.total_answers)
    top = top_sources(data.citations, data.total_answers, per_type=3)
    top_rows = sorted(
        (r for rows in top.values() for r in rows if r.source_type != "google_profile"),
        key=lambda r: -r.answers,
    )[:6]
    counts = {m: n for m, n in data.ai_patients.items() if m <= data.month}
    done = [t for t in data.tasks if t["status"] == "done"]
    pending = [t for t in data.tasks if t["status"] != "done"]

    return {
        "marca": brand,
        "clinica": {"nombre": data.clinic_name, "posicion": position, "total": len(ranked)},
        "mercado": {
            "tratamiento": TREATMENT.get(data.category, "tu especialidad"),
            "distrito": data.district,
            "mes": month_text(data.month),
        },
        "frase": sentence,
        "actual": {
            "combinado": _pct(current.combined),
            "bajo": _pct(current.ci_low),
            "alto": _pct(current.ci_high),
            "chatgpt": _pct(current.chatgpt),
            "google": _pct(current.google),
            "detectable": _pct(current.detectable),
            "cambio": current.change or "first_month",
        },
        "ventana": {
            "meses": len([h for h in data.history if h.month <= data.month][-3:]),
            "indice": _pct(current.window3),
            "bajo": _pct(current.window3_low),
            "alto": _pct(current.window3_high),
        },
        "evolucion": [
            {
                "mes": month_text(h.month),
                "combinado": _pct(h.combined),
                "rango": f"{_pct(h.ci_low)}–{_pct(h.ci_high)}",
                "ventana": _pct(h.window3),
                "cambio": {
                    "up": "sube",
                    "down": "baja",
                    "no_clear_change": "sin cambio claro",
                    "first_month": "primer mes",
                }.get(h.change or "", "—"),  # fmt: skip
                "ancho": max(h.combined, 0.5),
            }
            for h in data.history
            if h.month <= data.month
        ][-6:],
        "anterior": None if previous is None else {"mes": month_text(previous.month)},
        "competidores": [
            {
                "nombre": r["name"],
                "es_cliente": r["clinic_id"] == data.clinic_id,
                "actual": _pct(r["combined"]),
                "anterior": _pct(r.get("previous")),
                "ancho": max(r["combined"] or 0, 0.5),
            }
            for r in shown
        ],
        "fuentes": {
            "tipos": [
                {"nombre": TYPE_LABELS[t], "pct": _pct(p)}
                for t, p in shares.items()
                if t != "google_profile"
            ],
            "top": [
                {"dominio": r.domain, "tipo": TYPE_LABELS[r.source_type], "pct": _pct(r.share)}
                for r in top_rows
            ],
        },
        "tareas": {
            "hechas": [t["title"] for t in done],
            "pendientes": [t["title"] for t in pending],
        },
        "atribucion": {
            "este_mes": counts.get(data.month),
            "historial": [
                {"mes": month_text(m), "pacientes": n} for m, n in sorted(counts.items())
            ][-6:],
        },
        "calibracion": [
            {
                "app": c.app,
                "respuestas": c.answers,
                "coincidencia": _pct(c.coincidence),
                "mismo_lider": c.same_leader,
                "lider_app": c.leader_app or "—",
                "lider_api": c.leader_api or "—",
            }
            for c in data.calibration
        ],
        "alerta_calibracion": data.calibration_alert,
        "metodo": {"respuestas": current.n_responses, "mes": month_text(data.month)},
    }


# --- database ------------------------------------------------------------------------------


def _f(value) -> float | None:
    return None if value is None else float(value)


def load_monthly_data(conn: psycopg.Connection, site_id: int, month: date) -> MonthlyData:
    with conn.cursor() as cur:
        cur.execute(
            "select s.clinic_id, c.name, m.id, m.category_code, m.district from public.sites s "
            "join public.clinics c on c.id = s.clinic_id "
            "join public.markets m on m.id = s.market_id "
            "where s.id = %s",
            (site_id,),
        )
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"No existe la sede {site_id}")
        clinic_id, clinic_name, market_id, category, district = row
        cur.execute(
            "select c.month, c.presence_index, c.ci_low, c.ci_high, g.presence_index, "
            "o.presence_index, c.window3_index, c.window3_ci_low, c.window3_ci_high, c.change, "
            "c.detectable_diff, c.n_responses, g.n_responses, o.n_responses "
            "from public.monthly_scores c "
            "left join public.monthly_scores g on g.market_id = c.market_id and g.month = c.month "
            "and g.clinic_id = c.clinic_id and g.surface = 'chatgpt_api' "
            "left join public.monthly_scores o on o.market_id = c.market_id and o.month = c.month "
            "and o.clinic_id = c.clinic_id and o.surface = 'google_ai_mode' "
            "where c.market_id = %s and c.clinic_id = %s and c.surface = 'combined' "
            "and c.month <= %s order by c.month",
            (market_id, clinic_id, month),
        )
        history = [
            MonthScore(
                r[0],
                float(r[1]),
                _f(r[2]),
                _f(r[3]),
                _f(r[4]) if r[12] else None,
                _f(r[5]) if r[13] else None,
                _f(r[6]),
                _f(r[7]),
                _f(r[8]),
                r[9],
                _f(r[10]),
                r[11],
            )  # fmt: skip
            for r in cur.fetchall()
        ]
        cur.execute(
            "select s.clinic_id, c.name, s.presence_index, p.presence_index "
            "from public.monthly_scores s join public.clinics c on c.id = s.clinic_id "
            "left join public.monthly_scores p on p.market_id = s.market_id "
            "and p.clinic_id = s.clinic_id and p.surface = 'combined' "
            "and p.month = (s.month - interval '1 month')::date "
            "where s.market_id = %s and s.month = %s and s.surface = 'combined'",
            (market_id, month),
        )
        ranking = [
            {"clinic_id": cid, "name": name, "combined": _f(now), "previous": _f(prev)}
            for cid, name, now, prev in cur.fetchall()
        ]
        cur.execute(
            "select coalesce(title, code), status from public.tasks where site_id = %s "
            "order by priority, id",
            (site_id,),
        )
        tasks = [{"title": t, "status": s} for t, s in cur.fetchall()]
    citations, total = load_citations(conn, market_id, month)
    calibration, alert = calibration_with_alert(conn, market_id, month)
    return MonthlyData(
        site_id, clinic_id, clinic_name, category, district, month, history, ranking,
        citations, total, tasks, calibration, alert, load_counts(conn, site_id, month),
    )  # fmt: skip
