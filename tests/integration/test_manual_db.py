from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from visible_ia.mercados.mercado import create_market
from visible_ia.motor.manual import ManualError, import_registry, save_manual
from visible_ia.motor.presupuesto import month_usage

pytestmark = pytest.mark.integration

REGISTRY = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "01-descubrimiento"
    / "prueba-fuentes"
    / "registro.csv"
)


def _clear_manual_runs(tx):
    # Dev keeps the real phase-1 import; the fixture's transaction is rolled back anyway.
    with tx.cursor() as cur:
        cur.execute("delete from public.runs where kind = 'manual'")


def test_import_phase1_registry_counts_rows_per_surface(tx):
    _clear_manual_runs(tx)
    result = import_registry(tx, REGISTRY, create_markets=True)

    assert result.by_surface == {
        "chatgpt_app_manual": 11,
        "gemini_app_manual": 10,
        "google_ai_mode_manual": 10,
    }
    assert result.imported == 31
    assert len(result.skipped) == 1 and "Perplexity" in result.skipped[0]

    with tx.cursor() as cur:
        cur.execute(
            "select count(*), count(*) filter (where r.raw->>'excluir_calibracion' = 'true'), "
            "bool_and(ru.kind = 'manual'), bool_and(r.provider = 'manual') "
            "from public.responses r join public.runs ru on ru.id = r.run_id "
            "where r.raw->>'importado_de' = 'registro.csv'"
        )
        total, lima, all_manual, provider_manual = cur.fetchone()
        assert (total, lima, all_manual, provider_manual) == (31, 6, True, True)
        cur.execute(
            "select count(*) from public.sources s join public.responses r "
            "on r.id = s.response_id where r.raw->>'importado_de' = 'registro.csv'"
        )
        assert cur.fetchone()[0] > 0
        cur.execute(
            "select count(*) from public.markets where active = false and "
            "(category_code, district) in (('EDE', 'San Isidro'), ('DER', 'Surco'))"
        )
        assert cur.fetchone()[0] == 2

    again = import_registry(tx, REGISTRY, create_markets=True)
    assert again.imported == 0 and again.already_there == 31


def test_without_create_markets_missing_markets_are_skipped(tx):
    _clear_manual_runs(tx)
    result = import_registry(tx, REGISTRY, create_markets=False)
    assert all("--crear-mercados" in s or "Perplexity" in s for s in result.skipped)
    assert result.imported + len(result.skipped) == 32


def test_pasted_sample_gets_next_repetition_and_stays_out_of_the_budget(tx):
    market_id = create_market(tx, "DER", "Surco")
    day = date(2026, 10, 3)
    first = save_manual(
        tx, market_id, "DER-01", "gemini_app_manual", "Te recomiendo X.", [], taken_on=day
    )
    second = save_manual(
        tx,
        market_id,
        "DER-01",
        "gemini_app_manual",
        "Te recomiendo Y.",
        ["https://www.y.pe/?utm_source=x"],
        taken_on=day,
    )
    assert first[0] == second[0]  # same manual run for the month
    assert (first[1], second[1]) == (1, 2)
    usage = month_usage(tx, datetime(2026, 10, 20, tzinfo=UTC))
    assert usage.serpapi_used == 0 and usage.spent_usd == 0


def test_invalid_samples_are_rejected(tx):
    market_id = create_market(tx, "DER", "Surco")
    day = date(2026, 10, 3)
    with pytest.raises(ManualError, match="Superficie"):
        save_manual(tx, market_id, "DER-01", "chatgpt_api", "x", [], taken_on=day)
    with pytest.raises(ManualError, match="vacía"):
        save_manual(tx, market_id, "DER-01", "gemini_app_manual", "  ", [], taken_on=day)
    with pytest.raises(ManualError, match="IMP-01"):
        save_manual(tx, market_id, "IMP-01", "gemini_app_manual", "x", [], taken_on=day)
