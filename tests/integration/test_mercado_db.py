import pytest

from visible_ia.mercados.mercado import (
    MarketError,
    create_market,
    current_version,
    edit_question,
    list_questions,
)
from visible_ia.mercados.plantillas import read_templates, upsert_templates

pytestmark = pytest.mark.integration


@pytest.fixture
def tx(dev_conn):
    """Everything inside is rolled back: no test data stays in dev."""
    upsert_templates(dev_conn, read_templates())
    dev_conn.commit()
    with dev_conn.transaction(force_rollback=True):
        with dev_conn.cursor() as cur:
            cur.execute("delete from public.markets where category_code = 'DER'")
        yield dev_conn


def test_create_market_generates_10_questions(tx):
    market_id = create_market(tx, "DER", "Surco")
    questions = list_questions(tx, market_id)
    assert len(questions) == 10
    assert all("Surco" in q.text and "{d}" not in q.text for q in questions)
    assert {q.version for q in questions} == {1}


def test_duplicate_market_is_rejected(tx):
    create_market(tx, "DER", "Surco")
    with pytest.raises(MarketError, match="ya existe"):
        create_market(tx, "DER", "Surco")


def test_edit_without_runs_updates_in_place(tx):
    market_id = create_market(tx, "DER", "Surco")
    version = edit_question(tx, market_id, "DER-01", "¿Quién es el mejor dermatólogo en Surco?")
    assert version == 1 and current_version(tx, market_id) == 1
    texts = {q.template_id: q.text for q in list_questions(tx, market_id)}
    assert texts["DER-01"] == "¿Quién es el mejor dermatólogo en Surco?"


def test_edit_with_runs_creates_new_version_and_keeps_history(tx):
    market_id = create_market(tx, "DER", "Surco")
    with tx.cursor() as cur:
        cur.execute(
            "insert into public.runs (market_id, month, kind) values (%s, '2026-10-01', 'api')",
            (market_id,),
        )
    version = edit_question(tx, market_id, "DER-01", "Nueva pregunta en Surco")
    assert version == 2 and current_version(tx, market_id) == 2
    v1 = {q.template_id: q.text for q in list_questions(tx, market_id, 1)}
    v2 = {q.template_id: q.text for q in list_questions(tx, market_id, 2)}
    assert v1["DER-01"] != "Nueva pregunta en Surco"
    assert v2["DER-01"] == "Nueva pregunta en Surco"
    assert len(v2) == 10 and v1["DER-02"] == v2["DER-02"]
