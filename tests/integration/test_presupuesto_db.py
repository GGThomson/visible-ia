from datetime import UTC, datetime

import pytest

from visible_ia.mercados.mercado import create_market, list_questions
from visible_ia.motor.presupuesto import month_usage

pytestmark = pytest.mark.integration


def _response(cur, run_id, question_id, surface, rep, cost, created_at):
    cur.execute(
        "insert into public.responses (run_id, question_id, surface, repetition, cost_usd, "
        "created_at) values (%s, %s, %s, %s, %s, %s)",
        (run_id, question_id, surface, rep, cost, created_at),
    )


def test_month_usage_sums_only_the_lima_month(tx):
    market_id = create_market(tx, "DER", "Surco")
    q = list_questions(tx, market_id)[0].id
    with tx.cursor() as cur:
        cur.execute(
            "insert into public.runs (market_id, month, kind) values (%s, '2026-10-01', 'api') "
            "returning id",
            (market_id,),
        )
        (run_id,) = cur.fetchone()
        # Before Oct 1 in Lima (Sept 30, 23:00 local) -> previous month.
        _response(cur, run_id, q, "chatgpt_api", 1, 0.5, "2026-10-01 04:00+00")
        _response(cur, run_id, q, "google_ai_mode", 1, 0, "2026-10-01 04:00+00")
        # October in Lima.
        _response(cur, run_id, q, "chatgpt_api", 2, 0.03, "2026-10-01 06:00+00")
        _response(cur, run_id, q, "chatgpt_api", 3, 0.02, "2026-10-20 12:00+00")
        _response(cur, run_id, q, "google_ai_mode", 2, 0, "2026-10-20 12:00+00")
        # Extraction cost counts in the month it ran (October), whatever the answer's date.
        cur.execute(
            "update public.responses set extraction_cost_usd = 0.0002, "
            "extracted_at = '2026-10-22 12:00+00' where run_id = %s and repetition = 1",
            (run_id,),
        )

    now = datetime(2026, 10, 25, tzinfo=UTC)
    usage = month_usage(tx, now)
    assert usage.spent_usd == pytest.approx(0.05 + 2 * 0.0002)
    assert usage.serpapi_used == 1
    assert month_usage(tx, now, serpapi_account_used=9).serpapi_used == 9


def test_diagnostic_llm_costs_count_in_the_month(tx):
    from visible_ia.motor.presupuesto import record_llm_cost

    before = month_usage(tx).spent_usd
    record_llm_cost(tx, "diagnostic_reasons", model="gpt-5-nano", calls=70, cost_usd=0.015)
    assert month_usage(tx).spent_usd == pytest.approx(before + 0.015)
    with tx.cursor() as cur:  # a cost of another Lima month does not count
        cur.execute(
            "insert into public.llm_costs (kind, model, calls, cost_usd, created_at) "
            "values ('diagnostic_reasons', 'gpt-5-nano', 1, 0.5, '2026-10-01 04:00+00')"
        )
    oct_usage = month_usage(tx, datetime(2026, 10, 25, tzinfo=UTC)).spent_usd
    assert oct_usage < 0.5
