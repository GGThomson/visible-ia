"""Traffic light, findings and action plan of the free diagnostic (redesign 28/09/2026).

All pure functions over data the diagnostic already loads (no new runs). The thresholds live in
semaforo.toml ("criterio Eminia"); effort per fix lives in recomendaciones.toml.
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
RULES_TOML = HERE / "semaforo.toml"
LEVELS = ("Bien", "Regular", "Bajo", "Sin datos")
# Which areas each fix of recomendaciones.toml improves: its impact is "alto" when one of them
# is "Bajo", "medio" otherwise.
FIX_AREAS = {
    "web": ("web",),
    "google": ("presencia", "maps"),
    "resenas": ("maps",),
    "doctoralia": ("directorios",),
    "chatgpt": ("directorios", "presencia"),
    "brecha": ("presencia", "web"),
    "mantener": ("presencia",),
}


@dataclass(frozen=True)
class Light:
    id: str
    name: str
    measures: str
    level: str  # one of LEVELS
    value: str  # what the clinic has, for the tooltip-free PDF ("12 %", "4.9 ★ · 1135 reseñas")


def load_rules(path: Path = RULES_TOML) -> dict[str, dict]:
    return {a["id"]: a for a in tomllib.loads(path.read_text(encoding="utf-8"))["area"]}


def level(value: float | None, good: float, fair: float) -> str:
    if value is None:
        return "Sin datos"
    return "Bien" if value >= good else "Regular" if value >= fair else "Bajo"


def maps_level(rating: float | None, reviews: int | None, rule: dict) -> str:
    if rating is None or reviews is None:
        return "Sin datos"
    if rating >= rule["bien_estrellas"] and reviews >= rule["bien_resenas"]:
        return "Bien"
    if rating >= rule["regular_estrellas"] and reviews >= rule["regular_resenas"]:
        return "Regular"
    return "Bajo"


def lights(
    index: float | None,
    web_share: float | None,
    directory_share: float | None,
    rating: float | None,
    reviews: int | None,
    rules: dict[str, dict] | None = None,
) -> list[Light]:
    """The 4 areas. Shares are 0–100; web_share is 0 when the clinic has no website."""
    rules = rules or load_rules()

    def pct(v):
        return "—" if v is None else f"{v:.0f} %"

    r = rules
    maps_value = "—" if rating is None else f"{rating:.1f} ★ · {reviews or 0} reseñas"
    return [
        Light("presencia", r["presencia"]["nombre"], r["presencia"]["mide"],
              level(index, r["presencia"]["bien"], r["presencia"]["regular"]), pct(index)),
        Light("web", r["web"]["nombre"], r["web"]["mide"],
              level(web_share, r["web"]["bien"], r["web"]["regular"]), pct(web_share)),
        Light("directorios", r["directorios"]["nombre"], r["directorios"]["mide"],
              level(directory_share, r["directorios"]["bien"], r["directorios"]["regular"]),
              pct(directory_share)),
        Light("maps", r["maps"]["nombre"], r["maps"]["mide"],
              maps_level(rating, reviews, r["maps"]), maps_value),
    ]  # fmt: skip


def impact(fix_id: str, by_area: dict[str, str]) -> str:
    return "alto" if any(by_area.get(a) == "Bajo" for a in FIX_AREAS.get(fix_id, ())) else "medio"


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
            f"Tienes {rating:.1f} ★ y {reviews:,} reseñas en Google Maps, pero la IA te nombra "
            f"en {appearances} de {total} respuestas."
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
            f"Te va mejor en {strong} ({max(chatgpt, google):.0f} %) que en {weak} "
            f"({min(chatgpt, google):.0f} %)."
        )
    return out[:3]
