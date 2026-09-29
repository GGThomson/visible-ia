"""Traffic light, findings and action plan of the free diagnostic (redesign 28/09/2026).

All pure functions over one `Facts` built once from the data the diagnostic already loads (no
new runs): the traffic light, the findings, the action plan and page 5 read the same numbers,
so they cannot contradict each other (tested in tests/unit/test_semaforo.py).

Each area is compared with the leader (29/09/2026): "Bien" only when the clinic's range reaches
the leader's; otherwise the fixed thresholds of semaforo.toml ("criterio Eminia") split
"Regular" from "Bajo".
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path

from visible_ia.puntaje.estadistica import wilson

HERE = Path(__file__).resolve().parent
RULES_TOML = HERE / "semaforo.toml"
LEVELS = ("Bien", "Regular", "Bajo", "Sin datos")
# Which areas each fix of recomendaciones.toml improves. A fix is only proposed when one of its
# areas is not "Bien" ("mantener" has none: it is advice for clinics already doing well).
FIX_AREAS = {
    "web": ("web",),
    "google": ("presencia", "maps"),
    "resenas": ("maps",),
    "doctoralia": ("directorios",),
    "chatgpt": ("directorios", "presencia"),
    "brecha": ("presencia", "web"),
    "mantener": (),
}


@dataclass(frozen=True)
class Side:
    """One clinic's figures for the 4 areas. Percentages are 0–100."""

    index: float | None = None
    index_low: float | None = None
    index_high: float | None = None
    chatgpt: float | None = None
    google: float | None = None
    web: int = 0  # answers citing its own website
    named: int = 0  # answers naming it
    directories: int = 0  # of those, answers citing Doctoralia or a directory
    rating: float | None = None
    reviews: int | None = None


@dataclass(frozen=True)
class Facts:
    total: int  # answers of the month
    me: Side
    ref: Side | None  # the leader (the runner-up when the clinic leads)
    ref_label: str = "el líder"
    has_web: bool = True
    has_answers: bool = True  # False: only the aggregated citations are known
    per_surface: int = 0  # answers per surface (ChatGPT or Google)


@dataclass(frozen=True)
class Light:
    id: str
    name: str
    level: str  # one of LEVELS
    value: str  # one line: what it measures, the clinic and the leader


def load_rules(path: Path = RULES_TOML) -> dict[str, dict]:
    return {a["id"]: a for a in tomllib.loads(path.read_text(encoding="utf-8"))["area"]}


# --- number format: the same everywhere in the report ---------------------------------------


def pct(value: float | None) -> str:
    """Whole percentage, no decimals: '25 %'."""
    return "—" if value is None else f"{value:.0f} %"  # no break between number and %


def dec(value: float | None) -> str:
    """One decimal with a comma, Peruvian style: '4,9'."""
    return "—" if value is None else f"{value:.1f}".replace(".", ",")


def thousands(value: int | None) -> str:
    """Thousands with a space: '1 135'."""
    return "—" if value is None else f"{value:,}".replace(",", " ")


def one_in(value: float | None) -> str:
    """'1 de cada 4 veces' / '6 de cada 10 veces' / 'ninguna vez'."""
    if not value:
        return "ninguna vez"
    if value >= 50:
        return f"{round(value / 10)} de cada 10 veces"
    return f"1 de cada {round(100 / value)} veces"


# --- levels ----------------------------------------------------------------------------------


def level(value: float | None, good: float, fair: float) -> str:
    """Fixed thresholds: used when there is no leader to compare with."""
    if value is None:
        return "Sin datos"
    return "Bien" if value >= good else "Regular" if value >= fair else "Bajo"


def compared_level(
    mine: tuple[float, float, float] | None,
    ref: tuple[float, float, float] | None,
    rule: dict,
) -> str:
    """(value, low, high) against the leader's: "Bien" when the clinic's range reaches the
    leader's range (or it is above); never "Bien" at 0 %."""
    if mine is None:
        return "Sin datos"
    value, _, high = mine
    if ref is None:
        return level(value, rule["bien"], rule["regular"])
    if value > 0 and high >= ref[1]:
        return "Bien"
    return "Regular" if value >= rule["regular"] else "Bajo"


def maps_level(rating: float | None, reviews: int | None, rule: dict,
               ref: Side | None = None) -> str:  # fmt: skip
    if rating is None or reviews is None:
        return "Sin datos"
    if ref is not None and ref.rating is not None and ref.reviews is not None:
        good = (rating >= ref.rating - rule["margen_estrellas"]
                and reviews >= ref.reviews * rule["fraccion_resenas"])  # fmt: skip
    else:
        good = rating >= rule["bien_estrellas"] and reviews >= rule["bien_resenas"]
    if good:
        return "Bien"
    if rating >= rule["regular_estrellas"] and reviews >= rule["regular_resenas"]:
        return "Regular"
    return "Bajo"


def share_range(k: int, n: int) -> tuple[float, float, float] | None:
    interval = wilson(k, n)
    return None if interval is None else (100 * k / n, 100 * interval[0], 100 * interval[1])


def _index_range(s: Side) -> tuple[float, float, float] | None:
    if s.index is None:
        return None
    low = s.index if s.index_low is None else s.index_low
    high = s.index if s.index_high is None else s.index_high
    return (s.index, low, high)


def lights(facts: Facts, rules: dict[str, dict] | None = None) -> list[Light]:
    """The 4 areas, each with one line: '25 % · el líder 50 %'."""
    r = rules or load_rules()
    me, ref, vs = facts.me, facts.ref, facts.ref_label
    n = facts.total if facts.has_answers else 0

    web_me = share_range(me.web, n)
    if web_me is None and n and not facts.has_web:
        web_me = (0.0, 0.0, 0.0)
    web_ref = share_range(ref.web, n) if ref else None
    dir_me = share_range(me.directories, me.named) if facts.has_answers else None
    if dir_me is None and facts.has_answers:
        dir_me = (0.0, 0.0, 0.0)  # never named: nothing to cite it with
    dir_ref = share_range(ref.directories, ref.named) if ref else None

    def line(what: str, mine, theirs) -> str:
        out = f"{what} {pct(mine[0]) if mine else '—'}"
        return f"{out} · {vs} {pct(theirs[0])}" if theirs else out

    def maps_text(s: Side) -> str:
        return f"{dec(s.rating)} ★ y {thousands(s.reviews or 0)} reseñas"

    maps_line = "—" if me.rating is None else maps_text(me)
    if me.rating is not None and ref and ref.rating is not None:
        maps_line += f" · {vs} {dec(ref.rating)} ★ y {thousands(ref.reviews or 0)}"
    return [
        Light("presencia", r["presencia"]["nombre"],
              compared_level(_index_range(me), ref and _index_range(ref), r["presencia"]),
              line("Te nombra en", _index_range(me), ref and _index_range(ref))),
        Light("web", r["web"]["nombre"], compared_level(web_me, web_ref, r["web"]),
              line("Cita tu web en", web_me, web_ref)),
        Light("directorios", r["directorios"]["nombre"],
              compared_level(dir_me, dir_ref, r["directorios"]),
              line("Cita Doctoralia o directorios en", dir_me, dir_ref)),
        Light("maps", r["maps"]["nombre"],
              maps_level(me.rating, me.reviews, r["maps"], ref), maps_line),
    ]  # fmt: skip


# --- action plan -----------------------------------------------------------------------------


def gap(fix_id: str, facts: Facts) -> int:
    """How many answers of the month the fix's area separates the clinic from the leader."""
    me, ref = facts.me, facts.ref
    if ref is None or fix_id == "mantener":
        return 0

    def points(a, b, n):
        return max(round(((a or 0) - (b or 0)) * n / 100), 0)

    per_surface = facts.per_surface or facts.total // 2
    return max(
        {
            "web": ref.web - me.web,
            "doctoralia": ref.directories - me.directories,
            "google": points(ref.google, me.google, per_surface),
            "chatgpt": points(ref.chatgpt, me.chatgpt, per_surface),
            "resenas": points(ref.index, me.index, facts.total),
            "brecha": points(ref.index, me.index, facts.total),
        }.get(fix_id, 0),
        0,
    )


def impact(answers: int, total: int) -> str:
    if total and answers * 6 >= total:  # 10 of 60 or more
        return "alto"
    if total and answers * 20 >= total:  # 3 of 60 or more
        return "medio"
    return "bajo"


def allowed(fix_id: str, by_area: dict[str, str]) -> bool:
    """A fix is proposed only if it improves an area that is not already "Bien"."""
    areas = FIX_AREAS.get(fix_id, ())
    return not areas or any(by_area.get(a) != "Bien" for a in areas)


# --- findings --------------------------------------------------------------------------------


def findings(
    *,
    clinic: str,
    appearances: int,
    total: int,
    leader: str,
    leader_appearances: int,
    is_leader: bool,
    rating: float | None,
    reviews: int | None,
    web_answers: int,
    chatgpt: float | None,
    google: float | None,
) -> list[str]:
    """Three one-line findings with real figures, in priority order."""
    out = []
    if rating is not None and reviews and rating >= 4.5 and total and appearances * 10 <= total:
        out.append(
            f"Tienes {dec(rating)} ★ y {thousands(reviews)} reseñas en Google Maps, pero la IA "
            f"te nombra en {appearances} de {total} respuestas."
        )
    if is_leader:
        out.append(f"Eres la clínica más nombrada: la IA te recomienda en {appearances} de {total} "
                   "respuestas.")  # fmt: skip
    else:
        out.append(
            f"{leader} aparece en {leader_appearances} de {total} respuestas; {clinic}, "
            f"en {appearances}."
        )
    out.append(
        f"Tu web se citó como fuente en {web_answers} de {total} respuestas."
        if web_answers
        else "Tu web no apareció como fuente en ninguna respuesta."
    )
    if chatgpt is not None and google is not None and abs(chatgpt - google) >= 10:
        strong, weak = ("ChatGPT", "Google") if chatgpt > google else ("Google", "ChatGPT")
        out.append(
            f"Te va mejor en {strong} ({pct(max(chatgpt, google))}) que en {weak} "
            f"({pct(min(chatgpt, google))})."
        )
    return out[:3]
