from pathlib import Path

import pytest

from visible_ia.atribucion import AI_OPTION, INTAKE_OPTIONS, suggested_coupon, tagged_url, utm_links

JS = Path(__file__).resolve().parents[2] / "web" / "panel" / "atribucion.js"

WEBSITES = [
    "https://clinicadentalcano.pe/",
    "clinicadentalcano.pe",
    "http://WWW.Smiles.PE/implantes?ref=maps&utm_source=old#citas",
    "https://odontologists.pe/es/implantes-dentales/",
    "  https://derma.pe  ",
    "",
    "no es una web",
]
NAMES = [
    "Clínica Odontologists",
    "Smiles Peru",
    "Dr. Aldo | Implantes Dentales y Rehabilitación Oral",
    "Centro Odontológico Sonrisa Perfecta",
    "Clínica Dental",
    "Estética Ñuñoa",
]


def test_utm_link_for_each_place():
    links = utm_links("clinicadentalcano.pe")
    assert [link.placement.split(" ")[0] for link in links] == ["Ficha", "Perfil", "Bio"]
    assert links[0].url == (
        "https://clinicadentalcano.pe/?utm_source=google&utm_medium=organic"
        "&utm_campaign=ficha-google"
    )


def test_existing_parameters_are_kept_and_old_utms_replaced():
    url = tagged_url("http://WWW.Smiles.PE/implantes?ref=maps&utm_source=old#citas",
                     "doctoralia", "referral", "perfil")  # fmt: skip
    assert url == (
        "http://www.smiles.pe/implantes?ref=maps&utm_source=doctoralia&utm_medium=referral"
        "&utm_campaign=perfil#citas"
    )


@pytest.mark.parametrize("website", ["", None, "no es una web", "localhost"])
def test_no_links_without_a_website(website):
    assert utm_links(website) == []


@pytest.mark.parametrize(
    "name, code",
    [
        ("Clínica Odontologists", "IA-ODONTOLOGISTS"),
        ("Centro de Rehabilitación Maxilofacial", "IA-REHABILITACION"),
        ("Smiles Peru", "IA-SMILES"),
        ("Dr. Aldo | Implantes Dentales y Rehabilitación Oral", "IA-ALDO"),
        ("Centro Odontológico Sonrisa Perfecta", "IA-SONRISA"),
        ("Clínica Dental", "IA-VISIBLE"),
        ("Estética Ñuñoa", "IA-NUNOA"),
    ],
)
def test_suggested_coupon(name, code):
    assert suggested_coupon(name) == code


def test_intake_has_an_ai_option():
    assert AI_OPTION in INTAKE_OPTIONS and "IA" in AI_OPTION


def test_panel_javascript_gives_the_same_links_and_coupons():
    playwright = pytest.importorskip("playwright.sync_api")
    with playwright.sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception as exc:
            pytest.skip(str(exc))
        page = browser.new_page()
        page.add_script_tag(content=JS.read_text(encoding="utf-8"))
        for website in WEBSITES:
            expected = [{"placement": k.placement, "url": k.url} for k in utm_links(website)]
            assert page.evaluate("w => utmLinks(w)", website) == expected, website
        for name in NAMES:
            assert page.evaluate("n => suggestedCoupon(n)", name) == suggested_coupon(name), name
        assert page.evaluate("INTAKE_OPTIONS") == list(INTAKE_OPTIONS)
        browser.close()


def test_kit_renders_the_three_tools():
    import re

    from visible_ia.atribucion import kit_context
    from visible_ia.informes.contexto import load_brand
    from visible_ia.informes.render import render_kit

    html = render_kit(
        kit_context("Smiles Peru", "smilesperu.com", load_brand(), "https://x.pe/panel/")
    )
    assert re.findall(r'data-seccion="([^"]+)"', html) == ["pregunta", "utm", "cupon"]
    assert "IA-SMILES" in html and "utm_source=doctoralia" in html
    assert "None" not in html and "{{" not in html
    without_web = render_kit(kit_context("Smiles Peru", None, load_brand(), "https://x.pe/"))
    assert "No tenemos registrada la dirección de tu web" in without_web
