"""Traffic light, findings, question grid and the redesigned diagnostic PDF (28/09/2026)."""

import re
from datetime import date

import pytest

from visible_ia.informes.profundo import Answer, consistency, question_grid
from visible_ia.informes.semaforo import (
    Facts,
    Side,
    compared_level,
    findings,
    impact,
    lights,
    load_rules,
    one_in,
)

CUTS = load_rules()["corte"]


@pytest.mark.parametrize(
    "mine, leader, expected",
    [(40, 50, "Bien"), (60, 50, "Bien"), (39.9, 50, "Regular"), (20, 50, "Regular"),
     (19.9, 50, "Bajo"), (0, 50, "Bajo"), (10, 0, "Sin datos"), (0, 0, "Sin datos"),
     (None, 50, "Sin datos"), (10, None, "Sin datos")],
)  # fmt: skip
def test_level_is_the_clinics_figure_as_a_share_of_the_leaders(mine, leader, expected):
    assert CUTS == {"bien": 0.8, "regular": 0.4}
    assert compared_level(mine, leader, CUTS) == expected


def test_lights_have_the_four_areas_and_no_invented_colour():
    got = lights(Facts(total=0, me=Side(), ref=None, has_answers=False))
    assert [x.name for x in got] == [
        "Presencia en IA", "Tu web como fuente", "Doctoralia y directorios", "Reputación en Maps"
    ]  # fmt: skip
    assert {x.level for x in got} == {"Sin datos"}


def test_each_area_compares_with_the_leader():
    leader = Side(50, web=12, named=30, directories=15, rating=4.9, reviews=1135)
    # 25 of 50 = 50 % (Regular), web 10 of 12 = 83 % (Bien), directories 53 % of 50 % (Bien),
    # reviews 400 of 1135 = 35 % (Bajo).
    me = Side(25, web=10, named=15, directories=8, rating=4.8, reviews=400)
    got = {x.id: x for x in lights(Facts(60, me, leader))}
    assert {k: x.level for k, x in got.items()} == {
        "presencia": "Regular", "web": "Bien", "directorios": "Bien", "maps": "Bajo",
    }  # fmt: skip
    assert got["presencia"].value == "Te nombra en 25 % · el líder 50 %"
    assert got["maps"].value == "4,8 ★ y 400 reseñas · el líder 4,9 ★ y 1 135"
    # A leader at 0 cannot be compared with.
    zero = Side(50, web=0, named=30, directories=0, rating=4.9, reviews=1135)
    got = {x.id: x.level for x in lights(Facts(60, me, zero))}
    assert got["web"] == got["directorios"] == "Sin datos"


def test_impact_levels_and_consequence():
    assert [impact(n, 60) for n in (12, 10, 3, 2)] == ["alto", "alto", "medio", "bajo"]
    assert one_in(25) == "1 de cada 4 veces" and one_in(50) == "5 de cada 10 veces"


def test_findings_use_real_figures_and_are_three_at_most():
    got = findings(clinic="Tu Clínica", appearances=6, total=60, leader="Líder",
                   leader_appearances=30, is_leader=False, rating=4.9, reviews=1135,
                   web_answers=0, chatgpt=17, google=3)  # fmt: skip
    assert got == [
        "Tienes 4,9 ★ y 1 135 reseñas en Google Maps, pero la IA te nombra en 6 de 60 respuestas.",
        "Líder aparece en 30 de 60 respuestas; Tu Clínica, en 6.",
        "Tu web no apareció como fuente en ninguna respuesta.",
    ]


def test_summary_findings_plan_and_page_5_never_contradict_each_other():
    """The same numbers everywhere: the web cited 7 times must not produce "your web was not
    a source" in the plan (bug of 28/09/2026)."""
    from test_diagnostico_profundo import _answer

    from visible_ia.informes.contexto import build_context

    web = ("https://www.odontologists.com/implantes", "odontologists.com", "own_website")
    doc = ("https://www.doctoralia.pe/clinicas/x", "doctoralia.pe", "doctoralia")
    ig = ("https://www.instagram.com/smilesperu/", "instagram.com", "social")
    for n_web, with_doc in ((7, True), (0, False)):
        data = _deep_data()
        data.deep_answers = [
            _answer(10 + i, "Texto.", {1, 4} if i % 2 else {1}, question_id=1 + i % 10,
                    form="MRCP"[i % 4], surface="chatgpt_api" if i < 30 else "google_ai_mode",
                    urls=[*([web] if i < n_web else []), *([doc] if with_doc else []), ig])
            for i in range(60)
        ]  # fmt: skip
        ctx = build_context(data)
        new, deep = ctx["nuevo"], ctx["profundo"]
        # One count of "your web as a source" everywhere.
        assert new["web_respuestas"] == deep["webs"]["tuya"] == ctx["fuentes"]["web_tuya"] == n_web
        web_finding = next(h for h in new["hallazgos"] if h.startswith("Tu web"))
        assert (f"en {n_web} de 60" in web_finding) if n_web else ("ninguna" in web_finding)
        assert len(new["plan"]) == 3  # always the 3 of highest impact, even in "Bien" areas
        for r in new["plan"]:
            if r["id"] == "web":
                assert (f"en {n_web} de 60" in r["texto"]) if n_web else "en ninguna" in r["texto"]
        assert [r["respuestas"] for r in new["plan"]] == sorted(
            (r["respuestas"] for r in new["plan"]), reverse=True
        )
        # Other clinics' Instagram is a line apart, never a "missing page".
        assert all("instagram" not in p["url"] for p in deep["faltantes"])
        assert deep["instagram"] == {"otras": 60, "tuya": 0}


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
