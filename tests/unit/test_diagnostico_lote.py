"""Batch of free diagnostics (C-010): list, name matching and the first WhatsApp message."""

import re
from dataclasses import replace
from pathlib import Path

import pytest
from test_informe_diagnostico import ODONTO, RANKING, SMILES, _data

from visible_ia.informes import lote
from visible_ia.informes.contexto import ClinicInfo, load_brand
from visible_ia.informes.lote import (
    UnknownName,
    match,
    read_list,
    standing,
    strongest_fact,
    whatsapp_message,
)
from visible_ia.nicho import load_niche

NAMES = {
    1: ["Smiles Peru"],
    5: ["Clínica Dental Cano"],
    6: ["The Dental Clinic & GT Concept"],
    29: ["Centro Odontológico NEODENTIS", "Neodentis"],
    30: ["Clínica Virtual Dent"],
    31: ["Clínica Dental Canoa"],
}


def test_list_skips_blank_lines_and_comments():
    assert read_list("NEODENTIS\n\n# prueba\n  Virtual Dent  \n30\n") == [
        "NEODENTIS", "Virtual Dent", "30"
    ]  # fmt: skip


@pytest.mark.parametrize(
    "line, expected",
    [("NEODENTIS", 29), ("neodentis", 29), ("Virtual Dent", 30), ("Dental Cano", 5),
     ("The Dental Clinic", 6), ("30", 30), ("clinica dental cano", 5)],
)  # fmt: skip
def test_names_match_by_id_exact_name_or_whole_words(line, expected):
    assert match(line, NAMES) == expected


@pytest.mark.parametrize("line", ["Sonrisa", "99", "Dental"])
def test_unknown_or_ambiguous_names_are_reported(line):
    with pytest.raises(UnknownName):
        match(line, NAMES)


def test_reputation_the_ai_ignores_is_the_strongest_fact():
    kind, fact = strongest_fact(standing(_data()))  # 4.9 ★, 1135 reviews, 6 of 60
    assert kind == "reputacion"
    assert fact == (
        "Clínica Odontologists tiene 4,9 estrellas y 1 135 reseñas en Google Maps, "
        "pero solo apareció en 6 de las 60 respuestas."
    )


def test_one_assistant_much_stronger_than_the_other():
    rows = [replace(r, chatgpt=30.0, google=3.3) if r.clinic_id == ODONTO else r for r in RANKING]
    data = _data(ranking=rows)
    data.clinic = replace(data.clinic, reviews=40)  # no reputation gap
    kind, fact = strongest_fact(standing(data))
    assert kind == "asistente"
    assert fact == (
        "Clínica Odontologists apareció en 9 de 30 respuestas de ChatGPT, pero solo en 1 de las 30 "
        "de Google."
    )


def test_otherwise_the_comparison_with_the_leader():
    data = _data(clinic=ClinicInfo(SMILES, "Smiles Peru", 4.7, 355, None, None))
    kind, fact = strongest_fact(standing(data))
    assert kind == "lider"
    assert fact.startswith("Smiles Peru encabeza la lista: apareció en 30 de las 60 respuestas")


def test_message_is_short_plain_and_signed_by_the_brand():
    text = whatsapp_message(_data(), load_niche(), load_brand())
    assert text.startswith(f"Hola, soy {load_brand()['firma']}.")
    assert "implantes dentales en Miraflores, como lo haría un paciente" in text
    assert text.endswith("¿Te lo envío por aquí?")
    assert len(text) <= 450
    jargon = ("índice", "rango", "fuente", "mención", "semáforo", "%", "puntaje", "eminia ")
    assert not any(w in text.lower() for w in jargon), text


def test_new_code_takes_the_niche_words_from_the_configuration():
    niche = load_niche()
    words = [niche.business, niche.businesses, niche.customer, niche.customers]
    for path in (Path(lote.__file__), Path(lote.__file__).parents[1] / "nicho.py"):
        # Comments (whole-line or trailing) and docstrings may name the niche; the code may not.
        lines = path.read_text(encoding="utf-8").splitlines()
        code = "\n".join(re.sub(r"#.*", "", line) for line in lines)
        code = re.sub(r'""".*?"""', "", code, flags=re.S)
        for word in words:
            assert not re.search(rf"\b{word}\b", code, re.I), (path.name, word)
