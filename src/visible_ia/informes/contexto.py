"""Data of the free diagnostic report (HU-14): the clinic against its 3 main competitors.

`build_context` is pure (plain data in, template context out) so the report can be tested
without a database; `load_report_data` reads a reviewed month of a market.

Privacy (PRD HU-14): no patient data, and professionals' names only when they are the name
of an establishment of the market list; any other "Dr./Dra. …" becomes "[profesional]".
"""

import re
import tomllib
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import psycopg

from visible_ia.informes.profundo import (
    SURFACE_LABELS,
    Answer,
    Reasons,
    consistency,
    instagram_counts,
    missing_pages,
    question_grid,
    question_table,
)
from visible_ia.informes.semaforo import (
    Facts,
    Side,
    dec,
    findings,
    gap,
    impact,
    lights,
    one_in,
    thousands,
)
from visible_ia.informes.semaforo import allowed as fix_allowed
from visible_ia.mercados.alias import fold
from visible_ia.puntaje.brecha import has_gap
from visible_ia.puntaje.fuentes import TYPE_LABELS, load_citations, top_sources, type_shares
from visible_ia.puntaje.indice import RankingRow, ScoreError, ranking

HERE = Path(__file__).resolve().parent
BRAND_TOML = HERE / "marca.toml"
RECOMMENDATIONS_TOML = HERE / "recomendaciones.toml"

TREATMENT = {
    "IMP": "implantes dentales",
    "EDE": "estética dental",
    "MES": "medicina estética",
    "DER": "dermatología",
}
MONTHS = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
          "setiembre", "octubre", "noviembre", "diciembre")  # fmt: skip
SURFACE_NAMES = {"chatgpt_api": "ChatGPT", "google_ai_mode": "Google (Modo IA)"}
PROFESSIONAL = re.compile(
    r"\b(?:Dr|Dra|Doctor|Doctora)\.?\s+[A-ZÁÉÍÓÚÑ][\wáéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][\wáéíóúñ]+){0,3}"
)
QUOTE_CHARS = 700  # example answers end at a full sentence before this
SENTENCE_END = re.compile(r"(?<=[.!?:])\s+")
MD_LINK = re.compile(r"\(?\[([^\]]+)\]\([^)]*\)\)?")


@dataclass(frozen=True)
class ClinicInfo:
    id: int
    name: str
    rating: float | None
    reviews: int | None
    data_date: date | None
    website: str | None
    instagram: str | None = None


@dataclass(frozen=True)
class ExampleAnswer:
    surface: str
    question: str
    asked_on: date
    text: str
    mentions: list[tuple[int, str, int | None]]  # (position, raw_name, clinic_id)


@dataclass
class ReportData:
    clinic: ClinicInfo
    category: str
    district: str
    month: date
    ranking: list[RankingRow]
    examples: list[ExampleAnswer]
    citations: list[tuple[int, str, str, str]]  # (response_id, surface, domain, type)
    total_answers: int
    detectable_diff: float | None  # points, combined
    google_without_names: int  # Google answers naming no clinic (C-006 included)
    market_names: dict[int, list[str]] = field(default_factory=dict)  # clinic -> name + aliases
    competitors: list[int] | None = None
    # Deeper diagnostic (C-008): the month's answers with their clinics, question form and
    # cited URLs, and the literal reasons picked for the top competitors.
    deep_answers: list[Answer] = field(default_factory=list)
    reasons: list[Reasons] = field(default_factory=list)
    # Website, Instagram, stars and reviews of every clinic of the market (to compare with the
    # leader): clinic -> {"website", "instagram", "rating", "reviews"}.
    profiles: dict[int, dict[str, Any]] = field(default_factory=dict)


def load_brand(path: Path = BRAND_TOML) -> dict[str, str]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def month_text(month: date) -> str:
    return f"{MONTHS[month.month - 1]} de {month.year}"


def mask_professionals(text: str, allowed_names: list[str]) -> str:
    """Replace 'Dr./Dra. Name' unless it is (part of) an establishment of the market."""
    allowed = [f" {fold(n)} " for n in allowed_names]

    def repl(m: re.Match) -> str:
        found = f" {fold(m.group(0))} "
        return m.group(0) if any(found in a for a in allowed) else "[profesional]"

    return PROFESSIONAL.sub(repl, text)


def plain_text(text: str) -> str:
    """Answer text without Markdown: links keep their text, no emphasis marks or bullets."""
    text = MD_LINK.sub(lambda m: m.group(1) if not m.group(0).startswith("(") else "", text)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"[*_`#]+", "", text)
    text = re.sub(r"(^|\s)[-•]\s+", " ", text)
    return " ".join(text.split())


def _pct(value: float | None) -> str:
    return "—" if value is None else f"{value:.0f}"


def pick_competitors(
    rows: list[RankingRow], clinic_id: int, chosen: list[int] | None
) -> list[RankingRow]:
    by_id = {r.clinic_id: r for r in rows}
    if chosen:
        missing = [c for c in chosen if c not in by_id]
        if missing:
            raise ScoreError(f"Competidores sin puntaje en el mercado: {missing}")
        return [by_id[c] for c in chosen][:3]
    return [r for r in rows if r.clinic_id != clinic_id][:3]


def pick_example(
    answers: list[ExampleAnswer], surface: str, focus: list[int]
) -> ExampleAnswer | None:
    """The answer of a surface that best shows the comparison: the clinic first, else its
    competitors (the most of them, earliest)."""
    candidates = [a for a in answers if a.surface == surface]
    if not candidates:
        return None

    def key(a: ExampleAnswer):
        ids = [cid for _, _, cid in sorted(a.mentions)]
        own = ids.index(focus[0]) if focus and focus[0] in ids else 99
        shared = sum(1 for c in focus[1:] if c in ids)
        return (own, -shared, len(a.text))

    return min(candidates, key=key)


def _example_context(a: ExampleAnswer, data: ReportData, allowed: list[str]) -> dict[str, Any]:
    names = []
    for _, raw_name, clinic_id in sorted(a.mentions):
        if clinic_id is not None:
            name = data.market_names.get(clinic_id, [raw_name])[0]
        else:
            name = mask_professionals(raw_name, allowed)
        if name not in [n["nombre"] for n in names]:
            names.append({"nombre": name, "es_cliente": clinic_id == data.clinic.id})
    return {
        "superficie": SURFACE_NAMES[a.surface],
        "pregunta": a.question,
        "fecha": a.asked_on.strftime("%d/%m/%Y"),
        "nombres": names,
        "cita": mask_professionals(example_quote(a, data.clinic.id), allowed),
    }


def example_quote(a: ExampleAnswer, clinic_id: int) -> str:
    """Whole sentences, from the one where the clinic (else the first clinic) is named."""
    sentences = [x for x in SENTENCE_END.split(plain_text(a.text)) if x]
    ordered = sorted(a.mentions)
    anchors = [raw for _, raw, cid in ordered if cid == clinic_id] or [raw for _, raw, _ in ordered]
    start = next(
        (i for i, x in enumerate(sentences) if any(n.lower() in x.lower() for n in anchors[:1])),
        0,
    )
    out: list[str] = []
    for x in sentences[start:]:
        if out and len(" ".join([*out, x])) > QUOTE_CHARS:
            break
        out.append(x)
    return " ".join(out)


def _site(value: str | None) -> str:
    return re.sub(r"^https?://(www\.)?", "", (value or "").lower()).split("/")[0]


def build_facts(data: ReportData, me: RankingRow) -> Facts:
    """The numbers every section of the diagnostic reads: computed once, here."""
    answers = data.deep_answers
    others = [r for r in data.ranking if r.clinic_id != me.clinic_id]
    leads = data.ranking[0].clinic_id == me.clinic_id
    ref = (others[0] if others else None) if leads else data.ranking[0]

    def side(row: RankingRow, website: str | None, rating, reviews) -> Side:
        domain = _site(website)
        if answers:
            named = [a for a in answers if row.clinic_id in a.clinics]
            web = sum(
                1
                for a in answers
                if domain and any(domain in (_site(u), _site(d)) for u, d, _ in a.urls)
            )
            dirs = sum(
                1 for a in named if any(k in ("doctoralia", "directory") for _, _, k in a.urls)
            )
            n_named = len(named)
        else:  # only the aggregated citations
            web = len({rid for rid, _, d, _ in data.citations if domain and _site(d) == domain})
            n_named, dirs = round((row.combined or 0) * data.total_answers / 100), 0
        return Side(row.combined, row.ci_low, row.ci_high, row.chatgpt, row.google,
                    web, n_named, dirs, rating, reviews)  # fmt: skip

    ref_side = None
    if ref is not None:
        p = data.profiles.get(ref.clinic_id, {})
        ref_side = side(ref, p.get("website"), p.get("rating"), p.get("reviews"))
    return Facts(
        total=data.total_answers,
        me=side(me, data.clinic.website, data.clinic.rating, data.clinic.reviews),
        ref=ref_side,
        ref_label="la n.º 2" if leads else "el líder",
        has_web=bool(data.clinic.website),
        has_answers=bool(answers),
        per_surface=sum(1 for a in answers if a.surface == "chatgpt_api"),
    )


def _plan(values: dict[str, Any], applies: dict[str, bool], facts: Facts,
          by_area: dict[str, str]) -> list[dict[str, Any]]:  # fmt: skip
    """Up to 3 fixes, only for areas that are not already "Bien", ordered by how many answers
    separate the clinic from the leader in that area (the computed impact)."""
    items = tomllib.loads(RECOMMENDATIONS_TOML.read_text(encoding="utf-8"))["recomendacion"]
    usable = [r for r in items if fix_allowed(r["id"], by_area)]
    gaps = {r["id"]: gap(r["id"], facts) for r in usable}

    def order(r):
        return (r["id"] == "mantener", -gaps[r["id"]])

    chosen = sorted((r for r in usable if applies.get(r["id"])), key=order)[:3]
    # Fill only with fixes whose text is true for any clinic.
    chosen += sorted(
        (r for r in usable if r not in chosen and r["id"] in ("web", "doctoralia")
         and gaps[r["id"]] > 0),
        key=order,
    )[: 3 - len(chosen)]  # fmt: skip
    out = []
    for r in sorted(chosen, key=order):
        answers = gaps[r["id"]]
        level = impact(answers, facts.total)
        if r["id"] == "mantener":
            text = "Impacto: mantiene tu puesto"
        elif answers:
            text = (f"Impacto {level} · {answers} de {facts.total} respuestas de diferencia "
                    f"con {facts.ref_label}")  # fmt: skip
        else:
            text = f"Impacto {level}"
        out.append({
            "id": r["id"],
            "titulo": r["titulo"].format(**values),
            "texto": r["texto"].format(**values),
            "esfuerzo": r.get("esfuerzo", "medio"),
            "respuestas": answers,
            "impacto": level,
            "impacto_texto": text,
        })  # fmt: skip
    return out


def reason_filter(data: ReportData):
    """Sentences shown only if masking would not change them (no professional's name)."""
    allowed = [n for names in data.market_names.values() for n in names]
    return lambda sentence: mask_professionals(sentence, allowed) == sentence


def reason_targets(data: ReportData) -> list[tuple[int, str, float]]:
    """The competitors whose reasons the diagnostic shows: the same ones it compares with."""
    return [
        (r.clinic_id, r.name, r.combined)
        for r in pick_competitors(data.ranking, data.clinic.id, data.competitors)
    ]


def _deep_context(
    data: ReportData, competitors: list, allowed: list[str], facts: Facts
) -> dict[str, Any]:
    """Sections of the deeper diagnostic (C-008); empty when there are no stored answers."""
    if not data.deep_answers:
        return {"hay": False}
    leader = next((r for r in data.ranking if r.clinic_id != data.clinic.id), data.ranking[0])
    pages, own = missing_pages(
        data.deep_answers, data.clinic.id, [c.clinic_id for c in competitors], data.clinic.website
    )
    own["tuya"] = facts.me.web  # the same count as the summary and the action plan
    return {
        "hay": True,
        "fuente": f"{len(data.deep_answers)} respuestas de ChatGPT y Google Modo IA, "
        f"{month_text(data.month)}",
        "razones": [
            {
                "nombre": r.name,
                "indice": _pct(r.index),
                "frases": [
                    {
                        "texto": mask_professionals(plain_text(q.sentence), allowed),
                        "superficie": SURFACE_LABELS.get(q.answer.surface, q.answer.surface),
                        "pregunta": q.answer.question,
                        "fecha": q.answer.asked_on.strftime("%d/%m/%Y"),
                    }
                    for q in r.quotes
                ],
            }
            for r in data.reasons
        ],
        "lider": leader.name,
        "preguntas": question_table(data.deep_answers, data.clinic.id, leader.clinic_id),
        "faltantes": [
            {
                "url": p.url,
                "corta": _short_url(p.url),
                "dominio": p.domain,
                "tipo": p.kind,
                "veces": p.answers,
            }
            for p in pages
        ],  # fmt: skip
        "webs": own,
        "instagram": instagram_counts(data.deep_answers, data.clinic.instagram),
    }


def _short_url(url: str, limit: int = 60) -> str:
    text = re.sub(r"^https?://(www\.)?", "", url).rstrip("/")
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _position(value: float | None) -> str:
    """Average position when named, Peruvian style (2,3)."""
    return dec(value)


def _redesign(data, me, competitors, leader, position, appearances, facts, light, recs):
    """Summary, comparison, question grid and action plan of the redesigned diagnostic."""
    answers = data.deep_answers
    total = data.total_answers
    compared = sorted([me, *competitors], key=lambda r: -(r.combined or 0))
    leader_appearances = round((leader.combined or 0) * total / 100)
    clinic_ids = [data.clinic.id, *[c.clinic_id for c in competitors]]
    names = {r.clinic_id: r.name for r in data.ranking}
    is_leader = me.clinic_id == leader.clinic_id

    def row(r):
        return {
            "nombre": r.name, "es_cliente": r.clinic_id == data.clinic.id,
            "combinado": _pct(r.combined), "bajo": _pct(r.ci_low), "alto": _pct(r.ci_high),
            "chatgpt": _pct(r.chatgpt), "google": _pct(r.google),
            "posicion": _position(r.avg_position),
            "cuota": _pct(r.mention_share), "ancho": max(r.combined or 0, 0.5),
        }  # fmt: skip

    consequence = (
        f"La IA te nombra {one_in(me.combined)}: eres la clínica más nombrada."
        if is_leader
        else f"La IA te nombra {one_in(me.combined)}; al líder, {leader.name}, "
        f"{one_in(leader.combined)}."
    )
    return {
        "cifras": {
            "indice": _pct(me.combined),
            "bajo": _pct(me.ci_low),
            "alto": _pct(me.ci_high),
            "puesto": position,
            "total": len(data.ranking),
            "posicion": _position(me.avg_position),
        },
        "consecuencia": consequence,
        "semaforo": [
            {
                "nombre": x.name,
                "nivel": x.level,
                "valor": x.value,
                "clase": {"Bien": "bien", "Regular": "regular", "Bajo": "bajo"}.get(x.level, "sin"),
            }
            for x in light
        ],  # fmt: skip
        "barras": [row(r) for r in compared],
        "hallazgos": findings(
            clinic=data.clinic.name,
            appearances=appearances,
            total=total,
            leader=leader.name,
            leader_appearances=leader_appearances,
            is_leader=is_leader,
            rating=data.clinic.rating,
            reviews=data.clinic.reviews,
            web_answers=facts.me.web,
            chatgpt=me.chatgpt,
            google=me.google,
        ),  # fmt: skip
        "competencia": [row(r) for r in compared],
        "cuadricula": {
            "clinicas": [
                {"nombre": names.get(cid, "—"), "es_cliente": cid == data.clinic.id}
                for cid in clinic_ids
            ],
            "grupos": question_grid(answers, clinic_ids),
        },
        "consistencia": consistency(answers, data.clinic.id),
        "plan": recs,
        "quien": "tu equipo, con la guía del Plan Medir, o nosotros, en el Plan Gestionado",
        "web_respuestas": facts.me.web,
    }


def build_context(data: ReportData, brand: dict[str, str] | None = None) -> dict[str, Any]:
    brand = brand or load_brand()
    rows = {r.clinic_id: r for r in data.ranking}
    if data.clinic.id not in rows:
        raise ScoreError(f"La clínica {data.clinic.name} no tiene puntaje en este mercado y mes")
    me = rows[data.clinic.id]
    competitors = pick_competitors(data.ranking, data.clinic.id, data.competitors)
    position = [r.clinic_id for r in data.ranking].index(data.clinic.id) + 1
    leader = data.ranking[0]
    allowed = [n for names in data.market_names.values() for n in names]
    treatment = TREATMENT.get(data.category, "tu especialidad")

    compared = sorted([me, *competitors], key=lambda r: -(r.combined or 0))
    ranking_rows = [
        {
            "nombre": r.name,
            "es_cliente": r.clinic_id == data.clinic.id,
            "combinado": _pct(r.combined),
            "bajo": _pct(r.ci_low),
            "alto": _pct(r.ci_high),
            "chatgpt": _pct(r.chatgpt),
            "google": _pct(r.google),
            "ancho": max(r.combined or 0, 0.5),
        }
        for r in compared
    ]
    appearances = round((me.combined or 0) * data.total_answers / 100)
    if me.clinic_id == leader.clinic_id:
        sentence = (
            f"La IA nombró a {data.clinic.name} en {appearances} de {data.total_answers} "
            f"respuestas: es la clínica más recomendada de su mercado este mes "
            f"(entre {_pct(me.ci_low)} % y {_pct(me.ci_high)} %)."
        )
    else:
        sentence = (
            f"La IA nombró a {data.clinic.name} en {appearances} de {data.total_answers} "
            f"respuestas (entre {_pct(me.ci_low)} % y {_pct(me.ci_high)} %). {leader.name}, la más "
            f"recomendada, aparece en {_pct(leader.combined)} %."
        )

    shares = type_shares(data.citations, data.total_answers)
    top = top_sources(data.citations, data.total_answers, per_type=3)
    top_rows = sorted(
        (r for rows_ in top.values() for r in rows_ if r.source_type != "google_profile"),
        key=lambda r: -r.answers,
    )[:6]

    facts = build_facts(data, me)
    light = lights(facts)
    by_area = {x.id: x.level for x in light}
    gap_found = has_gap(data.clinic.rating, data.clinic.reviews, me.combined or 0)
    total = data.total_answers
    values = {
        "tratamiento": treatment,
        "distrito": data.district,
        "pct_web": _pct(shares.get("own_website", 0)),
        "pct_doctoralia": _pct(shares.get("doctoralia", 0)),
        "pct_directorios": _pct(shares.get("directory", 0)),
        "google": _pct(me.google),
        "chatgpt": _pct(me.chatgpt),
        "resenas": thousands(data.clinic.reviews) if data.clinic.reviews is not None else "pocas",
        "rating": dec(data.clinic.rating),
        "indice": _pct(me.combined),
        "web_tuya": f"en {facts.me.web} de {total}" if facts.me.web else "en ninguna",
        "dir_tuyo": (
            f"{facts.me.directories} de las {facts.me.named}"
            if facts.me.named
            else "ninguna de las"
        ),  # fmt: skip
    }
    ref_reviews = facts.ref.reviews if facts.ref and facts.ref.reviews else 200
    applies = {
        "brecha": gap_found,
        "web": True,  # proposed unless the web area is "Bien" (see semaforo.allowed)
        "google": (me.google or 0) < (me.chatgpt or 0) or (me.google or 0) < 10,
        "chatgpt": (me.chatgpt or 0) < (me.google or 0),
        "doctoralia": True,
        "resenas": data.clinic.reviews is not None and data.clinic.reviews < ref_reviews / 2,
        "mantener": position <= 3,
    }

    recs = _plan(values, applies, facts, by_area)
    focus = [data.clinic.id, *[c.clinic_id for c in competitors]]
    examples = [
        _example_context(e, data, allowed)
        for surface in SURFACE_NAMES
        if (e := pick_example(data.examples, surface, focus)) is not None
    ]

    return {
        "marca": brand,
        "clinica": {
            "nombre": data.clinic.name,
            "posicion": position,
            "total_clinicas": len(data.ranking),
        },
        "mercado": {
            "tratamiento": treatment,
            "distrito": data.district,
            "mes": month_text(data.month),
        },
        "frase": sentence,
        "ranking": ranking_rows,
        "ejemplos": examples,
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
            "propia_citada": facts.me.web > 0,
            "web_tuya": facts.me.web,
        },
        "brecha": {
            "rating": dec(data.clinic.rating) if data.clinic.rating is not None else None,
            "resenas": thousands(data.clinic.reviews) if data.clinic.reviews is not None else None,
            "fecha": data.clinic.data_date.strftime("%d/%m/%Y") if data.clinic.data_date else None,
            "indice": _pct(me.combined),
            "tiene_brecha": gap_found,
            "lider": {"nombre": leader.name, "indice": _pct(leader.combined)},
        },
        "recomendaciones": recs,
        "profundo": _deep_context(data, competitors, allowed, facts),
        "nuevo": _redesign(
            data, me, competitors, leader, position, appearances, facts, light, recs
        ),
        "metodo": {
            "preguntas": 10,
            "repeticiones": 3,
            "respuestas": data.total_answers,
            "mes": month_text(data.month),
            "detectable": _pct(data.detectable_diff),
            "google_sin_nombres": data.google_without_names,
        },
    }


# --- database ------------------------------------------------------------------------------


def load_report_data(
    conn: psycopg.Connection,
    clinic_id: int,
    market_id: int,
    month: date | None = None,
    competitors: list[int] | None = None,
) -> ReportData:
    month, rows = ranking(conn, market_id, month)
    with conn.cursor() as cur:
        cur.execute(
            "select c.id, c.name, c.rating, c.review_count, c.data_date, c.website, c.instagram "
            "from public.clinics c join public.clinic_markets cm on cm.clinic_id = c.id "
            "where c.id = %s and cm.market_id = %s",
            (clinic_id, market_id),
        )
        row = cur.fetchone()
        if row is None:
            raise ScoreError(f"La clínica {clinic_id} no es del mercado {market_id}")
        cid, name, rating, reviews, data_date, website, instagram = row
        clinic = ClinicInfo(
            cid,
            name,
            None if rating is None else float(rating),
            reviews,
            data_date,
            website,
            instagram,
        )
        cur.execute(
            "select category_code, district from public.markets where id = %s", (market_id,)
        )
        category, district = cur.fetchone()
        cur.execute(
            "select c.id, c.name, "
            "coalesce(array_agg(a.alias) filter (where a.alias is not null), '{}') "
            "from public.clinics c join public.clinic_markets cm on cm.clinic_id = c.id "
            "left join public.aliases a on a.clinic_id = c.id "
            "where cm.market_id = %s group by c.id",
            (market_id,),
        )
        market_names = {cid: [n, *aliases] for cid, n, aliases in cur.fetchall()}
        cur.execute(
            "select c.id, c.website, c.instagram, c.rating, c.review_count from public.clinics c "
            "join public.clinic_markets cm on cm.clinic_id = c.id where cm.market_id = %s",
            (market_id,),
        )
        profiles = {
            cid: {"website": w, "instagram": ig,
                  "rating": None if r is None else float(r), "reviews": n}
            for cid, w, ig, r, n in cur.fetchall()
        }  # fmt: skip
        cur.execute(
            "select r.id, r.surface, q.text, (r.created_at at time zone 'America/Lima')::date, "
            "coalesce(r.text, '') from public.responses r "
            "join public.questions q on q.id = r.question_id "
            "join public.runs ru on ru.id = r.run_id "
            "where ru.market_id = %s and ru.month = %s and ru.kind = 'api' "
            "and ru.status = 'reviewed'",
            (market_id, month),
        )
        answers = cur.fetchall()
        cur.execute(
            "select m.response_id, m.position, m.raw_name, m.clinic_id from public.mentions m "
            "join public.responses r on r.id = m.response_id "
            "join public.runs ru on ru.id = r.run_id "
            "where ru.market_id = %s and ru.month = %s and ru.kind = 'api' "
            "and ru.status = 'reviewed' and m.status <> 'discarded'",
            (market_id, month),
        )
        by_response: dict[int, list[tuple[int, str, int | None]]] = {}
        for response_id, position, raw_name, mention_clinic in cur.fetchall():
            by_response.setdefault(response_id, []).append((position, raw_name, mention_clinic))
        cur.execute(
            "select detectable_diff from public.monthly_scores where market_id = %s and month = %s "
            "and clinic_id = %s and surface = 'combined'",
            (market_id, month, clinic_id),
        )
        detectable = cur.fetchone()
        cur.execute(
            "select r.id, r.question_id, t.form, s.url, s.domain, s.source_type "
            "from public.responses r join public.questions q on q.id = r.question_id "
            "join public.templates t on t.id = q.template_id "
            "join public.runs ru on ru.id = r.run_id "
            "left join public.sources s on s.response_id = r.id "
            "where ru.market_id = %s and ru.month = %s and ru.kind = 'api' "
            "and ru.status = 'reviewed'",
            (market_id, month),
        )
        meta: dict[int, tuple[int, str, list[tuple[str, str, str]]]] = {}
        for rid, question_id, form, url, domain, kind in cur.fetchall():
            item = meta.setdefault(rid, (question_id, form, []))
            if url:
                item[2].append((url, domain, kind))
    citations, total = load_citations(conn, market_id, month)
    deep_answers = [
        Answer(
            rid, surface, meta[rid][0], question, meta[rid][1], asked_on, text,
            frozenset(c for _, _, c in by_response.get(rid, []) if c is not None),
            tuple(meta[rid][2]),
        )
        for rid, surface, question, asked_on, text in answers
        if rid in meta
    ]  # fmt: skip
    examples = [
        ExampleAnswer(surface, question, asked_on, text, by_response.get(rid, []))
        for rid, surface, question, asked_on, text in answers
    ]
    google_without_names = sum(
        1
        for rid, surface, *_ in answers
        if surface == "google_ai_mode" and not by_response.get(rid)
    )
    return ReportData(
        clinic=clinic,
        category=category,
        district=district,
        month=month,
        ranking=rows,
        examples=examples,
        citations=citations,
        total_answers=total,
        detectable_diff=float(detectable[0]) if detectable and detectable[0] is not None else None,
        google_without_names=google_without_names,
        market_names=market_names,
        competitors=competitors,
        deep_answers=deep_answers,
        profiles=profiles,
    )
