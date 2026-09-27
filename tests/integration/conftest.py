import pytest

from visible_ia import db
from visible_ia.config import get_settings


@pytest.fixture(scope="session")
def dev_conn():
    try:
        conn = db.connect(get_settings(), "dev")
    except db.MissingDatabaseUrl:
        pytest.skip("SUPABASE_DB_URL_DEV not configured")
    yield conn
    conn.close()


@pytest.fixture
def tx(dev_conn):
    """Everything inside is rolled back: no test data stays in dev. Templates are loaded first
    (idempotent) and DER markets are cleared inside the transaction so tests start clean."""
    from visible_ia.mercados.plantillas import read_templates, upsert_templates

    upsert_templates(dev_conn, read_templates())
    dev_conn.commit()
    with dev_conn.transaction(force_rollback=True):
        with dev_conn.cursor() as cur:
            # Runs (and their responses, by cascade) go first: dev keeps manual samples in
            # DER markets. The transaction is rolled back, so nothing is really deleted.
            cur.execute(
                "delete from public.runs where market_id in "
                "(select id from public.markets where category_code = 'DER')"
            )
            cur.execute("delete from public.markets where category_code = 'DER'")
        yield dev_conn
