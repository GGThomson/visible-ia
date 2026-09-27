import pytest

from visible_ia.mercados.plantillas import read_templates, upsert_templates

pytestmark = pytest.mark.integration


def test_loading_twice_does_not_duplicate(dev_conn):
    templates = read_templates()
    upsert_templates(dev_conn, templates)
    upsert_templates(dev_conn, templates)
    with dev_conn.cursor() as cur:
        cur.execute("select category_code, count(*) from public.templates group by 1 order by 1")
        assert cur.fetchall() == [("DER", 10), ("EDE", 10), ("IMP", 10), ("MES", 10)]
