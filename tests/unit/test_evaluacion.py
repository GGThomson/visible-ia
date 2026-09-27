import json

import pytest

from visible_ia.extractor import evaluacion
from visible_ia.extractor.evaluacion import same_name, score


@pytest.mark.parametrize(
    "predicted, labelled, expected",
    [
        ("Dr. Aldo | Implantes Dentales y Rehabilitación Oral", "Dr. Aldo", True),
        ("Clinica Odontologists Miraflores", "Clínica Odontologists", True),
        ("Dental Pérez Yance", "Perez Yance", True),
        ("SMILES PERU", "Smiles Peru", True),
        ("Digital Smiles", "Smiles Peru", False),
        ("Odontonova", "Elyzea", False),
    ],
)
def test_same_name(predicted, labelled, expected):
    assert same_name(predicted, labelled) is expected


def _gold(estado="confirmada"):
    return [
        {
            "id": "corrida1-google_ai_mode-IMP-07-r2",
            "estado": estado,
            "texto": "Te recomiendo Smiles Peru y Dental Pérez Yance. Revisa Doctoralia.",
            "enlaces": [],
            "fuentes": ["https://www.doctoralia.pe/x?utm_source=a"],
            "menciones": [
                {"nombre": "Smiles Peru", "clinica": "Smiles Peru"},
                {"nombre": "Dental Pérez Yance", "clinica": "Dental Pérez Yance"},
            ],
            "dominios": ["doctoralia.pe"],
        }
    ]


def _cand(*names):
    return [
        {"nombre_tal_cual": n, "orden": i, "es_establecimiento_o_profesional": True}
        for i, n in enumerate(names, start=1)
    ]


def test_perfect_output_scores_100():
    s = score(
        _gold(), {"corrida1-google_ai_mode-IMP-07-r2": _cand("Smiles Peru", "Dental Pérez Yance")}
    )
    assert (s.precision, s.recall, s.association, s.domains) == (1, 1, 1, 1)
    assert s.failing() == {}


def test_missed_and_extra_names_lower_recall_and_precision():
    outputs = {"corrida1-google_ai_mode-IMP-07-r2": _cand("Smiles Peru", "Doctoralia", "Revisa")}
    s = score(_gold(), outputs)
    # Doctoralia is dropped by the validator; "Revisa" is literal but wrong.
    assert (s.true_positives, s.predicted) == (1, 2)
    assert (s.found, s.labelled) == (1, 2)
    assert s.association == 1.0  # the missed name only lowers recall
    assert set(s.failing()) == {"precision", "recall"}


def test_best_hit_prefers_the_identical_name():
    from visible_ia.extractor.evaluacion import best_hit

    assert best_hit(["Smiles Perú", "Digital Smiles"], "Digital Smiles") == "Digital Smiles"
    assert (
        best_hit(["Dr. Aldo | Implantes Dentales"], "Dr. Aldo") == "Dr. Aldo | Implantes Dentales"
    )
    assert best_hit(["Kagem"], "Odontonova") is None


def test_proposed_answers_are_skipped_unless_asked():
    outputs = {"corrida1-google_ai_mode-IMP-07-r2": _cand("Smiles Peru")}
    assert score(_gold("propuesta"), outputs).answers == 0
    assert score(_gold("propuesta"), outputs, include_proposed=True).answers == 1


def test_missing_output_is_reported():
    assert score(_gold(), {}).errors == ["sin salida grabada: corrida1-google_ai_mode-IMP-07-r2"]


def test_gold_file_is_well_formed():
    gold = evaluacion.read_jsonl(evaluacion.GOLD)
    assert len(gold) >= 60
    assert len({g["id"] for g in gold}) == len(gold)
    for g in gold:
        assert g["estado"] in ("propuesta", "confirmada")
        text = (g["texto"] + " " + " ".join(g["enlaces"])).lower()
        for m in g["menciones"]:
            assert m["nombre"].lower() in text, (g["id"], m["nombre"])
    clinics = {
        c["nombre"]
        for c in json.loads(evaluacion.CLINIC_LISTS["corrida1-"].read_text(encoding="utf-8"))[
            "clinicas"
        ]
    }
    for g in gold:
        for m in g["menciones"]:
            assert m["clinica"] is None or m["clinica"] in clinics, (g["id"], m)
