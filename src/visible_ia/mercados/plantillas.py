"""Question templates approved on 2026-09-26 (docs/03-especificacion/plantillas-preguntas.md).

The CSV is a verbatim copy of the approved document: do not edit the wording here (the PRD
is frozen); changes go through /cambio.
"""

import csv
from dataclasses import dataclass
from pathlib import Path

import psycopg

TEMPLATES_CSV = Path(__file__).resolve().parents[3] / "data" / "plantillas-preguntas.csv"
CATEGORIES = ("IMP", "EDE", "MES", "DER")
FORMS = ("M", "R", "C", "P")
PER_CATEGORY = 10
PLACEHOLDER = "{d}"


@dataclass(frozen=True)
class Template:
    id: str
    category: str
    form: str
    text: str
    origin: str

    def render(self, district: str) -> str:
        return self.text.replace(PLACEHOLDER, district)


class InvalidTemplates(ValueError):
    pass


def read_templates(path: Path = TEMPLATES_CSV) -> list[Template]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = [
            Template(r["id"], r["rubro"], r["forma"], r["texto"], r["origen"])
            for r in csv.DictReader(f)
        ]
    validate(rows)
    return rows


def validate(templates: list[Template]) -> None:
    errors = []
    ids = [t.id for t in templates]
    if len(ids) != len(set(ids)):
        errors.append("hay ids repetidos")
    for t in templates:
        if t.category not in CATEGORIES:
            errors.append(f"{t.id}: rubro desconocido {t.category}")
        if not t.id.startswith(f"{t.category}-"):
            errors.append(f"{t.id}: el id no coincide con el rubro {t.category}")
        if t.form not in FORMS:
            errors.append(f"{t.id}: forma desconocida {t.form}")
        if t.text.count(PLACEHOLDER) != 1:
            errors.append(f"{t.id}: debe contener {PLACEHOLDER} exactamente una vez")
    for category in CATEGORIES:
        n = sum(t.category == category for t in templates)
        if n != PER_CATEGORY:
            errors.append(f"{category}: tiene {n} plantillas (se esperan {PER_CATEGORY})")
    if errors:
        raise InvalidTemplates("; ".join(errors))


def upsert_templates(conn: psycopg.Connection, templates: list[Template]) -> int:
    """Insert or update templates (version 1). Idempotent: loading twice creates no duplicates."""
    with conn.transaction(), conn.cursor() as cur:
        cur.executemany(
            """
            insert into public.templates (id, category_code, form, text, origin, version, active)
            values (%s, %s, %s, %s, %s, 1, true)
            on conflict (id) do update set
                category_code = excluded.category_code,
                form = excluded.form,
                text = excluded.text,
                origin = excluded.origin
            """,
            [(t.id, t.category, t.form, t.text, t.origin) for t in templates],
        )
    return len(templates)
