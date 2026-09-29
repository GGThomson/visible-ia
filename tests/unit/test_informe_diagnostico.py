import re
from datetime import date

import pytest

from visible_ia.informes.contexto import (
    ClinicInfo,
    ExampleAnswer,
    ReportData,
    build_context,
    mask_professionals,
    pick_competitors,
)
from visible_ia.informes.render import STYLES, render_diagnostic
from visible_ia.puntaje.indice import RankingRow, ScoreError

SMILES, PEREZ, ALDO, ODONTO, CANO = 1, 2, 3, 4, 5


def _row(cid, name, combined, chatgpt, google):
    return RankingRow(cid, name, combined, combined - 12, combined + 12, chatgpt, google, 2.0, 5.0)


RANKING = [
    _row(SMILES, "Smiles Peru", 50, 56.7, 43.3),
    _row(PEREZ, "Dental Pérez Yance", 36.7, 10, 63.3),
    _row(ALDO, "Dr. Aldo | Implantes Dentales y Rehabilitación Oral", 30, 6.7, 53.3),
    _row(CANO, "Clínica Dental Cano", 16.7, 30, 3.3),
    _row(ODONTO, "Clínica Odontologists", 10, 16.7, 3.3),
]


def _data(**overrides):
    base = dict(
        clinic=ClinicInfo(
            ODONTO,
            "Clínica Odontologists",
            4.9,
            1135,
            date(2026, 9, 27),
            "https://odontologists.com/",
        ),
        category="IMP",
        district="Miraflores",
        month=date(2026, 9, 1),
        ranking=RANKING,
        examples=[
            ExampleAnswer(
                "chatgpt_api",
                "¿Cuál es la mejor clínica de implantes dentales en Miraflores?",
                date(2026, 9, 26),
                "Te recomiendo Clínica Odontologists, con más de 1,000 reseñas. "
                "También Smiles Peru. "
                "Atiende la Dra. María Pérez Gómez, especialista en implantes.",
                [(1, "Clínica Odontologists", ODONTO), (2, "Smiles Peru", SMILES)],
            ),
            ExampleAnswer(
                "google_ai_mode",
                "¿Qué implantólogo tiene buenas reseñas en Miraflores?",
                date(2026, 9, 26),
                "Destaca Dental Pérez Yance y el Dr. Aldo Moreno en Dr. Aldo Implants.",
                [(1, "Dental Pérez Yance", PEREZ), (2, "Dr. Aldo Moreno", ALDO)],
            ),
        ],
        citations=[
            (1, "chatgpt_api", "smilesperu.com", "own_website"),
            (1, "chatgpt_api", "doctoralia.pe", "doctoralia"),
            (2, "google_ai_mode", "google.com", "google_profile"),
            (2, "google_ai_mode", "limadentalrating.com", "directory"),
        ],
        total_answers=60,
        detectable_diff=10.7,
        google_without_names=3,
        market_names={
            SMILES: ["Smiles Peru"],
            PEREZ: ["Dental Pérez Yance", "Perez Yance"],
            ALDO: [
                "Dr. Aldo | Implantes Dentales y Rehabilitación Oral",
                "Dr. Aldo Moreno",
                "Dr. Aldo",
            ],
            CANO: ["Clínica Dental Cano"],
            ODONTO: ["Clínica Odontologists", "Odontologists"],
        },
    )
    base.update(overrides)
    return ReportData(**base)


def test_report_has_the_six_parts_and_no_blank_values():
    html = render_diagnostic(build_context(_data()))
    sections = re.findall(r'data-seccion="([^"]+)"', html)
    # Without stored answers (no C-008 data) the question grid is left out.
    assert sections == ["resumen", "competencia", "razones", "faltantes", "plan", "metodo"]
    assert "None" not in html and "{{" not in html
    assert "No garantizamos un puesto #1" in html
    assert "entre 0 % y" not in html  # margins come from the data, never defaulted


def test_competitors_are_the_top_3_other_clinics_by_default():
    assert [r.clinic_id for r in pick_competitors(RANKING, ODONTO, None)] == [SMILES, PEREZ, ALDO]
    assert [r.clinic_id for r in pick_competitors(RANKING, SMILES, None)] == [PEREZ, ALDO, CANO]
    assert [r.clinic_id for r in pick_competitors(RANKING, ODONTO, [CANO])] == [CANO]
    with pytest.raises(ScoreError):
        pick_competitors(RANKING, ODONTO, [99])


def test_simple_sentence_and_ranges():
    ctx = build_context(_data())
    assert ctx["frase"].startswith("La IA nombró a Clínica Odontologists en 6 de 60 respuestas")
    assert "Smiles Peru, la más recomendada, aparece en 50 %" in ctx["frase"]
    assert [r["nombre"] for r in ctx["ranking"]][0] == "Smiles Peru"
    assert ctx["clinica"]["posicion"] == 5


def test_professionals_are_masked_unless_they_are_the_establishment():
    allowed = [
        "Dr. Aldo | Implantes Dentales y Rehabilitación Oral",
        "Dr. Aldo Moreno",
        "Clínica Odontologists",
    ]
    text = "Atiende la Dra. María Pérez Gómez. También el Dr. Aldo Moreno."
    assert (
        mask_professionals(text, allowed) == "Atiende la [profesional]. También el Dr. Aldo Moreno."
    )
    html = render_diagnostic(build_context(_data()))
    assert "María Pérez" not in html
    assert "[profesional]" in html


def test_examples_list_names_in_order_with_the_client_marked():
    ctx = build_context(_data())
    chatgpt = ctx["ejemplos"][0]
    assert chatgpt["superficie"] == "ChatGPT"
    assert [n["nombre"] for n in chatgpt["nombres"]] == ["Clínica Odontologists", "Smiles Peru"]
    assert chatgpt["nombres"][0]["es_cliente"] is True
    google = ctx["ejemplos"][1]
    assert [n["nombre"] for n in google["nombres"]][
        1
    ] == "Dr. Aldo | Implantes Dentales y Rehabilitación Oral"


def test_gap_and_recommendations():
    ctx = build_context(_data())
    assert ctx["brecha"]["tiene_brecha"] is True
    titles = [r["titulo"] for r in ctx["recomendaciones"]]
    assert len(titles) == 3
    assert titles[0].startswith("Convierte tu reputación en Maps")  # biggest gap: 24 of 60
    assert any(t.startswith("Una página clara de implantes dentales") for t in titles)
    gaps = [r["respuestas"] for r in ctx["recomendaciones"]]
    assert gaps == sorted(gaps, reverse=True)


def test_leader_gets_a_leader_sentence_and_keep_advice():
    data = _data(
        clinic=ClinicInfo(
            SMILES, "Smiles Peru", 4.7, 355, date(2026, 9, 27), "https://smilesperu.com/"
        )
    )
    ctx = build_context(data)
    assert "es la clínica más recomendada" in ctx["frase"]
    assert any(r["titulo"] == "Mantén y amplía tu ventaja" for r in ctx["recomendaciones"])
    assert ctx["fuentes"]["propia_citada"] is True


def test_brand_comes_from_variables():
    brand = {
        "nombre": "Agencia X",
        "lema": "l",
        "color_primario": "#111111",
        "color_acento": "#222222",
        "color_suave": "#333333",
        "logo_url": "https://x.pe/logo.png",
        "contacto": "c",
        "web": "w",
    }
    html = render_diagnostic(build_context(_data(), brand))
    assert "--primario: #111111" in html and "Agencia X" in html and "visible-ia" not in html
    from visible_ia.informes.render import diagnostic_frame

    header, footer = diagnostic_frame(build_context(_data(), brand))
    assert 'src="https://x.pe/logo.png"' in header and "Agencia X" in footer
    assert 'class="pageNumber"' in footer and 'class="totalPages"' in footer


def test_text_is_at_least_11pt():
    sizes = [
        float(v) for v in re.findall(r"font-size:\s*([\d.]+)pt", STYLES.read_text(encoding="utf-8"))
    ]
    assert sizes and min(sizes) >= 11


def test_quotes_are_plain_text():
    from visible_ia.informes.contexto import plain_text

    text = (
        "- **Clínica Odontologists** — muchas reseñas. "
        "([limadentalrating.com](https://limadentalrating.com/es/?utm_source=openai))\n"
        "## Consejos\nRevisa [su web](https://x.pe) antes. https://y.pe/z"
    )
    assert (
        plain_text(text) == "Clínica Odontologists — muchas reseñas. Consejos Revisa su web antes."
    )


def test_footer_hides_an_empty_contact():
    from visible_ia.informes.contexto import load_brand

    brand = load_brand()
    html = render_diagnostic(build_context(_data(), {**brand, "contacto": ""}))
    proximo = html.split('class="proximo"')[1].split("</div>")[0]
    assert "15 minutos." in proximo and " · ." not in proximo


def test_default_brand_is_eminia_with_the_embedded_logo():
    import base64
    from pathlib import Path

    from visible_ia.informes.contexto import load_brand

    brand = load_brand()
    logo = Path(__file__).resolve().parents[2] / "web" / "marca" / "logo.svg"
    assert brand["nombre"] == "Eminia"
    prefix = "data:image/svg+xml;base64,"
    assert brand["logo_url"].startswith(prefix)
    embedded = base64.b64decode(brand["logo_url"][len(prefix) :])
    # Git may turn the file into CRLF on Windows: compare the content, not the line endings.
    assert embedded.replace(b"\r\n", b"\n") == logo.read_bytes().replace(b"\r\n", b"\n")
