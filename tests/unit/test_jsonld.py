import json
from pathlib import Path

import pytest

from visible_ia.jsonld import build, instagram_url, script_tag, validate

JS = Path(__file__).resolve().parents[2] / "web" / "panel" / "jsonld.js"

CASES = [
    dict(name="Clínica Dental Cano", category="IMP", district="Miraflores",
         address="Ca. Schell 343, Miraflores 15074", website="https://clinicadentalcano.pe/",
         instagram="https://www.instagram.com/clinicadentalcano/?hl=en",
         maps_url="https://maps.app.goo.gl/1cZgomxuEWQYQGSF8"),
    dict(name="Derma Surco", category="DER", district="Surco", instagram="@dermasurco",
         phone="+51 1 234 5678", opening_hours=["Mo-Fr 09:00-19:00", "Sa 09:00-13:00"],
         extra_same_as=["https://www.doctoralia.pe/clinicas/derma-surco"]),
    dict(name="Estética Uno", category="MES", district="San Isidro"),
]  # fmt: skip


@pytest.mark.parametrize("case", CASES, ids=["dentist", "dermatology", "minimal"])
def test_built_schema_is_valid(case):
    data = build(**case)
    assert validate(data) == []
    expected = {"IMP": "Dentist", "DER": "MedicalClinic", "MES": "MedicalClinic"}
    assert data["@type"] == expected[case["category"]]
    assert "aggregateRating" not in data and "review" not in data


def test_fields_and_same_as():
    data = build(**CASES[0])
    assert data["address"] == {
        "@type": "PostalAddress",
        "streetAddress": "Ca. Schell 343, Miraflores 15074",
        "addressLocality": "Miraflores",
        "addressRegion": "Lima",
        "addressCountry": "PE",
    }
    assert data["sameAs"] == [
        "https://maps.app.goo.gl/1cZgomxuEWQYQGSF8",
        "https://www.instagram.com/clinicadentalcano/",
    ]
    derma = build(**CASES[1])
    assert derma["medicalSpecialty"] == "Dermatology"
    assert derma["sameAs"][0] == "https://www.instagram.com/dermasurco/"
    assert "medicalSpecialty" not in build(**CASES[2])


@pytest.mark.parametrize(
    "change, error",
    [
        ({"@context": "http://schema.org"}, "@context"),
        ({"@type": "Store"}, "@type"),
        ({"name": " "}, "name"),
        ({"url": "http://x.pe"}, "url"),
        ({"telephone": "999999999"}, "telephone"),
        ({"openingHours": ["Lunes a viernes 9-7"]}, "openingHours"),
        ({"sameAs": ["www.x.pe"]}, "sameAs"),
        ({"aggregateRating": {"ratingValue": 5}}, "aggregateRating"),
    ],
)
def test_validator_catches_structure_errors(change, error):
    data = {**build(**CASES[0]), **change}
    assert any(error in e for e in validate(data))


def test_instagram_handles_and_script_tag():
    assert instagram_url("@clinica") == "https://www.instagram.com/clinica/"
    assert instagram_url(None) is None
    assert (
        instagram_url("https://www.instagram.com/x/?hl=es-la#top") == "https://www.instagram.com/x/"
    )
    tag = script_tag(build(**CASES[2]))
    assert tag.startswith('<script type="application/ld+json">') and "Estética Uno" in tag
    json.loads(tag.split(">", 1)[1].rsplit("<", 1)[0])


def test_panel_javascript_builds_the_same_object():
    playwright = pytest.importorskip("playwright.sync_api")
    with playwright.sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception as exc:
            pytest.skip(str(exc))
        page = browser.new_page()
        page.add_script_tag(content=JS.read_text(encoding="utf-8"))
        for case in CASES:
            js_input = {
                "name": case["name"],
                "category": case["category"],
                "district": case["district"],
                "address": case.get("address"),
                "website": case.get("website"),
                "instagram": case.get("instagram"),
                "mapsUrl": case.get("maps_url"),
                "phone": case.get("phone"),
                "openingHours": case.get("opening_hours"),
                "extraSameAs": case.get("extra_same_as"),
            }
            assert page.evaluate("c => buildJsonLd(c)", js_input) == build(**case), case["name"]
        browser.close()
