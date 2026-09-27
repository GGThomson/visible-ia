"""Match each mention to a clinic of the market (HU-07, HU-09).

1. Exact: the folded mention equals the folded name or an alias of one clinic.
2. Fuzzy: rapidfuzz token_set_ratio >= threshold, computed on the *specific* words only
   (category words, districts and honorifics removed); otherwise "Clínica Dental" would score
   100 against "Clínica Dental Cano". token_set_ratio also gives 100 when one name is contained
   in the other, so a mention with a distinctive word the clinic lacks is rejected ("Digital
   Smiles" is not "Smiles Peru"); the reverse is fine ("Pérez Yance" is short for "Perez
   Yance Americadent").
A tie between two clinics is never resolved automatically: the mention goes to review.
Without a match, the mention is a "new" clinic.
"""

from dataclasses import dataclass, field
from typing import Literal

import psycopg
from rapidfuzz import fuzz

from visible_ia.mercados.alias import GENERIC, fold

DEFAULT_THRESHOLD = 90
HONORIFICS = {"dr", "dra", "doctor", "doctora", "od", "cd"}
# The AI answers often use English names ("Vicich Dental Clinic", "Dr. Aldo Implants").
ENGLISH_GENERIC = {
    "clinic", "clinics", "dental", "implant", "implants", "oral", "rehabilitation",
    "center", "centre", "dentistry", "dentist", "dentists", "care", "group",
}  # fmt: skip
IGNORED = GENERIC | HONORIFICS | ENGLISH_GENERIC

Status = Literal["matched", "new", "review"]


@dataclass(frozen=True)
class ClinicCandidate:
    id: int
    name: str
    aliases: tuple[str, ...] = ()

    @property
    def names(self) -> tuple[str, ...]:
        return (self.name, *self.aliases)


@dataclass(frozen=True)
class MatchResult:
    status: Status
    clinic_id: int | None = None
    score: float = 0.0
    via: str = ""  # "exact", "fuzzy" or ""
    tied: tuple[int, ...] = field(default_factory=tuple)


def specific(text: str) -> str:
    """Folded text without category words, districts, fillers and honorifics."""
    return " ".join(w for w in fold(text).split() if w not in IGNORED)


def match(
    mention: str, clinics: list[ClinicCandidate], *, threshold: float = DEFAULT_THRESHOLD
) -> MatchResult:
    folded = fold(mention)
    if not folded:
        return MatchResult("new")
    without_title = " ".join(w for w in folded.split() if w not in HONORIFICS)

    exact = {c.id for c in clinics for n in c.names if fold(n) in (folded, without_title)}
    if len(exact) == 1:
        return MatchResult("matched", exact.pop(), 100.0, "exact")
    if len(exact) > 1:
        return MatchResult("review", score=100.0, via="exact", tied=tuple(sorted(exact)))

    core = specific(mention)
    if not core:
        return MatchResult("new")
    best: dict[int, float] = {}
    for clinic in clinics:
        # Extra words are checked against all the clinic's names together, so a mention that
        # joins two aliases ("Dental Pérez Yance / Clínicas Dentales Americadent") still fits.
        vocabulary = " ".join(specific(n) for n in clinic.names).split()
        for name in clinic.names:
            other = specific(name)
            if other:
                score = _score(core, other, vocabulary, threshold)
                best[clinic.id] = max(best.get(clinic.id, 0.0), score)
    if not best:
        return MatchResult("new")
    top = max(best.values())
    if top < threshold:
        return MatchResult("new", score=top)
    winners = sorted(cid for cid, score in best.items() if score == top)
    if len(winners) > 1:
        return MatchResult("review", score=top, via="fuzzy", tied=tuple(winners))
    return MatchResult("matched", winners[0], top, "fuzzy")


def _score(core: str, other: str, vocabulary: list[str], threshold: float) -> float:
    score = fuzz.token_set_ratio(core, other)
    if score < threshold:
        return score
    extra = [w for w in core.split() if not any(fuzz.ratio(w, v) >= threshold for v in vocabulary)]
    return 0.0 if extra else score


def load_market_clinics(conn: psycopg.Connection, market_id: int) -> list[ClinicCandidate]:
    with conn.cursor() as cur:
        cur.execute(
            "select c.id, c.name, coalesce(array_agg(a.alias order by a.alias) "
            "filter (where a.alias is not null), '{}') "
            "from public.clinics c join public.clinic_markets cm on cm.clinic_id = c.id "
            "left join public.aliases a on a.clinic_id = c.id "
            "where cm.market_id = %s group by c.id, c.name order by c.id",
            (market_id,),
        )
        return [ClinicCandidate(cid, name, tuple(aliases)) for cid, name, aliases in cur.fetchall()]
