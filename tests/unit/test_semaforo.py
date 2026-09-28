"""Traffic light, findings, question grid and the redesigned diagnostic PDF (28/09/2026)."""

import re
from datetime import date

import pytest

from visible_ia.informes.profundo import Answer, consistency, question_grid
from visible_ia.informes.semaforo import findings, impact, level, lights, load_rules, maps_level

RULES = load_rules()


@pytest.mark.parametrize(
    "value, expected",
    [(25, "Bien"), (24.9, "Regular"), (10, "Regular"), (9.9, "Bajo"), (0, "Bajo"),
     (None, "Sin datos")],
)  # fmt: skip
def test_presence_thresholds(value, expected):
    rule = RULES["presencia"]
    assert level(value, rule["bien"], rule["regular"]) == expected


@pytest.mark.parametrize(
    "area, good, fair, low",
    [("web", 15, 1, 0), ("directorios", 40, 15, 14.9)],
)
def test_share_thresholds(area, good, fair, low):
    rule = RULES[area]
    assert [level(v, rule["bien"], rule["regular"]) for v in (good, fair, low)] == [
        "Bien", "Regular", "Bajo"
    ]  # fmt: skip


@pytest.mark.parametrize(
    "rating, reviews, expected",
    [(4.7, 200, "Bien"), (4.9, 199, "Regular"), (4.3, 50, "Regular"), (4.2, 5000, "Bajo"),
     (4.9, 49, "Bajo"), (None, 300, "Sin datos"), (4.8, None, "Sin datos")],
)  # fmt: skip
def test_maps_needs_both_stars_and_reviews(rating, reviews, expected):
    assert maps_level(rating, reviews, RULES["maps"]) == expected


def test_lights_have_the_four_areas_and_no_invented_colour():
    got = lights(None, None, None, None, None)
    assert [x.name for x in got] == [
        "Presencia en IA", "Tu web como fuente", "Doctoralia y directorios", "Reputación en Maps"
    ]  # fmt: skip
    assert {x.level for x in got} == {"Sin datos"}


def test_impact_is_high_only_when_a_related_area_is_low():
    assert impact("web", {"web": "Bajo"}) == "alto"
    assert impact("web", {"web": "Regular", "maps": "Bajo"}) == "medio"


def test_findings_use_real_figures_and_are_three_at_most():
    got = findings(clinic="Tu Clínica", appearances=6, total=60, leader="Líder",
                   leader_appearances=30, is_leader=False, rating=4.9, reviews=1135,
                   web_answers=0, chatgpt=17, google=3)  # fmt: skip
    assert got == [
        "Tienes 4.9 ★ y 1,135 reseñas en Google Maps, pero la IA te nombra en 6 de 60 respuestas.",
        "Líder aparece en 30 de 60 respuestas; Tu Clínica, en 6.",
        "Tu web no apareció como fuente en ninguna respuesta.",
    ]


def _a(rid, qid, form, surface, clinics):
    return Answer(rid, surface, qid, f"P{qid}", form, date(2026, 9, 1), "", frozenset(clinics))


def test_grid_has_one_dot_per_answer_chatgpt_first():
    answers = [
        _a(4, 1, "M", "google_ai_mode", {1}),
        _a(1, 1, "M", "chatgpt_api", {1, 2}),
        _a(2, 1, "M", "chatgpt_api", {2}),
        _a(3, 2, "P", "chatgpt_api", set()),
    ]
    groups = question_grid(answers, [1, 2])
    assert [g["forma"] for g in groups] == ["Mejor", "Procedimiento"]
    assert groups[0]["preguntas"][0]["celdas"] == [[True, False, True], [True, True, False]]


def test_consistency_counts_questions_by_repetitions():
    answers = [_a(i, 1, "M", "chatgpt_api", {1}) for i in range(3)]  # named 3 of 3
    answers += [_a(10 + i, 2, "M", "chatgpt_api", {1} if i == 0 else set()) for i in range(3)]
    answers += [_a(20 + i, 3, "M", "chatgpt_api", set()) for i in range(3)]
    [row] = consistency(answers, 1)
    assert (row["todas"], row["algunas"], row["ninguna"], row["repeticiones"]) == (1, 1, 1, 3)


def _deep_data():
    from test_diagnostico_profundo import _answer
    from test_informe_diagnostico import _data

    data = _data()
    data.deep_answers = [
        _answer(10 + i, "Smiles Peru destaca por sus reseñas y su trato en Miraflores.",
                {1, 4} if i % 2 else {1}, question_id=1 + i % 10, form="MRCP"[i % 4],
                surface="chatgpt_api" if i < 30 else "google_ai_mode")
        for i in range(60)
    ]  # fmt: skip
    return data


def test_redesigned_report_has_every_section_and_no_blank_values():
    from visible_ia.informes.contexto import build_context
    from visible_ia.informes.render import render_diagnostic

    html = render_diagnostic(build_context(_deep_data()))
    assert re.findall(r'data-seccion="([^"]+)"', html) == [
        "resumen", "competencia", "preguntas", "razones", "faltantes", "plan", "metodo"
    ]  # fmt: skip
    assert "None" not in html and "{{" not in html and "nan" not in html.lower().split()
    assert "No garantizamos un puesto #1" in html and "criterio Eminia" in html
    assert html.count('class="luz ') == 4 and html.count('class="proximo"') == 2


def test_pdf_has_no_empty_page(tmp_path):
    """Render the PDF (with its header and footer) and check every page has real content."""
    from pypdf import PdfReader

    from visible_ia.informes.contexto import build_context
    from visible_ia.informes.pdf import PdfError, html_to_pdf
    from visible_ia.informes.render import diagnostic_frame, render_diagnostic

    context = build_context(_deep_data())
    path = tmp_path / "d.pdf"
    try:
        html_to_pdf(render_diagnostic(context), path, *diagnostic_frame(context))
    except PdfError as exc:  # no Chromium here (e.g. the CI)
        pytest.skip(str(exc))
    pages = [p.extract_text() or "" for p in PdfReader(path).pages]
    # Header and footer alone are ~90 characters: a page with only them would be "empty".
    assert all(len(text) > 200 for text in pages), [len(t) for t in pages]
    assert 4 <= len(pages) <= 8
    assert all(f"Página {i} de {len(pages)}" in text for i, text in enumerate(pages, start=1))
