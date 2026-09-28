from datetime import date

import pytest

from visible_ia.atribucion import save_count
from visible_ia.checklist import generate
from visible_ia.clientes import add_site, create_client
from visible_ia.informes.mensual import build_monthly_context, load_monthly_data
from visible_ia.informes.render import render_monthly
from visible_ia.mercados.clinicas import ClinicRow, import_clinics, list_market_clinics
from visible_ia.mercados.mercado import create_market, list_questions
from visible_ia.motor.corrida import Call, create_run, save_response
from visible_ia.motor.manual import save_manual
from visible_ia.motor.modelos import EngineResponse
from visible_ia.puntaje.indice import calculate

pytestmark = pytest.mark.integration


def test_monthly_report_from_the_database(tx):
    market = create_market(tx, "DER", "Surco")
    import_clinics(
        tx,
        market,
        [
            ClinicRow(name="Clínica Mía", district="Surco", maps_url="https://maps.google.com/?cid=m-1"),
            ClinicRow(name="Competidora", district="Surco", maps_url="https://maps.google.com/?cid=m-2"),
        ],
        date(2026, 9, 27),
    )  # fmt: skip
    ids = {name: cid for cid, name, *_ in list_market_clinics(tx, market)}
    site, _ = add_site(
        tx, create_client(tx, "clinic", "Cliente mensual"), ids["Clínica Mía"], market
    )
    run = create_run(tx, market, surfaces=["chatgpt_api", "google_ai_mode"], repetitions=1,
                     estimated_cost_usd=0, forced=False)  # fmt: skip
    q = list_questions(tx, market)[0]
    for surface in ("chatgpt_api", "google_ai_mode"):
        save_response(tx, run, Call(q.id, q.template_id, q.text, surface, 1),
                      EngineResponse(surface=surface, provider="fake", text="x"))  # fmt: skip
    manual_run, _, _ = save_manual(tx, market, "DER-01", "chatgpt_app_manual", "Competidora", [],
                                   taken_on=date.today())  # fmt: skip
    with tx.cursor() as cur:
        cur.execute(
            "insert into public.mentions (response_id, position, raw_name, clinic_id) "
            "select id, 1, 'Clínica Mía', %s from public.responses where run_id = %s",
            (ids["Clínica Mía"], run),
        )
        cur.execute(
            "insert into public.mentions (response_id, position, raw_name, clinic_id) "
            "select id, 1, 'Competidora', %s from public.responses where run_id = %s",
            (ids["Competidora"], manual_run),
        )
        cur.execute("update public.runs set status = 'reviewed' where id = %s", (run,))
    _, month, _ = calculate(tx, run)
    generate(tx, site)
    save_count(tx, site, month, 2)
    save_count(tx, site, month, 3)  # the clinic corrects it: the last value wins

    data = load_monthly_data(tx, site, month)
    assert data.ai_patients == {month: 3}
    assert data.clinic_name == "Clínica Mía" and len(data.history) == 1
    assert data.history[0].combined == 100.0 and data.tasks
    [cal] = data.calibration
    assert cal.app == "ChatGPT (app)" and cal.coincidence == 0.0  # the app named only the rival
    assert cal.leader_app == "Competidora" and cal.leader_api == "Clínica Mía"

    html = render_monthly(build_monthly_context(data))
    assert (
        "Clínica Mía" in html and "Completa tu ficha de Google" in html and "ChatGPT (app)" in html
    )
    assert "registraste <b>3 pacientes</b>" in html


def test_ai_patients_need_a_real_site_and_a_sane_number(tx):
    with pytest.raises(ValueError, match="No existe"):
        save_count(tx, 10**9, date(2026, 9, 1), 1)
    with pytest.raises(ValueError, match="entre 0"):
        save_count(tx, 1, date(2026, 9, 1), -1)
