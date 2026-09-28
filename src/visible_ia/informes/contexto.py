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
    missing_pages,
    question_grid,
    question_table,
)
from visible_ia.informes.semaforo import findings, impact, lights
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
QUOTE_CHARS = 320
MD_LINK = re.compile(r"\(?\[([^\]]+)\]\([^)]*\)\)?")


@dataclass(frozen=True)
class ClinicInfo:
    id: int
    name: str
    rating: float | None
    reviews: int | None
    data_date: date | None
    website: str | None


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
    flat = plain_text(a.text)
    anchor = next((raw for _, raw, cid in sorted(a.mentions) if cid == data.clinic.id), None)
    start = (
        max(flat.lower().find(anchor.lower()) - 60, 0)
        if anchor and anchor.lower() in flat.lower()
        else 0
    )
    quote = flat[start : start + QUOTE_CHARS].strip()
    if start > 0:
        quote = "…" + quote
    if start + QUOTE_CHARS < len(flat):
        quote += "…"
    return {
        "superficie": SURFACE_NAMES[a.surface],
        "pregunta": a.question,
        "fecha": a.asked_on.strftime("%d/%m/%Y"),
        "nombres": names,
        "cita": mask_professionals(quote, allowed),
    }


def _recommendations(values: dict[str, Any], applies: dict[str, bool]) -> list[dict[str, str]]:
    items = tomllib.loads(RECOMMENDATIONS_TOML.read_text(encoding="utf-8"))["recomendacion"]
    chosen = [r for r in items if applies.get(r["id"])]
    for r in items:  # always 3: fill with the rest, in priority order
        if len(chosen) >= 3:
            break
        if r not in chosen and r["id"] in ("web", "doctoralia", "mantener"):
            chosen.append(r)
    return [
        {
            "id": r["id"],
            "titulo": r["titulo"].format(**values),
            "texto": r["texto"].format(**values),
            "esfuerzo": r.get("esfuerzo", "medio"),
        }
        for r in chosen[:3]
    ]


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


def _deep_context(data: ReportData, competitors: list, allowed: list[str]) -> dict[str, Any]:
    """Sections of the deeper diagnostic (C-008); empty when there are no stored answers."""
    if not data.deep_answers:
        return {"hay": False}
    leader = next((r for r in data.ranking if r.clinic_id != data.clinic.id), data.ranking[0])
    pages, own = missing_pages(
        data.deep_answers, data.clinic.id, [c.clinic_id for c in competitors], data.clinic.website
    )
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
    }


def _short_url(url: str, limit: int = 60) -> str:
    text = re.sub(r"^https?://(www\.)?", "", url).rstrip("/")
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _position(value: float | None) -> str:
    """Average position when named, Peruvian style (2,3)."""
    return "—" if value is None else f"{value:.1f}".replace(".", ",")


def _share(answers: list[Answer], test) -> float | None:
    return 100 * sum(1 for a in answers if test(a)) / len(answers) if answers else None


def _redesign(data, me, competitors, leader, position, appearances, website_domain, recs):
    """Summary, comparison, question grid and action plan of the redesigned diagnostic."""
    answers = data.deep_answers
    total = data.total_answers

    def cites_web(a):
        return bool(website_domain) and any(
            re.sub(r"^www\.", "", (d or "").lower()) == website_domain for _, d, _ in a.urls
        )

    naming_me = [a for a in answers if data.clinic.id in a.clinics]
    web_answers = sum(1 for a in answers if cites_web(a))
    web_share = (100 * web_answers / len(answers)) if answers else None
    if answers and not website_domain:
        web_share = 0.0
    directory_share = _share(
        naming_me, lambda a: any(k in ("doctoralia", "directory") for _, _, k in a.urls)
    )
    if answers and not naming_me:
        directory_share = 0.0
    light = lights(me.combined, web_share, directory_share, data.clinic.rating,
                   data.clinic.reviews)  # fmt: skip
    by_area = {x.id: x.level for x in light}
    compared = sorted([me, *competitors], key=lambda r: -(r.combined or 0))
    leader_appearances = round((leader.combined or 0) * total / 100)
    clinic_ids = [data.clinic.id, *[c.clinic_id for c in competitors]]
    names = {r.clinic_id: r.name for r in data.ranking}

    def row(r):
        return {
            "nombre": r.name, "es_cliente": r.clinic_id == data.clinic.id,
            "combinado": _pct(r.combined), "bajo": _pct(r.ci_low), "alto": _pct(r.ci_high),
            "chatgpt": _pct(r.chatgpt), "google": _pct(r.google),
            "posicion": _position(r.avg_position),
            "cuota": _pct(r.mention_share), "ancho": max(r.combined or 0, 0.5),
        }  # fmt: skip

    return {
        "cifras": {
            "indice": _pct(me.combined),
            "bajo": _pct(me.ci_low),
            "alto": _pct(me.ci_high),
            "puesto": position,
            "total": len(data.ranking),
            "posicion": _position(me.avg_position),
        },
        "semaforo": [
            {
                "nombre": x.name,
                "mide": x.measures,
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
            is_leader=me.clinic_id == leader.clinic_id,
            rating=data.clinic.rating,
            reviews=data.clinic.reviews,
            web_answers=web_answers,
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
        "plan": [
            {
                **r,
                "impacto": impact(r["id"], by_area),
                "quien": "Tu equipo en el Plan Medir · nosotros en el Plan Gestionado",
            }
            for r in recs
        ],  # fmt: skip
        "web_respuestas": web_answers,
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
    cited_own = {
        r.domain
        for r in top_sources(data.citations, data.total_answers, per_type=999).get(
            "own_website", []
        )
    }
    website_domain = (
        re.sub(r"^https?://(www\.)?", "", data.clinic.website or "").split("/")[0].lower()
        if data.clinic.website
        else ""
    )

    gap = has_gap(data.clinic.rating, data.clinic.reviews, me.combined or 0)
    values = {
        "tratamiento": treatment,
        "distrito": data.district,
        "pct_web": _pct(shares.get("own_website", 0)),
        "pct_doctoralia": _pct(shares.get("doctoralia", 0)),
        "pct_directorios": _pct(shares.get("directory", 0)),
        "google": _pct(me.google),
        "chatgpt": _pct(me.chatgpt),
        "resenas": data.clinic.reviews if data.clinic.reviews is not None else "pocas",
        "rating": data.clinic.rating if data.clinic.rating is not None else "—",
        "indice": _pct(me.combined),
    }
    applies = {
        "brecha": gap,
        "web": not website_domain or website_domain not in cited_own,
        "google": (me.google or 0) < (me.chatgpt or 0) or (me.google or 0) < 10,
        "chatgpt": (me.chatgpt or 0) < (me.google or 0),
        "doctoralia": shares.get("doctoralia", 0) >= 15,
        "resenas": data.clinic.reviews is not None and data.clinic.reviews < 100,
        "mantener": position <= 3,
    }

    recs = _recommendations(values, applies)
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
            "propia_citada": bool(website_domain and website_domain in cited_own),
        },
        "brecha": {
            "rating": data.clinic.rating,
            "resenas": data.clinic.reviews,
            "fecha": data.clinic.data_date.strftime("%d/%m/%Y") if data.clinic.data_date else None,
            "indice": _pct(me.combined),
            "tiene_brecha": gap,
            "lider": {"nombre": leader.name, "indice": _pct(leader.combined)},
        },
        "recomendaciones": recs,
        "profundo": _deep_context(data, competitors, allowed),
        "nuevo": _redesign(
            data, me, competitors, leader, position, appearances, website_domain, recs
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
            "select c.id, c.name, c.rating, c.review_count, c.data_date, c.website "
            "from public.clinics c join public.clinic_markets cm on cm.clinic_id = c.id "
            "where c.id = %s and cm.market_id = %s",
            (clinic_id, market_id),
        )
        row = cur.fetchone()
        if row is None:
            raise ScoreError(f"La clínica {clinic_id} no es del mercado {market_id}")
        cid, name, rating, reviews, data_date, website = row
        clinic = ClinicInfo(
            cid, name, None if rating is None else float(rating), reviews, data_date, website
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
    )
