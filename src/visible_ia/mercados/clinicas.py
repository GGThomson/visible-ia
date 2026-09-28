"""Clinic import from a CSV built by hand from Google Maps (HU-02). No scraping.

Minimum columns: nombre, distrito, maps_url. Optional: direccion, rating, resenas, web, instagram
and alias (extra names separated by ';', e.g. the variants seen in the AI answers).
Accepts ',' or ';' as separator (Excel in Spanish saves with ';'), UTF-8 with or without BOM,
decimal commas ("4,5") and thousands separators ("1.020" / "1,020").
"""

import csv
import io
import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import psycopg

from visible_ia.mercados.alias import add_alias, add_derived_aliases

REQUIRED = ("nombre", "distrito", "maps_url")
OPTIONAL = ("direccion", "rating", "resenas", "web", "instagram", "alias")


@dataclass(frozen=True)
class ClinicRow:
    name: str
    district: str
    maps_url: str
    address: str | None = None
    rating: float | None = None
    review_count: int | None = None
    website: str | None = None
    instagram: str | None = None
    aliases: tuple[str, ...] = ()


@dataclass(frozen=True)
class RowError:
    line: int
    message: str


class InvalidClinicsFile(ValueError):
    pass


def _normalize_header(name: str) -> str:
    plain = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", "_", plain.strip().lower())


def _optional(value: str | None) -> str | None:
    value = (value or "").strip()
    return value or None


def _instagram(value: str | None) -> str | None:
    """Profile URL or handle without the query string Maps adds (?hl=en, ?igsh=…)."""
    value = _optional(value)
    return re.split(r"[?#]", value, maxsplit=1)[0] if value else None


def _parse_rating(value: str | None) -> float | None:
    value = _optional(value)
    if value is None:
        return None
    rating = float(value.replace(",", "."))
    if not 0 <= rating <= 5:
        raise ValueError("rating fuera de 0–5")
    return round(rating, 1)


def _parse_count(value: str | None) -> int | None:
    value = _optional(value)
    if value is None:
        return None
    digits = re.sub(r"[.,\s]", "", value)
    if not digits.isdigit():
        raise ValueError(f"reseñas no es un número: {value}")
    return int(digits)


def parse_clinics_csv(text: str) -> tuple[list[ClinicRow], list[RowError]]:
    text = text.lstrip("﻿")
    first_line = text.splitlines()[0] if text else ""
    delimiter = ";" if first_line.count(";") > first_line.count(",") else ","
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    if reader.fieldnames is None:
        raise InvalidClinicsFile("El archivo está vacío")
    headers = {_normalize_header(h): h for h in reader.fieldnames}
    missing = [c for c in REQUIRED if c not in headers]
    if missing:
        raise InvalidClinicsFile(f"Faltan columnas obligatorias: {', '.join(missing)}")

    rows: list[ClinicRow] = []
    errors: list[RowError] = []
    for line, raw in enumerate(reader, start=2):
        get = {key: raw.get(original) for key, original in headers.items()}
        name, district, maps_url = (_optional(get.get(c)) for c in REQUIRED)
        if not (name and district and maps_url):
            errors.append(RowError(line, "faltan nombre, distrito o maps_url"))
            continue
        if not maps_url.startswith(("http://", "https://")):
            errors.append(RowError(line, "maps_url debe empezar con http(s)://"))
            continue
        try:
            rows.append(
                ClinicRow(
                    name=name,
                    district=district,
                    maps_url=maps_url,
                    address=_optional(get.get("direccion")),
                    rating=_parse_rating(get.get("rating")),
                    review_count=_parse_count(get.get("resenas")),
                    website=_optional(get.get("web")),
                    instagram=_instagram(get.get("instagram")),
                    aliases=tuple(
                        a.strip() for a in (get.get("alias") or "").split(";") if a.strip()
                    ),
                )
            )
        except ValueError as exc:
            errors.append(RowError(line, str(exc)))
    return rows, errors


def read_clinics_csv(path: Path) -> tuple[list[ClinicRow], list[RowError]]:
    return parse_clinics_csv(path.read_text(encoding="utf-8-sig"))


def import_clinics(
    conn: psycopg.Connection, market_id: int, rows: list[ClinicRow], data_date: date
) -> tuple[int, int]:
    """Create or update clinics by maps_url, link them to the market and add automatic,
    non-generic aliases derived from the name (HU-03). Returns (created, updated)."""
    created = updated = 0
    with conn.transaction(), conn.cursor() as cur:
        cur.execute("select 1 from public.markets where id = %s", (market_id,))
        if cur.fetchone() is None:
            raise InvalidClinicsFile(f"No existe el mercado {market_id}")
        for row in rows:
            cur.execute(
                """
                insert into public.clinics
                    (name, address, district, rating, review_count, website, instagram,
                     maps_url, data_date)
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                on conflict (maps_url) do update set
                    name = excluded.name,
                    address = coalesce(excluded.address, clinics.address),
                    district = excluded.district,
                    rating = coalesce(excluded.rating, clinics.rating),
                    review_count = coalesce(excluded.review_count, clinics.review_count),
                    website = coalesce(excluded.website, clinics.website),
                    instagram = coalesce(excluded.instagram, clinics.instagram),
                    data_date = excluded.data_date
                returning id, (xmax = 0) as inserted
                """,
                (row.name, row.address, row.district, row.rating, row.review_count,
                 row.website, row.instagram, row.maps_url, data_date),
            )  # fmt: skip
            clinic_id, inserted = cur.fetchone()
            created += inserted
            updated += not inserted
            add_derived_aliases(conn, clinic_id, row.name)
            for alias in row.aliases:
                add_alias(conn, clinic_id, alias)
            cur.execute(
                "insert into public.clinic_markets (clinic_id, market_id) values (%s, %s) "
                "on conflict do nothing",
                (clinic_id, market_id),
            )
    return created, updated


def list_market_clinics(conn: psycopg.Connection, market_id: int) -> list[tuple]:
    with conn.cursor() as cur:
        cur.execute(
            "select c.id, c.name, c.rating, c.review_count, c.data_date "
            "from public.clinics c join public.clinic_markets cm on cm.clinic_id = c.id "
            "where cm.market_id = %s order by c.name",
            (market_id,),
        )
        return cur.fetchall()
