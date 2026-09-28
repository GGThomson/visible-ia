from datetime import date

from visible_ia.motor.mensual import (
    MarketPlan,
    MarketResult,
    MonthPlan,
    estimate_issue,
    review_issue,
)
from visible_ia.motor.presupuesto import MonthUsage, RunPlan, check
from visible_ia.motor.tarifas import load_openai_rates

RATES = load_openai_rates()


def _plan(spent=0.0, used=0, markets=1, budget=5.0):
    rows = [
        MarketPlan(i, f"Implantología · Distrito {i}", None, None, RunPlan(30, 30), 60)
        for i in range(1, markets + 1)
    ]
    total = RunPlan(30 * markets, 30 * markets)
    b = check(total, MonthUsage(spent, used), budget_usd=budget, serpapi_quota=250, rates=RATES)
    return MonthPlan(date(2026, 10, 1), rows, b, round(60 * markets * 0.0005, 2))


def test_estimate_issue_says_nothing_was_spent_and_how_to_approve():
    title, body = estimate_issue(_plan())
    assert title == "Corridas de octubre de 2026 · esperando tu OK"
    assert "no se gastó nada" in body and "modo `correr`" in body
    assert "1 mercado activo" in body and "✅" in body
    assert "| Implantología · Distrito 1 | 30 | 30 | nueva |" in body


def test_month_over_budget_does_not_fit_and_says_why():
    mp = _plan(spent=4.5)
    assert not mp.fits
    assert "⛔" in estimate_issue(mp)[1]
    over_quota = _plan(used=240)
    assert not over_quota.fits and "cuota de SerpApi" in estimate_issue(over_quota)[1]


def test_extraction_counts_in_the_budget():
    mp = _plan(spent=5.0 - 1.215 - 0.01)  # ChatGPT fits exactly, extraction does not
    assert mp.budget.ok and not mp.fits


def test_review_issue_lists_runs_steps_and_failures():
    results = [
        MarketResult("Implantología · Miraflores", 7, "complete", 60, 60, 1.1, 200, 2, 8),
        MarketResult(
            "Dermatología · Surco",
            8,
            "incomplete",
            58,
            60,
            1.0,
            150,
            0,
            3,
            ["google_ai_mode DER-02 rep 1: GoogleRateLimited"],
        ),  # fmt: skip
    ]
    title, body = review_issue(date(2026, 10, 1), results)
    assert title == "Revisar corridas de octubre de 2026"
    assert "| Implantología · Miraflores | 7 | complete | 60/60 | US$1.10 |" in body
    assert "visible-ia revisar corrida <corrida> --env prod" in body and "uv run" not in body
    assert "GoogleRateLimited" in body
