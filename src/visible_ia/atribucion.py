"""Attribution kit (C9-T02, HU-25): how a clinic tells the patients who came through the AI.

Three tools, shown in the panel and in the kit PDF:
- an intake question ("¿Cómo nos conociste?") with an "AI" option; the clinic saves the monthly
  count in its panel (public.attributions, migration 0008) and the monthly report shows it;
- its website link with UTM parameters for each place the AI reads (Google profile,
  Doctoralia, Instagram), so its web analytics can tell where visits come from;
- a suggested coupon code to publish only in those places.

The panel builds the same links and coupon in web/panel/atribucion.js; a test checks both give
the same result.
"""

import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import psycopg

INTAKE_QUESTION = "¿Cómo nos conociste?"
INTAKE_OPTIONS = (
    "Google o Google Maps",
    "ChatGPT u otra IA (Gemini, Copilot…)",
    "Instagram, Facebook o TikTok",
    "Doctoralia",
    "Recomendación de un amigo o familiar",
    "Otro",
)
AI_OPTION = INTAKE_OPTIONS[1]

# (where the link goes, utm_source, utm_medium, utm_campaign)
PLACEMENTS = (
    ("Ficha de Google (botón «Sitio web»)", "google", "organic", "ficha-google"),
    ("Perfil de Doctoralia (enlace a tu web)", "doctoralia", "referral", "perfil"),
    ("Bio de Instagram", "instagram", "social", "bio"),
)
# Words that say nothing about which clinic it is, skipped when suggesting the coupon code.
GENERIC = {
    "clinica", "clinicas", "centro", "consultorio", "dental", "dentales", "odontologica",
    "odontologico", "odontologia", "estetica", "medica", "medico", "dermatologia", "dr", "dra",
    "de", "del", "la", "las", "el", "los", "y", "en", "sede", "spa",
}  # fmt: skip
MAX_CODE_WORD = 14


@dataclass(frozen=True)
class UtmLink:
    placement: str
    url: str


def tagged_url(website: str, source: str, medium: str, campaign: str) -> str | None:
    """The website with utm_* set (other parameters kept), or None if it is not a web URL."""
    value = (website or "").strip()
    if not value:
        return None
    if not re.match(r"^https?://", value, flags=re.IGNORECASE):
        value = "https://" + value
    parts = urlsplit(value)
    if not parts.hostname or "." not in parts.hostname:
        return None
    query = [(k, v) for k, v in parse_qsl(parts.query) if not k.startswith("utm_")]
    query += [("utm_source", source), ("utm_medium", medium), ("utm_campaign", campaign)]
    netloc = parts.hostname.lower() + (f":{parts.port}" if parts.port else "")
    return urlunsplit(
        (parts.scheme.lower(), netloc, parts.path or "/", urlencode(query), parts.fragment)
    )


def utm_links(website: str | None) -> list[UtmLink]:
    links = []
    for placement, source, medium, campaign in PLACEMENTS:
        url = tagged_url(website or "", source, medium, campaign)
        if url:
            links.append(UtmLink(placement, url))
    return links


def suggested_coupon(clinic_name: str) -> str:
    """'IA-' plus the first distinctive word of the name, e.g. 'IA-SMILES'."""
    plain = unicodedata.normalize("NFD", clinic_name)
    plain = "".join(c for c in plain if not unicodedata.combining(c)).upper()
    words = [w for w in re.split(r"[^A-Z0-9]+", plain) if w]
    word = next((w for w in words if w.lower() not in GENERIC and len(w) > 1), None)
    return "IA-" + (word or "VISIBLE")[:MAX_CODE_WORD]


# --- database ------------------------------------------------------------------------------


def save_count(conn: psycopg.Connection, site_id: int, month: date, patients: int) -> None:
    if month.day != 1:
        raise ValueError("El mes es AAAA-MM")
    if not 0 <= patients <= 10000:
        raise ValueError("El número de pacientes debe estar entre 0 y 10 000")
    with conn.transaction(), conn.cursor() as cur:
        cur.execute("select 1 from public.sites where id = %s", (site_id,))
        if cur.fetchone() is None:
            raise ValueError(f"No existe la sede {site_id}")
        cur.execute(
            "insert into public.attributions (site_id, month, ai_patients) values (%s, %s, %s) "
            "on conflict (site_id, month) do update set ai_patients = excluded.ai_patients, "
            "updated_at = now()",
            (site_id, month, patients),
        )


def load_counts(conn: psycopg.Connection, site_id: int, until: date) -> dict[date, int]:
    """Monthly counts of a site up to `until`, oldest first."""
    with conn.cursor() as cur:
        cur.execute(
            "select month, ai_patients from public.attributions "
            "where site_id = %s and month <= %s order by month",
            (site_id, until),
        )
        return dict(cur.fetchall())


def kit_context(clinic_name: str, website: str | None, brand: dict, panel_url: str) -> dict:
    """What the kit PDF shows (templates/kit.html.j2)."""
    return {
        "marca": brand,
        "clinica": clinic_name,
        "pregunta": INTAKE_QUESTION,
        "opciones": INTAKE_OPTIONS,
        "opcion_ia": AI_OPTION,
        "enlaces": utm_links(website),
        "cupon": suggested_coupon(clinic_name),
        "panel": panel_url,
    }
