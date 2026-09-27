import pytest

from visible_ia.mercados.mercado import MarketError, render_questions, validate_market


def test_render_questions_replaces_district():
    rendered = render_questions([("IMP-01", "¿Mejor clínica en {d}?")], "San Isidro")
    assert rendered == [("IMP-01", "¿Mejor clínica en San Isidro?")]


@pytest.mark.parametrize(
    ("category", "district", "message"),
    [
        ("IMP", "Barranco", "Distrito no válido"),
        ("XXX", "Miraflores", "Rubro no válido"),
        ("IMP", "miraflores", "Distrito no válido"),
    ],
)
def test_validate_market_rejects(category, district, message):
    with pytest.raises(MarketError, match=message):
        validate_market(category, district)


def test_validate_market_accepts_known_values():
    for district in ("Miraflores", "San Isidro", "Surco"):
        validate_market("DER", district)
