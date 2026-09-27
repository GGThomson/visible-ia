from datetime import date

import pytest

from visible_ia.mercados.alias import AliasError, add_alias, list_aliases, remove_alias
from visible_ia.mercados.clinicas import ClinicRow, import_clinics, list_market_clinics
from visible_ia.mercados.mercado import create_market

pytestmark = pytest.mark.integration

ROW = ClinicRow(
    name="Implantes Dental | Perez Yance / Clínicas Dentales Americadent",
    district="Surco",
    maps_url="https://maps.google.com/?cid=test-alias-0001",
)


def test_import_adds_derived_aliases_and_manual_ones_work(tx):
    market = create_market(tx, "DER", "Surco")
    import_clinics(tx, market, [ROW], date(2026, 9, 26))
    clinic_id = list_market_clinics(tx, market)[0][0]
    assert list_aliases(tx, clinic_id) == ["Americadent", "Perez Yance"]

    assert add_alias(tx, clinic_id, "Dr. Pérez Yance") is True
    assert add_alias(tx, clinic_id, "AMERICADENT") is False  # case-insensitive duplicate
    assert remove_alias(tx, clinic_id, "americadent") is True
    assert list_aliases(tx, clinic_id) == ["Dr. Pérez Yance", "Perez Yance"]


def test_alias_for_unknown_clinic_fails(tx):
    with pytest.raises(AliasError, match="No existe la clínica"):
        add_alias(tx, -1, "Algo")
