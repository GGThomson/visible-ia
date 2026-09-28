"""Monthly run with fake engines and extractor in dev (no API cost)."""

from datetime import UTC, datetime

import pytest

from visible_ia.extractor import llm
from visible_ia.mercados.mercado import create_market
from visible_ia.motor.mensual import plan_month, run_month
from visible_ia.motor.modelos import EngineResponse
from visible_ia.motor.presupuesto import MonthUsage

pytestmark = pytest.mark.integration
NOW = datetime(2026, 10, 1, 12, tzinfo=UTC)


def _only_my_market(tx, market):
    with tx.cursor() as cur:
        cur.execute("update public.markets set active = (id = %s)", (market,))  # rolled back


def _engine(surface, fail_on=()):
    calls = {"n": 0}

    def ask(question):
        calls["n"] += 1
        if calls["n"] in fail_on:
            raise RuntimeError("falla simulada")
        return EngineResponse(surface=surface, provider="fake", text="Te recomiendo Clínica X.")

    return ask


def _extractor(text, links):
    return llm.Extraction([llm.Mention("Clínica X", 1)], extractor_version="fake")


def test_month_is_planned_run_and_resumed(tx):
    market = create_market(tx, "DER", "Surco")
    _only_my_market(tx, market)
    plan = plan_month(tx, MonthUsage(0, 0), budget_usd=5, serpapi_quota=250, now=NOW)
    assert [
        (m.market_id, m.run_id, m.plan.chatgpt_calls, m.plan.serpapi_calls) for m in plan.markets
    ] == [(market, None, 30, 30)]
    assert plan.fits

    clients = {
        "chatgpt_api": _engine("chatgpt_api", fail_on={3}),
        "google_ai_mode": _engine("google_ai_mode"),
    }
    [first] = run_month(tx, plan, clients, _extractor, now=NOW)
    assert first.status == "incomplete" and first.answers == 59 and first.failures

    again = plan_month(tx, MonthUsage(0, 0), budget_usd=5, serpapi_quota=250, now=NOW)
    [m] = again.markets
    assert m.run_id == first.run_id and m.plan.chatgpt_calls == 1 and m.plan.serpapi_calls == 0

    clients = {"chatgpt_api": _engine("chatgpt_api"), "google_ai_mode": _engine("google_ai_mode")}
    [second] = run_month(tx, again, clients, _extractor, now=NOW)
    assert second.run_id == first.run_id and second.status == "complete" and second.answers == 60
    assert second.mentions == 1  # only the resumed answer was left to extract


def test_over_budget_month_is_not_run(tx):
    market = create_market(tx, "DER", "Surco")
    _only_my_market(tx, market)
    plan = plan_month(tx, MonthUsage(4.9, 0), budget_usd=5, serpapi_quota=250, now=NOW)
    assert not plan.fits
    with pytest.raises(ValueError, match="presupuesto"):
        run_month(tx, plan, {}, _extractor, now=NOW)
