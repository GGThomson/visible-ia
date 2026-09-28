"""Prioritized checklist of a site (C8-T03, HU-17).

From data/checklist.toml: keep the tasks whose condition applies to the site and raise the
ones whose sources the AI cites most in its market. Tasks already done stay done; pending
tasks that no longer apply are removed; the order is stored in tasks.priority.
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path

import psycopg

from visible_ia.informes.contexto import TREATMENT
from visible_ia.motor.corrida import domain_of

CATALOG = Path(__file__).resolve().parents[2] / "data" / "checklist.toml"
MIN_REVIEWS = 100
DOCTORALIA_SHARE = 10.0  # % of the market's answers citing Doctoralia


@dataclass(frozen=True)
class SiteProfile:
    site_id: int
    category: str
    district: str
    website: str | None
    instagram: str | None
    rating: float | None
    reviews: int | None
    type_shares: dict[str, float]  # % of the market's answers citing each source type
    cited_domains: set[str]  # domains cited in the market's answers


@dataclass(frozen=True)
class Task:
    code: str
    priority: int
    title: str
    detail: str


def load_catalog(path: Path = CATALOG) -> list[dict]:
    return tomllib.loads(path.read_text(encoding="utf-8"))["tarea"]


def applies(condition: str, p: SiteProfile) -> bool:
    website_domain = domain_of(p.website) if p.website and "://" in p.website else None
    return {
        "siempre": True,
        "pocas_resenas": p.reviews is None or p.reviews < MIN_REVIEWS,
        "mercado_cita_doctoralia": p.type_shares.get("doctoralia", 0) >= DOCTORALIA_SHARE,
        "web_no_citada": website_domain is None or website_domain not in p.cited_domains,
        "sin_redes": not p.instagram,
    }[condition]


def prioritize(profile: SiteProfile, catalog: list[dict] | None = None) -> list[Task]:
    """Applicable tasks in priority order: base order, raised by how much the market cites
    their source (each 10 % of answers moves a task up half a place)."""
    catalog = catalog or load_catalog()
    values = {
        "tratamiento": TREATMENT.get(profile.category, "tu especialidad"),
        "distrito": profile.district,
    }
    chosen = [t for t in catalog if applies(t["condicion"], profile)]
    chosen.sort(key=lambda t: t["orden"] - profile.type_shares.get(t["fuente"], 0) / 20)
    return [
        Task(t["codigo"], i, t["titulo"].format(**values), t["detalle"].format(**values))
        for i, t in enumerate(chosen, start=1)
    ]


# --- database ------------------------------------------------------------------------------


def load_profile(conn: psycopg.Connection, site_id: int) -> SiteProfile:
    with conn.cursor() as cur:
        cur.execute(
            "select s.market_id, m.category_code, m.district, c.website, c.instagram, c.rating, "
            "c.review_count from public.sites s join public.markets m on m.id = s.market_id "
            "join public.clinics c on c.id = s.clinic_id where s.id = %s",
            (site_id,),
        )
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"No existe la sede {site_id}")
        market_id, category, district, website, instagram, rating, reviews = row
        cur.execute(
            "select max(ru.month) from public.runs ru where ru.market_id = %s "
            "and ru.kind = 'api' and ru.status = 'reviewed'",
            (market_id,),
        )
        (month,) = cur.fetchone()
        shares: dict[str, float] = {}
        domains: set[str] = set()
        if month is not None:
            cur.execute(
                "select count(*) from public.responses r join public.runs ru on ru.id = r.run_id "
                "where ru.market_id = %s and ru.month = %s and ru.kind = 'api' "
                "and ru.status = 'reviewed'",
                (market_id, month),
            )
            (total,) = cur.fetchone()
            cur.execute(
                "select s.source_type, count(distinct s.response_id), "
                "array_agg(distinct s.domain) from public.sources s "
                "join public.responses r on r.id = s.response_id "
                "join public.runs ru on ru.id = r.run_id where ru.market_id = %s "
                "and ru.month = %s and ru.kind = 'api' and ru.status = 'reviewed' "
                "group by s.source_type",
                (market_id, month),
            )
            for source_type, answers, type_domains in cur.fetchall():
                shares[source_type] = 100 * answers / total if total else 0
                domains.update(type_domains)
    return SiteProfile(
        site_id, category, district, website, instagram,
        None if rating is None else float(rating), reviews, shares, domains,
    )  # fmt: skip


def generate(conn: psycopg.Connection, site_id: int) -> list[Task]:
    """Create or refresh the site's checklist. Done tasks are kept as they are."""
    tasks = prioritize(load_profile(conn, site_id))
    codes = [t.code for t in tasks]
    with conn.transaction(), conn.cursor() as cur:
        cur.execute(
            "delete from public.tasks where site_id = %s and status = 'pending' "
            "and not (code = any(%s))",
            (site_id, codes),
        )
        for t in tasks:
            cur.execute(
                "insert into public.tasks (site_id, code, priority, title, detail) "
                "values (%s, %s, %s, %s, %s) on conflict (site_id, code) do update set "
                "priority = excluded.priority, title = excluded.title, detail = excluded.detail",
                (site_id, t.code, t.priority, t.title, t.detail),
            )
    return tasks
