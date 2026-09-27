import re
from pathlib import Path

import pytest

from visible_ia.mercados.plantillas import (
    CATEGORIES,
    InvalidTemplates,
    Template,
    read_templates,
    validate,
)

APPROVED_DOC = Path(__file__).parents[2] / "docs" / "03-especificacion" / "plantillas-preguntas.md"


def test_csv_has_40_valid_templates():
    templates = read_templates()
    assert len(templates) == 40
    for category in CATEGORIES:
        assert sum(t.category == category for t in templates) == 10
    assert all(t.text.count("{d}") == 1 for t in templates)


def test_csv_is_verbatim_copy_of_approved_document():
    doc = APPROVED_DOC.read_text(encoding="utf-8")
    approved = {
        m.group(1): m.group(2).strip()
        for m in re.finditer(r"^\| ((?:IMP|EDE|MES|DER)-\d\d) \| [MRCP] \| (.+?) \|", doc, re.M)
    }
    assert {t.id: t.text for t in read_templates()} == approved


def test_render_replaces_district():
    t = Template("IMP-01", "IMP", "M", "¿Cuál es la mejor clínica en {d}?", "Q01")
    assert t.render("San Isidro") == "¿Cuál es la mejor clínica en San Isidro?"


@pytest.mark.parametrize(
    ("bad", "message"),
    [
        (Template("IMP-01", "IMP", "X", "en {d}", "Q01"), "forma desconocida"),
        (Template("IMP-01", "IMP", "M", "sin distrito", "Q01"), "exactamente una vez"),
        (Template("IMP-01", "IMP", "M", "{d} y {d}", "Q01"), "exactamente una vez"),
        (Template("IMP-01", "ABC", "M", "en {d}", "Q01"), "rubro desconocido"),
        (Template("EDE-01", "IMP", "M", "en {d}", "Q01"), "no coincide con el rubro"),
    ],
)
def test_validate_rejects_bad_rows(bad, message):
    good = [t for t in read_templates() if t.id != bad.id]
    with pytest.raises(InvalidTemplates, match=message):
        validate([*good, bad])


def test_validate_rejects_wrong_count():
    with pytest.raises(InvalidTemplates, match="IMP: tiene 9"):
        validate([t for t in read_templates() if t.id != "IMP-10"])
