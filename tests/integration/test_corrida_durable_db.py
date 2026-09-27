"""A run cut halfway keeps what it saved, seen from another connection (bug of 27/09).

The CLI used a non-autocommit connection: every answer was only a savepoint of one big
transaction, rolled back when the command ended with an error. This test uses real commits,
so it cleans up after itself instead of relying on the rolled-back `tx` fixture.
"""

import pytest

from visible_ia import db
from visible_ia.config import get_settings
from visible_ia.mercados.mercado import create_market
from visible_ia.mercados.plantillas import read_templates, upsert_templates
from visible_ia.motor.corrida import create_run, execute
from visible_ia.motor.modelos import EngineResponse

pytestmark = pytest.mark.integration

CATEGORY, DISTRICT = "MES", "San Isidro"  # not used by any other test


@pytest.fixture
def autocommit_conn(dev_conn):
    upsert_templates(dev_conn, read_templates())
    dev_conn.commit()
    conn = db.connect(get_settings(), "dev", autocommit=True)
    _cleanup(conn)
    yield conn
    _cleanup(conn)
    conn.close()


def _cleanup(conn):
    with conn.transaction(), conn.cursor() as cur:
        cur.execute(
            "delete from public.runs where market_id in (select id from public.markets "
            "where category_code = %s and district = %s)",
            (CATEGORY, DISTRICT),
        )
        cur.execute(
            "delete from public.markets where category_code = %s and district = %s",
            (CATEGORY, DISTRICT),
        )


def test_answers_saved_before_a_cut_survive_the_cut(autocommit_conn):
    market = create_market(autocommit_conn, CATEGORY, DISTRICT)
    run_id = create_run(
        autocommit_conn,
        market,
        surfaces=["chatgpt_api"],
        repetitions=1,
        estimated_cost_usd=0,
        forced=False,
    )
    calls = {"n": 0}

    def engine(question):
        calls["n"] += 1
        if calls["n"] == 4:
            raise KeyboardInterrupt
        return EngineResponse(surface="chatgpt_api", provider="fake", text="ok")

    with pytest.raises(KeyboardInterrupt):
        execute(autocommit_conn, run_id, {"chatgpt_api": engine}, concurrency=1)

    with db.connect(get_settings(), "dev") as other, other.cursor() as cur:
        cur.execute("select count(*) from public.responses where run_id = %s", (run_id,))
        (saved,) = cur.fetchone()
        cur.execute("select status from public.runs where id = %s", (run_id,))
        (status,) = cur.fetchone()
    assert saved >= 3
    assert status == "incomplete"
