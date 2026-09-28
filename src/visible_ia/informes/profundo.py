"""Deeper free diagnostic (C-008): only answers already stored, no new runs.

1. Why the AI chose the competition: 2–3 sentences per top competitor, copied LITERALLY from
   the answers. The code cuts the answers into sentences; gpt-5-nano only picks sentence
   numbers (it never writes text), and every pick is checked to be a literal substring of its
   answer. Without the API (no key, error, budget) the first sentences that name it are used.
2. Where you are missing: pages cited in answers that name those competitors and never in
   answers that name the clinic, by type, only where the clinic can be: clinics' own
   websites and Google profiles are left out (summarised in one line for websites).
3. In which questions you appear: for each of the 10 questions, how many of its answers name
   the clinic and the leader, grouped by the question's form.
"""

import json
import re
import unicodedata
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from urllib.parse import urlsplit

MODEL = "gpt-5-nano"
MAX_REASONS = 3
MAX_CANDIDATES = 40
MAX_PAGES = 8
FORM_LABELS = {"M": "Mejor", "R": "Recomendación", "C": "Criterio", "P": "Procedimiento"}
# source_type -> label. Left out on purpose, because you cannot "be" there: clinics' own
# websites (own_website) and other clinics' Google profiles (google_profile; yours is your own).
PAGE_TYPES = {
    "doctoralia": "Doctoralia",
    "directory": "Directorio o ranking",
    "press": "Prensa",
    "social": "Redes",
    "other": "Otras",
}
SURFACE_LABELS = {"chatgpt_api": "ChatGPT", "google_ai_mode": "Google (Modo IA)"}
# Words that usually carry the reason ("porque destaca por sus reseñas…"): fallback order only.
REASON_WORDS = (
    "destaca", "reseña", "opinion", "especialista", "experiencia", "tecnolog",
    "recomend", "garant", "precio", "calidad", "atencion", "porque", "valorad",
)  # fmt: skip


@dataclass(frozen=True)
class Answer:
    id: int
    surface: str
    question_id: int
    question: str
    form: str
    asked_on: date
    text: str
    clinics: frozenset[int]
    urls: tuple[tuple[str, str, str], ...] = ()  # (url, domain, source_type)


@dataclass(frozen=True)
class Candidate:
    answer: Answer
    sentence: str  # literal substring of answer.text


@dataclass
class Reasons:
    clinic_id: int
    name: str
    index: float
    quotes: list[Candidate] = field(default_factory=list)


@dataclass(frozen=True)
class Page:
    url: str
    domain: str
    kind: str
    answers: int


def fold(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in text if not unicodedata.combining(c))


ABBREVIATIONS = {
    "dr", "dra", "dres", "sr", "sra", "srta", "av", "ca", "jr", "urb", "mz",
    "lt", "nro", "no", "n", "cdra", "prol", "st", "sto", "sta", "ing", "lic",
}  # fmt: skip


def split_sentences(text: str) -> list[str]:
    """Sentences as literal substrings of `text` (no characters changed), trimmed.

    A period after an abbreviation (Dr., Dra., Av., …) does not end a sentence, so a
    professional's title stays next to the name and can be masked later.
    """
    out, start = [], 0
    for m in re.finditer(r"[.!?]+(?=\s|$)|\n", text):
        word = re.search(r"(\w+)$", text[start : m.start()])
        if m.group(0) == "." and word and fold(word.group(1)) in ABBREVIATIONS:
            continue
        chunk, start = text[start : m.end()], m.end()
        s = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s+", "", chunk).strip()
        if 25 <= len(s) <= 400:
            out.append(s)
    tail = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s+", "", text[start:]).strip()
    if 25 <= len(tail) <= 400:
        out.append(tail)
    return out


def candidates(
    answers: list[Answer],
    clinic_id: int,
    names: list[str],
    keep: Callable[[str], bool] | None = None,
) -> list[Candidate]:
    """Sentences of the answers that name the clinic and mention one of its names. `keep`
    drops sentences the report could not show as they are (e.g. a professional's name)."""
    keys = [fold(n) for n in names if len(n) >= 4]
    seen, out = set(), []
    for a in answers:
        if clinic_id not in a.clinics:
            continue
        for s in split_sentences(a.text):
            if any(k in fold(s) for k in keys) and fold(s) not in seen and (not keep or keep(s)):
                seen.add(fold(s))
                out.append(Candidate(a, s))
    return out[:MAX_CANDIDATES]


def fallback_pick(cands: list[Candidate], n: int = MAX_REASONS) -> list[int]:
    """Without the model: the sentences with reason words first, in order of appearance."""
    scored = sorted(
        range(len(cands)),
        key=lambda i: (-sum(w in fold(cands[i].sentence) for w in REASON_WORDS), i),
    )
    return sorted(scored[:n])


def validate_picks(picks: list[int], cands: list[Candidate]) -> list[Candidate]:
    """Keep only valid, distinct numbers whose sentence is literally in its answer."""
    out = []
    for i in picks:
        if isinstance(i, int) and 0 <= i < len(cands) and cands[i] not in out:
            if cands[i].sentence in cands[i].answer.text:
                out.append(cands[i])
    return out[:MAX_REASONS]


def competitor_reasons(
    top: list[tuple[int, str, float]],
    answers: list[Answer],
    market_names: dict[int, list[str]],
    chooser: Callable[[str, list[str]], list[int]] | None = None,
    keep: Callable[[str], bool] | None = None,
) -> list[Reasons]:
    """Reasons for each (clinic_id, name, index) of `top`. `chooser(name, sentences)` returns
    sentence numbers (the model); when it is missing or fails, fallback_pick is used."""
    out = []
    for clinic_id, name, index in top:
        cands = candidates(answers, clinic_id, market_names.get(clinic_id, [name]), keep)
        picks: list[int] = []
        if chooser and cands:
            try:
                picks = chooser(name, [c.sentence for c in cands])
            except Exception:  # noqa: BLE001 - the report must be generated anyway
                picks = []
        chosen = validate_picks(picks, cands) or validate_picks(fallback_pick(cands), cands)
        out.append(Reasons(clinic_id, name, index, chosen))
    return out


def _domain(url: str) -> str:
    host = (urlsplit(url).hostname or "").lower()
    return host[4:] if host.startswith("www.") else host


def missing_pages(
    answers: list[Answer], clinic_id: int, competitor_ids: list[int], clinic_website: str | None
) -> tuple[list[Page], dict[str, int]]:
    """Pages cited with the competitors and never with the clinic (max 8, most cited first),
    plus how many answers naming the competitors cite clinics' own websites, and how many
    answers cite the clinic's own website."""
    rivals = set(competitor_ids)
    my_domain = _domain(clinic_website) if clinic_website else None
    mine = {u for a in answers if clinic_id in a.clinics for u, _, _ in a.urls}
    counts: Counter = Counter()
    info: dict[str, tuple[str, str]] = {}
    own_rivals, own_mine = set(), set()
    for a in answers:
        with_rival = bool(a.clinics & rivals)
        for url, domain, kind in set(a.urls):
            if my_domain and _domain(url) == my_domain:
                own_mine.add(a.id)
            if kind == "own_website":
                if with_rival:
                    own_rivals.add(a.id)
                continue
            if kind == "google_profile":  # another clinic's Google profile: not for you
                continue
            if not with_rival or url in mine or kind not in PAGE_TYPES:
                continue
            counts[url] += 1
            info[url] = (domain or _domain(url), PAGE_TYPES[kind])
    pages = [Page(u, info[u][0], info[u][1], n) for u, n in counts.most_common(MAX_PAGES)]
    # Grouped by type; the type with the most cited page first, then the most cited pages.
    best = {}
    for p in pages:
        best[p.kind] = max(best.get(p.kind, 0), p.answers)
    pages.sort(key=lambda p: (-best[p.kind], p.kind, -p.answers))
    return pages, {"competidores": len(own_rivals), "tuya": len(own_mine)}


def question_table(answers: list[Answer], clinic_id: int, leader_id: int) -> list[dict]:
    """Per question: answers, answers naming the clinic, answers naming the leader; by form."""
    rows: dict[int, dict] = {}
    for a in answers:
        r = rows.setdefault(
            a.question_id,
            {"pregunta": a.question, "forma": a.form, "total": 0, "tu": 0, "lider": 0},
        )
        r["total"] += 1
        r["tu"] += clinic_id in a.clinics
        r["lider"] += leader_id in a.clinics
    groups = []
    for form, label in FORM_LABELS.items():
        items = sorted(
            (r for r in rows.values() if r["forma"] == form), key=lambda r: r["pregunta"]
        )
        if items:
            groups.append({"forma": label, "preguntas": items})
    return groups


# --- the model: it picks sentence numbers, it never writes text -------------------------------

INSTRUCTIONS = (
    "Recibes frases numeradas, copiadas de respuestas de un asistente de IA a pacientes que "
    "buscan una clínica en Lima. Elige hasta 3 frases que mejor explican POR QUÉ la IA "
    "recomienda a la clínica indicada (reseñas, especialidad, tecnología, precio, trato, "
    "ubicación…). Prefiere frases con una razón concreta y distintas entre sí. Si ninguna da una "
    "razón, elige las que mejor la describen. Devuelve solo los números."
)
SCHEMA = {
    "type": "object",
    "properties": {"elegidas": {"type": "array", "items": {"type": "integer"}, "maxItems": 3}},
    "required": ["elegidas"],
    "additionalProperties": False,
}


def model_input(name: str, sentences: list[str]) -> str:
    lines = "\n".join(f"{i}. {s}" for i, s in enumerate(sentences))
    return f"Clínica: {name}\n\nFrases:\n{lines}"


def parse_picks(raw: dict) -> list[int]:
    for item in raw.get("output") or []:
        for part in item.get("content") or []:
            if part.get("type") == "output_text":
                return [int(i) for i in json.loads(part["text"]).get("elegidas", [])]
    return []


class ModelChooser:
    """Calls gpt-5-nano once per competitor and adds up calls and cost."""

    def __init__(self, client, rates) -> None:
        self.client, self.rates = client, rates
        self.calls, self.cost_usd = 0, 0.0

    def __call__(self, name: str, sentences: list[str]) -> list[int]:
        from visible_ia.motor.modelos import Usage

        response = self.client.responses.create(
            model=MODEL,
            instructions=INSTRUCTIONS,
            input=model_input(name, sentences),
            reasoning={"effort": "minimal"},
            text={"format": {"type": "json_schema", "name": "frases", "schema": SCHEMA,
                             "strict": True}},
        )  # fmt: skip
        raw = response.model_dump(mode="json")
        usage = raw.get("usage") or {}
        self.calls += 1
        self.cost_usd += self.rates.cost(
            MODEL,
            Usage(
                input_tokens=usage.get("input_tokens") or 0,
                cached_input_tokens=(usage.get("input_tokens_details") or {}).get("cached_tokens")
                or 0,
                output_tokens=usage.get("output_tokens") or 0,
                reasoning_tokens=(usage.get("output_tokens_details") or {}).get("reasoning_tokens")
                or 0,
            ),
            searches=0,
        )
        return parse_picks(raw)


# --- redesign (28/09): question grid and repetition consistency ------------------------------

SURFACE_ORDER = ("chatgpt_api", "google_ai_mode")


def _surface_then_id(a: Answer) -> tuple[int, int]:
    return (SURFACE_ORDER.index(a.surface) if a.surface in SURFACE_ORDER else 9, a.id)


def question_grid(answers: list[Answer], clinic_ids: list[int]) -> list[dict]:
    """Per question, one list of dots per clinic (True = that answer names it), ChatGPT first,
    then Google, in answer order; grouped by the question's form."""
    by_question: dict[int, list[Answer]] = {}
    for a in answers:
        by_question.setdefault(a.question_id, []).append(a)
    groups = []
    for form, label in FORM_LABELS.items():
        rows = []
        for qa in by_question.values():
            if qa[0].form != form:
                continue
            ordered = sorted(qa, key=_surface_then_id)
            rows.append({
                "pregunta": qa[0].question,
                "celdas": [[cid in a.clinics for a in ordered] for cid in clinic_ids],
            })  # fmt: skip
        if rows:
            groups.append({"forma": label, "preguntas": sorted(rows, key=lambda r: r["pregunta"])})
    return groups


def consistency(answers: list[Answer], clinic_id: int) -> list[dict]:
    """Per surface: in how many questions the clinic was named in all repetitions, in some,
    and in none."""
    out = []
    for surface in SURFACE_ORDER:
        per_question: dict[int, list[bool]] = {}
        for a in answers:
            if a.surface == surface:
                per_question.setdefault(a.question_id, []).append(clinic_id in a.clinics)
        if not per_question:
            continue
        named = [sum(v) for v in per_question.values()]
        reps = max(len(v) for v in per_question.values())
        out.append({
            "superficie": SURFACE_LABELS[surface],
            "repeticiones": reps,
            "todas": sum(1 for v in per_question.values() if v and all(v)),
            "algunas": sum(1 for n, v in zip(named, per_question.values(), strict=True)
                           if 0 < n < len(v)),
            "ninguna": sum(1 for n in named if n == 0),
        })  # fmt: skip
    return out
