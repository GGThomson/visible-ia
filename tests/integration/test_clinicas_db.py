from datetime import date
from pathlib import Path

import pytest

from visible_ia.mercados.clinicas import import_clinics, list_market_clinics, read_clinics_csv
from visible_ia.mercados.mercado import create_market

pytestmark = pytest.mark.integration

EXAMPLE = Path(__file__).parents[2] / "data" / "ejemplos" / "clinicas-ejemplo.csv"


def test_import_creates_then_updates_and_links(tx):
    surco = create_market(tx, "DER", "Surco")
    rows, _ = read_clinics_csv(EXAMPLE)
    assert import_clinics(tx, surco, rows, date(2026, 9, 26)) == (5, 0)
    assert import_clinics(tx, surco, rows, date(2026, 9, 27)) == (0, 5)
    listed = list_market_clinics(tx, surco)
    assert len(listed) == 5
    assert {row[4] for row in listed} == {date(2026, 9, 27)}  # data_date refreshed


def test_same_clinic_can_belong_to_two_markets(tx):
    surco = create_market(tx, "DER", "Surco")
    miraflores = create_market(tx, "DER", "Miraflores")
    rows, _ = read_clinics_csv(EXAMPLE)
    import_clinics(tx, surco, rows[:1], date(2026, 9, 26))
    import_clinics(tx, miraflores, rows[:1], date(2026, 9, 26))
    assert list_market_clinics(tx, surco)[0][0] == list_market_clinics(tx, miraflores)[0][0]
