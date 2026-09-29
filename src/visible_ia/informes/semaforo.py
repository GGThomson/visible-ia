"""Traffic light, findings and action plan of the free diagnostic (redesign 28/09/2026).

All pure functions over one `Facts` built once from the data the diagnostic already loads (no
new runs): the traffic light, the findings, the action plan and page 5 read the same numbers,
so they cannot contradict each other (tested in tests/unit/test_semaforo.py).

Each area compares the clinic's figure with the leader's (29/09/2026): "Bien" from 80 % of the
leader's figure, "Regular" from 40 %, "Bajo" below; "Sin datos" when the leader is at 0. The
cut-offs live in semaforo.toml ("criterio Eminia").
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
RULES_TOML = HERE / "semaforo.toml"
LEVELS = ("Bien", "Regular", "Bajo", "Sin datos")


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


def load_rules(path: Path = RULES_TOML) -> dict:
    """{"corte": {"bien": 0.8, "regular": 0.4}, "areas": {id: {...}}}."""
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return {"corte": data["corte"], "areas": {a["id"]: a for a in data["area"]}}


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


def compared_level(mine: float | None, ref: float | None, cuts: dict) -> str:
    """The clinic's figure as a share of the leader's: "Bien" from `bien` (0.8), "Regular" from
    `regular` (0.4), "Bajo" below. No figure, or a leader at 0, is "Sin datos"."""
    if mine is None or not ref:
        return "Sin datos"
    ratio = mine / ref
    return "Bien" if ratio >= cuts["bien"] else "Regular" if ratio >= cuts["regular"] else "Bajo"


def share(k: int, n: int) -> float | None:
    return 100 * k / n if n else None


def lights(facts: Facts, rules: dict | None = None) -> list[Light]:
    """The 4 areas, each with one line: 'Te nombra en 25 % · el líder 50 %'."""
    rules = rules or load_rules()
    r, cuts = rules["areas"], rules["corte"]
    me, ref, vs = facts.me, facts.ref, facts.ref_label
    n = facts.total if facts.has_answers else 0

    web_me = share(me.web, n)
    web_ref = share(ref.web, n) if ref else None
    dir_me = (share(me.directories, me.named) or 0.0) if facts.has_answers else None
    dir_ref = share(ref.directories, ref.named) if ref and facts.has_answers else None

    def line(what: str, mine, theirs) -> str:
        out = f"{what} {pct(mine)}"
        return f"{out} · {vs} {pct(theirs)}" if theirs is not None else out

    maps_line = "—"
    if me.rating is not None:
        maps_line = f"{dec(me.rating)} ★ y {thousands(me.reviews or 0)} reseñas"
        if ref and ref.rating is not None:
            maps_line += f" · {vs} {dec(ref.rating)} ★ y {thousands(ref.reviews or 0)}"
    ref_index = ref.index if ref else None
    ref_reviews = ref.reviews if ref and ref.rating is not None else None
    my_reviews = me.reviews if me.rating is not None else None
    return [
        Light("presencia", r["presencia"]["nombre"],
              compared_level(me.index, ref_index, cuts),
              line("Te nombra en", me.index, ref_index)),
        Light("web", r["web"]["nombre"], compared_level(web_me, web_ref, cuts),
              line("Cita tu web en", web_me, web_ref)),
        Light("directorios", r["directorios"]["nombre"],
              compared_level(dir_me, dir_ref, cuts),
              line("Cita Doctoralia o directorios en", dir_me, dir_ref)),
        # Maps compares the number of reviews: stars barely differ between clinics.
        Light("maps", r["maps"]["nombre"],
              compared_level(my_reviews, ref_reviews, cuts), maps_line),
    ]  # fmt: skip


# --- action plan -----------------------------------------------------------------------------


# What each fix's impact measures. Fixes that share a measure show the same difference, so the
# plan keeps only one of them (29/09/2026).
GAP_MEASURE = {"resenas": "presencia", "brecha": "presencia"}


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
            # Same measure as the traffic light: share of the answers that name each clinic.
            "doctoralia": points(
                share(ref.directories, ref.named), share(me.directories, me.named), facts.total
            ),
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
