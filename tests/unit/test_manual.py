import csv

import pytest

from visible_ia.mercados.plantillas import read_templates
from visible_ia.motor.manual import (
    PHASE1_QUESTIONS_CSV,
    SURFACE_BY_AI,
    parse_sources,
)
from visible_ia.motor.modelos import MANUAL_SURFACES


def test_parse_sources_finds_urls_in_free_text():
    value = "https://a.pe/x?utm_source=chatgpt.com https://b.com/y, (https://c.org/z)."
    assert parse_sources(value) == [
        "https://a.pe/x?utm_source=chatgpt.com",
        "https://b.com/y",
        "https://c.org/z",
    ]
    assert parse_sources("") == []


def test_every_ai_maps_to_a_manual_surface():
    assert set(SURFACE_BY_AI.values()) <= set(MANUAL_SURFACES)


def test_phase1_questions_match_the_template_origins():
    """Each phase-1 question points to the template that was built from it."""
    templates = {t.id: t for t in read_templates()}
    with PHASE1_QUESTIONS_CSV.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 10
    for row in rows:
        template = templates[row["plantilla"]]
        assert template.origin.startswith(row["pregunta_id"])
        if row["mercado_original"] == "Lima":
            assert row["distrito"] == "Miraflores" and "Lima" in row["texto_original"]
        else:
            assert template.render(row["distrito"]) == row["texto_original"]


@pytest.mark.parametrize("qid", ["Q05", "Q19"])
def test_lima_questions_are_marked(qid):
    with PHASE1_QUESTIONS_CSV.open(encoding="utf-8-sig", newline="") as f:
        row = next(r for r in csv.DictReader(f) if r["pregunta_id"] == qid)
    assert row["mercado_original"] == "Lima"


def test_split_pasted_separates_answer_sources_and_comments():
    from visible_ia.motor.manual import split_pasted

    text = (
        "Te recomiendo la Clínica X.\n"
        "Fuente: https://x.pe/?utm_source=gemini\n"
        "\n"
        "También la Clínica Y.\n"
        "# Pega arriba la respuesta\n"
        "fuente: https://y.pe\n"
    )
    body, urls = split_pasted(text)
    assert body == "Te recomiendo la Clínica X.\n\nTambién la Clínica Y."
    assert urls == ["https://x.pe/?utm_source=gemini", "https://y.pe"]
