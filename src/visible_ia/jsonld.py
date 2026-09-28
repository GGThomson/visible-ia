"""Schema.org JSON-LD of a clinic site, ready to paste in its website (C8-T04, HU-18).

Dentist for dental categories, MedicalClinic (with its specialty) for the others. Only data
we hold about the clinic; no ratings or reviews (Google does not allow a business to mark
up reviews about itself). The panel builds the same object in web/panel/jsonld.js; a test
checks both give the same result.
"""

import re
from typing import Any

TYPE_BY_CATEGORY = {
    "IMP": "Dentist",
    "EDE": "Dentist",
    "MES": "MedicalClinic",
    "DER": "MedicalClinic",
}
# schema.org has no "aesthetic medicine" specialty: only dermatology gets one.
SPECIALTY = {"DER": "Dermatology"}
ALLOWED_TYPES = {"Dentist", "MedicalClinic"}
OPENING = re.compile(r"^(Mo|Tu|We|Th|Fr|Sa|Su)(-(Mo|Tu|We|Th|Fr|Sa|Su))?(,(Mo|Tu|We|Th|Fr|Sa|Su))* "
                     r"([01]\d|2[0-3]):[0-5]\d-([01]\d|2[0-3]):[0-5]\d$")  # fmt: skip
PHONE = re.compile(r"^\+\d[\d ]{6,18}$")


def instagram_url(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip()
    if value.startswith("http"):
        return re.split(r"[?#]", value, maxsplit=1)[0]  # drop ?hl=en, ?igsh=… and the like
    return f"https://www.instagram.com/{value.lstrip('@').strip('/')}/"


def build(
    *,
    name: str,
    category: str,
    district: str,
    address: str | None = None,
    website: str | None = None,
    instagram: str | None = None,
    maps_url: str | None = None,
    phone: str | None = None,
    opening_hours: list[str] | None = None,
    extra_same_as: list[str] | None = None,
) -> dict[str, Any]:
    data: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": TYPE_BY_CATEGORY.get(category, "MedicalClinic"),
        "name": name,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": address or "",
            "addressLocality": district,
            "addressRegion": "Lima",
            "addressCountry": "PE",
        },
    }
    if category in SPECIALTY:
        data["medicalSpecialty"] = SPECIALTY[category]
    if website:
        data["url"] = website
    if phone:
        data["telephone"] = phone
    if opening_hours:
        data["openingHours"] = opening_hours
    if maps_url:
        data["hasMap"] = maps_url
    same_as = [u for u in (maps_url, instagram_url(instagram), *(extra_same_as or [])) if u]
    if same_as:
        data["sameAs"] = list(dict.fromkeys(same_as))
    if not address:
        del data["address"]["streetAddress"]
    return data


def validate(data: dict[str, Any]) -> list[str]:
    """Local structural checks against schema.org's LocalBusiness shape. [] = valid."""
    errors = []
    if data.get("@context") != "https://schema.org":
        errors.append("@context debe ser https://schema.org")
    if data.get("@type") not in ALLOWED_TYPES:
        errors.append(f"@type no válido: {data.get('@type')}")
    if not str(data.get("name", "")).strip():
        errors.append("falta name")
    address = data.get("address") or {}
    if address.get("@type") != "PostalAddress" or not address.get("addressLocality"):
        errors.append("address debe ser PostalAddress con addressLocality")
    if address.get("addressCountry") != "PE":
        errors.append("addressCountry debe ser PE")
    for key in ("url", "hasMap"):
        if key in data and not str(data[key]).startswith("https://"):
            errors.append(f"{key} debe ser una URL https")
    for url in data.get("sameAs", []):
        if not str(url).startswith("https://"):
            errors.append(f"sameAs con URL no https: {url}")
    if "telephone" in data and not PHONE.match(data["telephone"]):
        errors.append("telephone debe ir con código de país, p. ej. +51 1 234 5678")
    for spec in data.get("openingHours", []):
        if not OPENING.match(spec):
            errors.append(f"openingHours no válido: {spec} (formato: Mo-Fr 09:00-18:00)")
    for forbidden in ("aggregateRating", "review"):
        if forbidden in data:
            errors.append(f"{forbidden} no se incluye: Google no permite reseñas propias")
    return errors


def script_tag(data: dict[str, Any]) -> str:
    import json

    return (
        '<script type="application/ld+json">\n'
        + json.dumps(data, ensure_ascii=False, indent=2)
        + "\n</script>"
    )
