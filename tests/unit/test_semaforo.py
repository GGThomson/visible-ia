"""Traffic light, findings, question grid and the redesigned diagnostic PDF (28/09/2026)."""

import re
from datetime import date

import pytest

from visible_ia.informes.profundo import Answer, consistency, question_grid
from visible_ia.informes.semaforo import (
    Facts,
    Side,
    allowed,
    findings,
    impact,
    level,
    lights,
    load_rules,
    maps_level,
    one_in,
)

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
    got = lights(Facts(total=0, me=Side(), ref=None, has_answers=False))
    assert [x.name for x in got] == [
        "Presencia en IA", "Tu web como fuente", "Doctoralia y directorios", "Reputación en Maps"
    ]  # fmt: skip
    assert {x.level for x in got} == {"Sin datos"}


def test_bien_only_when_the_range_reaches_the_leaders():
    leader = Side(50, 38, 62, web=12, named=30, directories=15, rating=4.9, reviews=1135)
    close = Side(25, 38, 45, web=10, named=15, directories=8, rating=4.8, reviews=600)
    far = Side(12, 6, 22, web=0, named=7, directories=0, rating=4.9, reviews=120)
    got = {x.id: x for x in lights(Facts(60, close, leader))}
    assert got["presencia"].level == "Bien"
    assert got["presencia"].value == "Te nombra en 25 % · el líder 50 %"
    assert got["maps"].value == "4,8 ★ y 600 reseñas · el líder 4,9 ★ y 1 135"
    assert {x.id: x.level for x in lights(Facts(60, far, leader))} == {
        "presencia": "Regular", "web": "Bajo", "directorios": "Bajo", "maps": "Regular",
    }  # fmt: skip


def test_impact_comes_from_the_gap_and_fixes_skip_areas_already_good():
    assert [impact(n, 60) for n in (12, 10, 3, 2)] == ["alto", "alto", "medio", "bajo"]
    assert not allowed("doctoralia", {"directorios": "Bien"})
    assert allowed("mantener", {"presencia": "Bien"})
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
    """The same numbers everywhere: the web cited 7 times and Doctoralia "Bien" must not
    produce "your web was not a source" or "complete Doctoralia" (bug of 28/09/2026)."""
    from test_diagnostico_profundo import _answer

    from visible_ia.informes.contexto import build_context
    from visible_ia.informes.semaforo import allowed as fix_allowed

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
        by_area = {
            "Presencia en IA": "presencia",
            "Tu web como fuente": "web",
            "Doctoralia y directorios": "directorios",
            "Reputación en Maps": "maps",
        }
        levels = {by_area[s["nombre"]]: s["nivel"] for s in new["semaforo"]}
        # One count of "your web as a source" everywhere.
        assert new["web_respuestas"] == deep["webs"]["tuya"] == ctx["fuentes"]["web_tuya"] == n_web
        web_finding = next(h for h in new["hallazgos"] if h.startswith("Tu web"))
        assert (f"en {n_web} de 60" in web_finding) if n_web else ("ninguna" in web_finding)
        for r in new["plan"]:
            assert fix_allowed(r["id"], levels), (r["id"], levels)  # never fix what is "Bien"
            if r["id"] == "web":
                assert (f"en {n_web} de 60" in r["texto"]) if n_web else "en ninguna" in r["texto"]
        if levels["directorios"] == "Bien":
            assert "doctoralia" not in [r["id"] for r in new["plan"]]
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
