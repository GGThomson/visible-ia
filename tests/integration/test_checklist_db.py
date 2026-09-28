from datetime import date

import pytest

from visible_ia.checklist import generate
from visible_ia.clientes import add_site, create_client
from visible_ia.mercados.clinicas import ClinicRow, import_clinics, list_market_clinics
from visible_ia.mercados.mercado import create_market

pytestmark = pytest.mark.integration


def test_checklist_is_generated_refreshed_and_keeps_done_tasks(tx):
    market = create_market(tx, "DER", "Surco")
    import_clinics(
        tx,
        market,
        [ClinicRow(name="Clínica Check", district="Surco",
                   maps_url="https://maps.google.com/?cid=t-check", rating=4.2, review_count=12)],
        date(2026, 9, 27),
    )  # fmt: skip
    clinic = list_market_clinics(tx, market)[0][0]
    site, _ = add_site(tx, create_client(tx, "clinic", "Cliente Check"), clinic, market)

    first = generate(tx, site)
    assert [t.code for t in first] == [
        "ficha_google",
        "resenas",
        "web_schema",
        "redes",
        "bing_places",
    ]
    with tx.cursor() as cur:
        cur.execute(
            "update public.tasks set status = 'done' where site_id = %s and code = 'redes'", (site,)
        )
        # The clinic now has Instagram and many reviews: those tasks no longer apply.
        cur.execute(
            "update public.clinics set instagram = '@check', review_count = 300 where id = %s",
            (clinic,),
        )
    second = generate(tx, site)
    assert "resenas" not in [t.code for t in second]
    with tx.cursor() as cur:
        cur.execute(
            "select code, status, priority, title from public.tasks "
            "where site_id = %s order by priority",
            (site,),
        )
        rows = cur.fetchall()
    codes = [r[0] for r in rows]
    assert "resenas" not in codes  # pending and no longer applicable: removed
    assert ("redes", "done") in [(r[0], r[1]) for r in rows]  # done: kept
    assert rows[0][0] == "ficha_google" and rows[0][3] == "Completa tu ficha de Google"
