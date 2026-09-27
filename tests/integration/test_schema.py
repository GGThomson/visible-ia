import pytest

from visible_ia.db import pending_migrations

pytestmark = pytest.mark.integration


def test_no_pending_migrations_in_dev(dev_conn):
    assert pending_migrations(dev_conn) == []


def test_all_public_tables_have_rls(dev_conn):
    with dev_conn.cursor() as cur:
        cur.execute(
            "select tablename from pg_tables where schemaname = 'public' and not rowsecurity"
        )
        assert cur.fetchall() == []


def test_purge_after_defaults_to_one_year(dev_conn):
    with dev_conn.cursor() as cur:
        cur.execute(
            "select column_default from information_schema.columns "
            "where table_schema = 'public' and table_name = 'responses' "
            "and column_name = 'purge_after'"
        )
        (default,) = cur.fetchone()
        # Evaluate the stored expression instead of matching text (Postgres normalizes it).
        cur.execute(
            f"select ({default}) = "
            "(((now() at time zone 'America/Lima')::date + interval '1 year')::date)"
        )
        assert cur.fetchone()[0] is True


def test_categories_seeded(dev_conn):
    with dev_conn.cursor() as cur:
        cur.execute("select code from public.categories order by code")
        assert [r[0] for r in cur.fetchall()] == ["DER", "EDE", "IMP", "MES"]
