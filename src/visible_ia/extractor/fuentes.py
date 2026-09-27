"""Source types (HU-12): Google profile, Doctoralia, own website, social, directory, press, other.

Order of the rules:
1. The exact host of a market clinic's website -> own website.
2. The known-domains table (data/dominios.csv); the longest matching suffix wins, so
   sites.google.com is not taken for google.com.
3. Institutional sites (.gob, .gov, .edu, guilds, academic) -> other.
4. A domain made of clinic words (dental, clínica, derma...) -> own website: it is the web of
   a clinic, even one not yet in the market list.
5. Anything else -> other.
"""

import csv
from functools import cache
from pathlib import Path
from typing import Literal

from visible_ia.motor.corrida import domain_of

DOMAINS_CSV = Path(__file__).resolve().parents[3] / "data" / "dominios.csv"

SourceType = Literal[
    "google_profile", "doctoralia", "own_website", "social", "directory", "press", "other"
]
SOURCE_TYPES: tuple[str, ...] = SourceType.__args__  # type: ignore[attr-defined]

INSTITUTIONAL_SUFFIXES = (".gob.pe", ".gov", ".edu", ".edu.pe", ".org.pe", ".nih.gov", ".ri.gov")
INSTITUTIONAL_PARTS = ("academy.", "pmc.", "buscador.")
CLINIC_WORDS = (
    "dental", "dent", "clinica", "clinic", "implant", "odonto", "ortodon", "smile", "sonris",
    "derma", "estetic", "esthetic", "piel", "laser", "maxilo", "medic",
)  # fmt: skip


@cache
def known_domains(path: Path = DOMAINS_CSV) -> dict[str, str]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        table = {row["dominio"].strip().lower(): row["tipo"].strip() for row in csv.DictReader(f)}
    unknown = set(table.values()) - set(SOURCE_TYPES)
    if unknown:
        raise ValueError(f"Tipos no válidos en {path.name}: {sorted(unknown)}")
    return table


def _table_type(domain: str, table: dict[str, str]) -> str | None:
    matches = [d for d in table if domain == d or domain.endswith(f".{d}")]
    return table[max(matches, key=len)] if matches else None


def classify(url_or_domain: str, market_websites: set[str] | None = None) -> str:
    """Type of one source. `market_websites` are the websites of the market's clinics."""
    value = url_or_domain.strip()
    domain = domain_of(value) if "://" in value else value.lower().removeprefix("www.")
    if not domain:
        return "other"
    own = {
        domain_of(w) if "://" in w else w.lower().removeprefix("www.")
        for w in market_websites or ()
    }
    if domain in own:
        return "own_website"
    found = _table_type(domain, known_domains())
    if found:
        return found
    if domain.endswith(INSTITUTIONAL_SUFFIXES) or domain.startswith(INSTITUTIONAL_PARTS):
        return "other"
    if any(word in domain for word in CLINIC_WORDS):
        return "own_website"
    return "other"
