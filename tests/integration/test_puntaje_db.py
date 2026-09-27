from datetime import date

import pytest

from visible_ia.mercados.clinicas import ClinicRow, import_clinics, list_market_clinics
from visible_ia.mercados.mercado import create_market, list_questions
from visible_ia.motor.corrida import Call, create_run, save_response
from visible_ia.motor.manual import save_manual
from visible_ia.motor.modelos import EngineResponse
from visible_ia.puntaje.indice import ScoreError, calculate, month_shift, ranking

pytestmark = pytest.mark.integration


def _setup(tx):
    market = create_market(tx, "DER", "Surco")
    import_clinics(
        tx,
        market,
        [
            ClinicRow(
                name="Clínica Uno", district="Surco", maps_url="https://maps.google.com/?cid=t-p-1"
            ),
            ClinicRow(
                name="Clínica Dos", district="Surco", maps_url="https://maps.google.com/?cid=t-p-2"
            ),
            ClinicRow(
                name="Clínica Tres", district="Surco", maps_url="https://maps.google.com/?cid=t-p-3"
            ),
        ],
        date(2026, 9, 27),
    )
    ids = {name: cid for cid, name, *_ in list_market_clinics(tx, market)}
    run_id = create_run(
        tx, market, surfaces=["chatgpt_api", "google_ai_mode"], repetitions=1,
        estimated_cost_usd=0, forced=False,
    )  # fmt: skip
    questions = list_questions(tx, market)
    with tx.cursor() as cur:
        for q in questions:
            for surface in ("chatgpt_api", "google_ai_mode"):
                answer = EngineResponse(surface=surface, provider="fake", text="x")
                save_response(tx, run_id, Call(q.id, q.template_id, q.text, surface, 1), answer)
        cur.execute(
            "select id, surface from public.responses where run_id = %s order by id", (run_id,)
        )
        responses = cur.fetchall()
        rows = []
        for i, (rid, surface) in enumerate(responses):
            if surface == "chatgpt_api" and i < 12:  # Uno in 6 of 10 ChatGPT answers
                rows.append((rid, 1, "Clínica Uno", ids["Clínica Uno"], "auto"))
            if surface == "google_ai_mode":  # Dos in all Google answers, one discarded
                rows.append((rid, 1, "Clínica Dos", ids["Clínica Dos"], "auto"))
        rows[-1] = rows[-1][:4] + ("discarded",)
        cur.executemany(
            "insert into public.mentions (response_id, position, raw_name, clinic_id, status) "
            "values (%s, %s, %s, %s, %s)",
            rows,
        )
    # A manual sample naming Tres must not count.
    save_manual(
        tx, market, "DER-01", "gemini_app_manual", "Clínica Tres", [], taken_on=date(2026, 9, 27)
    )
    return market, run_id, ids


def test_only_reviewed_api_runs_are_scored(tx):
    market, run_id, _ = _setup(tx)
    with pytest.raises(ScoreError, match="revisa"):
        calculate(tx, run_id)
    with tx.cursor() as cur:
        cur.execute(
            "select id from public.runs where market_id = %s and kind = 'manual'", (market,)
        )
        (manual_run,) = cur.fetchone()
    with pytest.raises(ScoreError, match="manual"):
        calculate(tx, manual_run)


def test_scores_are_saved_and_ranked(tx):
    market, run_id, ids = _setup(tx)
    with tx.cursor() as cur:
        cur.execute("update public.runs set status = 'reviewed' where id = %s", (run_id,))
    _, month, _ = calculate(tx, run_id)
    assert month.day == 1  # the run's month (Lima)

    with tx.cursor() as cur:
        cur.execute(
            "select clinic_id, surface, n_responses, appearances, presence_index "
            "from public.monthly_scores where market_id = %s",
            (market,),
        )
        saved = {(c, s): (n, k, float(i)) for c, s, n, k, i in cur.fetchall()}
    assert saved[ids["Clínica Uno"], "chatgpt_api"][1:] == (6, 60.0)
    assert saved[ids["Clínica Dos"], "google_ai_mode"] == (10, 9, 90.0)  # one discarded
    assert saved[ids["Clínica Tres"], "combined"] == (20, 0, 0.0)  # manual sample ignored

    _, rows = ranking(tx, market)
    assert [r.name for r in rows] == ["Clínica Dos", "Clínica Uno", "Clínica Tres"]
    assert rows[0].combined == 45.0 and rows[1].combined == 30.0

    calculate(tx, run_id)  # recalculating updates, never duplicates
    with tx.cursor() as cur:
        cur.execute("select count(*) from public.monthly_scores where market_id = %s", (market,))
        assert cur.fetchone()[0] == 9


def test_second_month_gets_change_and_window(tx):
    market, run_id, ids = _setup(tx)
    with tx.cursor() as cur:
        cur.execute("update public.runs set status = 'reviewed' where id = %s", (run_id,))
    _, month, _ = calculate(tx, run_id)
    with tx.cursor() as cur:
        # Pretend this month's scores belong to the previous month, then score again.
        cur.execute(
            "update public.monthly_scores set month = %s where market_id = %s",
            (month_shift(month, -1), market),
        )
    calculate(tx, run_id)
    with tx.cursor() as cur:
        cur.execute(
            "select change, window3_index, detectable_diff from public.monthly_scores "
            "where market_id = %s and month = %s and clinic_id = %s and surface = 'combined'",
            (market, month, ids["Clínica Dos"]),
        )
        change, window, detectable = cur.fetchone()
    assert change == "no_clear_change"
    assert float(window) == 45.0 and detectable is not None


def test_sources_and_gap_from_the_database(tx):
    from visible_ia.puntaje.brecha import gap_table
    from visible_ia.puntaje.fuentes import latest_reviewed_month, load_citations, top_sources

    market, run_id, ids = _setup(tx)
    with tx.cursor() as cur:
        cur.execute("update public.runs set status = 'reviewed' where id = %s", (run_id,))
        cur.execute(
            "select id from public.responses where run_id = %s and surface = 'chatgpt_api' "
            "order by id limit 3",
            (run_id,),
        )
        for (rid,) in cur.fetchall():
            cur.execute(
                "insert into public.sources (response_id, url, domain, source_type) "
                "values (%s, 'https://www.doctoralia.pe/x', 'doctoralia.pe', 'doctoralia')",
                (rid,),
            )
        # Tres: great on Maps, absent from the AI -> gap. Uno: well rated but present.
        cur.execute(
            "update public.clinics set rating = 4.9, review_count = 300, data_date = '2026-09-27' "
            "where id = any(%s)",
            ([ids["Clínica Tres"], ids["Clínica Uno"]],),
        )
    calculate(tx, run_id)

    month = latest_reviewed_month(tx, market)
    citations, total = load_citations(tx, market, month)
    assert total == 20
    doctoralia = top_sources(citations, total)["doctoralia"][0]
    assert (doctoralia.answers, doctoralia.share) == (3, 15.0)

    _, rows = gap_table(tx, market)
    gaps = [r.name for r in rows if r.gap]
    assert gaps == ["Clínica Tres"]
    assert rows[0].data_date.isoformat() == "2026-09-27"
