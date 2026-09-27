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
