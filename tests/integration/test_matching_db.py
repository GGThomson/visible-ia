from datetime import date

import pytest

from visible_ia.extractor.matching import load_market_clinics, match
from visible_ia.mercados.clinicas import ClinicRow, import_clinics
from visible_ia.mercados.mercado import create_market

pytestmark = pytest.mark.integration


def test_market_clinics_load_with_their_aliases_and_match(tx):
    market = create_market(tx, "DER", "Surco")
    rows = [
        ClinicRow(
            name="Implantes Dental | Perez Yance / Clínicas Dentales Americadent",
            district="Surco",
            maps_url="https://maps.google.com/?cid=test-match-0001",
        ),
        ClinicRow(
            name="Smiles Peru",
            district="Surco",
            maps_url="https://maps.google.com/?cid=test-match-0002",
        ),
    ]
    import_clinics(tx, market, rows, date(2026, 9, 26))

    clinics = load_market_clinics(tx, market)
    by_name = {c.name: c for c in clinics}
    assert set(
        by_name["Implantes Dental | Perez Yance / Clínicas Dentales Americadent"].aliases
    ) == {
        "Americadent",
        "Perez Yance",
    }
    assert by_name["Smiles Peru"].aliases == ()

    assert (
        match("Dental Pérez Yance", clinics).clinic_id
        == by_name["Implantes Dental | Perez Yance / Clínicas Dentales Americadent"].id
    )
    assert match("RenovaSmiles Perú", clinics).status == "new"
