from datetime import UTC, date, datetime

import httpx
import pytest

from visible_ia.config import Settings
from visible_ia.motor import google_ai_mode
from visible_ia.motor.presupuesto import (
    MonthUsage,
    RunPlan,
    authorize,
    check,
    month_bounds,
)
from visible_ia.motor.tarifas import load_openai_rates

RATES = load_openai_rates()
PER_CALL = RATES.estimated_call_cost()
MARKET = RunPlan.for_market(10, 3, ["chatgpt_api", "google_ai_mode"])


def test_estimated_call_cost_from_the_table_profile():
    # 2 × 0.01 + (15000 × 0.25 + 3000 × 2.00) / 1e6
    assert PER_CALL == pytest.approx(0.02975)


def test_market_plan_is_10_by_3_per_surface():
    assert MARKET == RunPlan(chatgpt_calls=30, serpapi_calls=30)
    assert RunPlan.for_market(10, 3, ["google_ai_mode"]) == RunPlan(0, 30)


def test_default_budget_is_the_approved_5_usd(monkeypatch):
    monkeypatch.delenv("MONTHLY_BUDGET_USD", raising=False)
    settings = Settings(_env_file=None)
    assert settings.monthly_budget_usd == 5.0
    assert settings.serpapi_monthly_quota == 250


def test_run_within_budget_and_quota_is_ok():
    result = check(MARKET, MonthUsage(1.0, 10), budget_usd=5, serpapi_quota=250, rates=RATES)
    assert result.ok
    assert result.estimated_cost_usd == pytest.approx(30 * PER_CALL, abs=1e-4)
    assert "30 llamadas" in result.explain() and "BLOQUEADA" not in result.explain()


def test_run_exactly_at_the_caps_is_ok():
    estimated = round(30 * PER_CALL, 4)
    usage = MonthUsage(5 - estimated, 220)
    assert check(MARKET, usage, budget_usd=5, serpapi_quota=250, rates=RATES).ok


def test_run_over_the_budget_is_blocked_and_explains_the_cost():
    result = check(MARKET, MonthUsage(4.5, 0), budget_usd=5, serpapi_quota=250, rates=RATES)
    assert not result.ok
    assert len(result.problems) == 1 and "presupuesto de OpenAI" in result.problems[0]
    text = result.explain()
    assert "BLOQUEADA" in text and "US$0.89" in text


def test_run_over_the_serpapi_quota_is_blocked():
    result = check(MARKET, MonthUsage(0, 221), budget_usd=5, serpapi_quota=250, rates=RATES)
    assert not result.ok and "cuota de SerpApi" in result.problems[0]


def test_month_bounds_use_lima_time():
    # 03:00 UTC on Oct 1 is still Sept 30 in Lima (UTC-5).
    assert month_bounds(datetime(2026, 10, 1, 3, tzinfo=UTC)) == (
        date(2026, 9, 1),
        date(2026, 10, 1),
    )
    assert month_bounds(datetime(2026, 10, 1, 6, tzinfo=UTC)) == (
        date(2026, 10, 1),
        date(2026, 11, 1),
    )
    assert month_bounds(datetime(2026, 12, 15, tzinfo=UTC)) == (date(2026, 12, 1), date(2027, 1, 1))


def _blocked():
    return check(MARKET, MonthUsage(4.9, 0), budget_usd=5, serpapi_quota=250, rates=RATES)


def test_authorize_ok_run_never_asks():
    ok = check(MARKET, MonthUsage(0, 0), budget_usd=5, serpapi_quota=250, rates=RATES)
    asked = []
    assert authorize(ok, force=False, prompt=asked.append, echo=lambda _: None)
    assert asked == []


def test_authorize_blocked_run_without_force_is_refused():
    assert not authorize(_blocked(), force=False, prompt=lambda _: "SI", echo=lambda _: None)


@pytest.mark.parametrize(
    "answer, expected", [("SI", True), (" SI ", True), ("si", False), ("", False)]
)
def test_force_needs_the_operator_to_type_si(answer, expected):
    assert (
        authorize(_blocked(), force=True, prompt=lambda _: answer, echo=lambda _: None) is expected
    )


def test_serpapi_account_usage_reads_this_month_usage():
    def handler(request):
        assert request.url.path == "/account.json"
        return httpx.Response(200, json={"this_month_usage": 7, "plan_searches_left": 243})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    assert google_ai_mode.account_usage("k", client=client) == 7
