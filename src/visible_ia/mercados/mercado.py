"""Markets (category + district) and their versioned question bank (HU-01).

Functions never commit on their own: they run inside `conn.transaction()`, which becomes a
savepoint when the caller already opened a transaction (tests roll everything back).
"""

from dataclasses import dataclass

import psycopg
from psycopg import errors

from visible_ia.mercados.plantillas import CATEGORIES, PLACEHOLDER

DISTRICTS = ("Miraflores", "San Isidro", "Surco")


class MarketError(ValueError):
    pass


@dataclass(frozen=True)
class Question:
    id: int
    template_id: str
    text: str
    version: int


def validate_market(category: str, district: str) -> None:
    if category not in CATEGORIES:
        raise MarketError(f"Rubro no válido: {category} (usa {', '.join(CATEGORIES)})")
    if district not in DISTRICTS:
        raise MarketError(f"Distrito no válido: {district} (usa {', '.join(DISTRICTS)})")


def render_questions(templates: list[tuple[str, str]], district: str) -> list[tuple[str, str]]:
    """(template_id, text with {d}) -> (template_id, final text)."""
    return [(tid, text.replace(PLACEHOLDER, district)) for tid, text in templates]


def create_market(conn: psycopg.Connection, category: str, district: str) -> int:
    validate_market(category, district)
    with conn.transaction(), conn.cursor() as cur:
        cur.execute(
            "select id, text from public.templates where category_code = %s and active order by id",
            (category,),
        )
        templates = cur.fetchall()
        if len(templates) != 10:
            raise MarketError(
                f"El rubro {category} tiene {len(templates)} plantillas activas (se esperan 10). "
                "Ejecuta primero: visible-ia plantillas cargar"
            )
        try:
            with conn.transaction():
                cur.execute(
                    "insert into public.markets (category_code, district) values (%s, %s) "
                    "returning id",
                    (category, district),
                )
        except errors.UniqueViolation:
            raise MarketError(f"El mercado {category} · {district} ya existe") from None
        (market_id,) = cur.fetchone()
        cur.executemany(
            "insert into public.questions (market_id, template_id, text, version) "
            "values (%s, %s, %s, 1)",
            [(market_id, tid, text) for tid, text in render_questions(templates, district)],
        )
    return market_id


def current_version(conn: psycopg.Connection, market_id: int) -> int:
    with conn.cursor() as cur:
        cur.execute("select question_set_version from public.markets where id = %s", (market_id,))
        row = cur.fetchone()
    if row is None:
        raise MarketError(f"No existe el mercado {market_id}")
    return row[0]


def list_questions(
    conn: psycopg.Connection, market_id: int, version: int | None = None
) -> list[Question]:
    version = version or current_version(conn, market_id)
    with conn.cursor() as cur:
        cur.execute(
            "select id, template_id, text, version from public.questions "
            "where market_id = %s and version = %s order by template_id",
            (market_id, version),
        )
        return [Question(*row) for row in cur.fetchall()]


def edit_question(conn: psycopg.Connection, market_id: int, template_id: str, text: str) -> int:
    """Change one question. If the market already has runs, create a new bank version so the
    history stays tied to the version it was measured with. Returns the version edited."""
    text = text.strip()
    if not text:
        raise MarketError("El texto de la pregunta no puede estar vacío")
    version = current_version(conn, market_id)
    questions = list_questions(conn, market_id, version)
    if template_id not in {q.template_id for q in questions}:
        raise MarketError(f"El mercado {market_id} no tiene la pregunta {template_id}")
    with conn.transaction(), conn.cursor() as cur:
        cur.execute("select exists(select 1 from public.runs where market_id = %s)", (market_id,))
        (has_runs,) = cur.fetchone()
        if not has_runs:
            cur.execute(
                "update public.questions set text = %s "
                "where market_id = %s and template_id = %s and version = %s",
                (text, market_id, template_id, version),
            )
            return version
        new_version = version + 1
        cur.executemany(
            "insert into public.questions (market_id, template_id, text, version) "
            "values (%s, %s, %s, %s)",
            [
                (
                    market_id,
                    q.template_id,
                    text if q.template_id == template_id else q.text,
                    new_version,
                )
                for q in questions
            ],
        )
        cur.execute(
            "update public.markets set question_set_version = %s where id = %s",
            (new_version, market_id),
        )
    return new_version


def list_markets(conn: psycopg.Connection) -> list[tuple[int, str, str, int, bool]]:
    with conn.cursor() as cur:
        cur.execute(
            "select id, category_code, district, question_set_version, active "
            "from public.markets order by id"
        )
        return cur.fetchall()
