"""Batch of free diagnostics (C-010): a list of names in, one PDF and one WhatsApp message each.

Only stored data (no new runs). The vocabulary comes from nicho.toml and the signature from
marca.toml: this module does not name the business or its customers itself (a test checks it).

The message carries ONE fact, the strongest of three, in plain words (no index, range or
sources): a good Maps reputation the AI ignores, one assistant much stronger than the other,
or the comparison with the leader.
"""

from dataclasses import dataclass

from visible_ia.informes.contexto import ReportData
from visible_ia.informes.semaforo import dec, thousands
from visible_ia.mercados.alias import fold
from visible_ia.nicho import Niche
from visible_ia.puntaje.brecha import has_gap

# (surface code, label in the message, attribute of the ranking row)
SURFACES = (("chatgpt_api", "ChatGPT", "chatgpt"), ("google_ai_mode", "Google", "google"))
# One assistant counts as "much stronger" when it names the business 3 times as often and in
# at least 5 more answers.
SPLIT_RATIO = 3
SPLIT_MIN_DIFF = 5


class UnknownName(ValueError):
    """A line of the list that matches no establishment, or more than one."""


def read_list(text: str) -> list[str]:
    """One name (or id) per line; blank lines and lines starting with # are skipped."""
    return [x.strip() for x in text.splitlines() if x.strip() and not x.strip().startswith("#")]


def match(line: str, market_names: dict[int, list[str]]) -> int:
    """The id of the establishment a line refers to: its id, its exact name or alias, or the
    only one whose name contains the line as whole words."""
    if line.isdigit():
        if int(line) in market_names:
            return int(line)
        raise UnknownName(f"«{line}»: no hay ningún id {line} en el mercado")
    wanted = fold(line)
    exact = {cid for cid, names in market_names.items() if wanted in {fold(n) for n in names}}
    found = exact or {
        cid
        for cid, names in market_names.items()
        if any(f" {wanted} " in f" {fold(n)} " for n in names)
    }
    if len(found) == 1:
        return found.pop()
    if not found:
        raise UnknownName(f"«{line}»: no está en el mercado")
    options = ", ".join(sorted(f"{market_names[c][0]} ({c})" for c in found))
    raise UnknownName(f"«{line}»: coincide con varios: {options}. Usa el id.")


@dataclass(frozen=True)
class Standing:
    """What the message can say about one establishment, in answers (not percentages)."""

    name: str
    total: int
    appearances: int
    by_surface: tuple[tuple[str, int, int], ...]  # (label, answers naming it, answers)
    ref_name: str  # the leader, or the runner-up when it leads
    ref_appearances: int
    leads: bool
    rating: float | None
    reviews: int | None
    index: float


def standing(data: ReportData) -> Standing:
    rows = {r.clinic_id: r for r in data.ranking}
    me = rows[data.clinic.id]
    others = [r for r in data.ranking if r.clinic_id != me.clinic_id]
    leads = data.ranking[0].clinic_id == me.clinic_id
    ref = (others[0] if others else me) if leads else data.ranking[0]
    total = data.total_answers

    def answers(pct: float | None, n: int) -> int:
        return round((pct or 0) * n / 100)

    by_surface = []
    for code, label, field in SURFACES:
        n = sum(1 for a in data.deep_answers if a.surface == code) or total // 2
        by_surface.append((label, answers(getattr(me, field), n), n))
    return Standing(
        name=data.clinic.name,
        total=total,
        appearances=answers(me.combined, total),
        by_surface=tuple(by_surface),
        ref_name=ref.name,
        ref_appearances=answers(ref.combined, total),
        leads=leads,
        rating=data.clinic.rating,
        reviews=data.clinic.reviews,
        index=me.combined or 0,
    )


def _times(k: int, n: int) -> str:
    return f"en ninguna de las {n}" if k == 0 else f"en {k} de las {n}"


def _only(k: int, n: int) -> str:
    return f"no apareció en ninguna de las {n}" if k == 0 else f"solo apareció en {k} de las {n}"


def strongest_fact(s: Standing) -> tuple[str, str]:
    """(kind, sentence): "reputacion", "asistente" or "lider"."""
    if has_gap(s.rating, s.reviews, s.index):
        return "reputacion", (
            f"{s.name} tiene {dec(s.rating)} estrellas y {thousands(s.reviews)} reseñas en "
            f"Google Maps, pero {_only(s.appearances, s.total)} respuestas."
        )
    (a_label, a_k, a_n), (b_label, b_k, b_n) = sorted(s.by_surface, key=lambda x: -x[1])
    if a_k >= SPLIT_RATIO * b_k and a_k - b_k >= SPLIT_MIN_DIFF:
        return "asistente", (
            f"{s.name} apareció en {a_k} de {a_n} respuestas de {a_label}, pero "
            f"{'en ninguna' if b_k == 0 else f'solo en {b_k}'} de las {b_n} de {b_label}."
        )
    if s.leads:
        return "lider", (
            f"{s.name} encabeza la lista: apareció {_times(s.appearances, s.total)} "
            f"respuestas; {s.ref_name}, en {s.ref_appearances}."
        )
    return "lider", (
        f"{s.name} apareció {_times(s.appearances, s.total)} respuestas; {s.ref_name}, "
        f"que encabeza la lista, en {s.ref_appearances}."
    )


def whatsapp_message(data: ReportData, niche: Niche, brand: dict[str, str]) -> str:
    """Short first message: who writes, what was asked, one fact, the offer."""
    s = standing(data)
    _, fact = strongest_fact(s)
    return (
        f"Hola, soy {brand['firma']}. Pregunté {s.total} veces a ChatGPT y a Google por "
        f"{niche.category(data.category)} en {data.district}, como lo haría "
        f"{niche.customer_article} {niche.customer}. {fact} Preparé un diagnóstico gratis con "
        f"lo que puede mejorar para aparecer más. ¿Te lo envío por aquí?"
    )
