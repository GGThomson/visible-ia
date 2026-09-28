import re
from datetime import date

import pytest

from visible_ia.informes.mensual import MonthlyData, MonthScore, build_monthly_context
from visible_ia.informes.render import render_monthly
from visible_ia.puntaje.calibracion import APPS, Calibration, chatgpt_alert, compare

SEP, OCT, NOV = date(2026, 9, 1), date(2026, 10, 1), date(2026, 11, 1)
SCORES = {
    SEP: MonthScore(SEP, 10, 5, 20, 16.7, 3.3, 10, 5, 20, "first_month", 11, 60),
    OCT: MonthScore(OCT, 25, 16, 37, 30, 20, 17.5, 12, 25, "up", 14, 60),
    NOV: MonthScore(NOV, 28, 18, 40, 33, 23, 21.1, 16, 27, "no_clear_change", 15, 60),
}


def _data(month, calibration=(), alert=False, tasks=None, ai_patients=None):
    history = [s for m, s in SCORES.items() if m <= month]
    ranking = [
        {"clinic_id": 1, "name": "Smiles Peru", "combined": 50.0, "previous": 48.0},
        {"clinic_id": 2, "name": "Dental Pérez Yance", "combined": 36.7, "previous": None},
        {"clinic_id": 3, "name": "Dr. Aldo", "combined": 30.0, "previous": 31.0},
        {"clinic_id": 12, "name": "Clínica Odontologists", "combined": history[-1].combined,
         "previous": history[-2].combined if len(history) > 1 else None},
    ]  # fmt: skip
    return MonthlyData(
        site_id=1, clinic_id=12, clinic_name="Clínica Odontologists", category="IMP",
        district="Miraflores", month=month, history=history, ranking=ranking,
        citations=[(1, "chatgpt_api", "smilesperu.com", "own_website"),
                   (2, "google_ai_mode", "doctoralia.pe", "doctoralia")],
        total_answers=60,
        tasks=tasks if tasks is not None else [
            {"title": "Completa tu ficha de Google", "status": "done"},
            {"title": "Completa tu perfil de Doctoralia", "status": "pending"},
        ],
        calibration=list(calibration), calibration_alert=alert,
        ai_patients=ai_patients or {},
    )  # fmt: skip


@pytest.mark.parametrize("month, months", [(SEP, 1), (OCT, 2), (NOV, 3)])
def test_report_renders_with_one_two_and_three_months(month, months):
    html = render_monthly(build_monthly_context(_data(month)))
    sections = re.findall(r'data-seccion="([^"]+)"', html)
    assert sections == [
        "resumen", "evolucion", "competidores", "fuentes", "tareas", "atribucion", "calibracion"
    ]  # fmt: skip
    assert len(re.findall(r'class="barra( cliente)?"', html)) == months
    assert "None" not in html and "{{" not in html
    assert "No garantizamos un puesto #1" in html


def test_first_month_explains_there_is_no_trend_yet():
    ctx = build_monthly_context(_data(SEP))
    assert "es el primer mes medido" in ctx["frase"]
    assert "Es el primer mes medido" in render_monthly(ctx)


def test_change_sentence_and_detectable_difference():
    up = build_monthly_context(_data(OCT))
    assert "subió frente al mes anterior" in up["frase"]
    flat = build_monthly_context(_data(NOV))
    assert "no tuvo un cambio claro" in flat["frase"] and "menor a 15 puntos" in flat["frase"]
    assert flat["ventana"] == {"meses": 3, "indice": "21", "bajo": "16", "alto": "27"}


def test_competitors_show_this_month_and_the_previous_one():
    ctx = build_monthly_context(_data(OCT))
    rows = {c["nombre"]: c for c in ctx["competidores"]}
    assert rows["Smiles Peru"]["anterior"] == "48" and rows["Dental Pérez Yance"]["anterior"] == "—"
    assert (
        rows["Clínica Odontologists"]["es_cliente"]
        and rows["Clínica Odontologists"]["anterior"] == "10"
    )


def test_checklist_splits_done_and_pending():
    ctx = build_monthly_context(_data(OCT))
    assert ctx["tareas"] == {
        "hechas": ["Completa tu ficha de Google"],
        "pendientes": ["Completa tu perfil de Doctoralia"],
    }


def test_calibration_and_alert_are_shown():
    cal = [Calibration(APPS["chatgpt_app_manual"], 10, 8, 3, 37.5, "Smiles Peru", "Smiles Peru")]
    html = render_monthly(build_monthly_context(_data(NOV, cal, alert=True)))
    assert "38 %" in html and "Smiles Peru / Smiles Peru ✔" in html
    assert "por segundo mes seguido" in html
    assert "no hubo muestra manual" in render_monthly(build_monthly_context(_data(NOV)))


def test_compare_coincidence_and_leader():
    names = {1: "Smiles Peru", 2: "Pérez Yance", 3: "Cano", 4: "Otra"}
    c = compare([1, 1, 2, 4], [1, 2, 2, 3], names, "ChatGPT (app)", 10)
    assert (c.app_clinics, c.shared, c.coincidence) == (3, 2, 66.7)
    assert (
        c.leader_app == "Smiles Peru" and c.leader_api == "Pérez Yance" and c.same_leader is False
    )
    assert compare([], [1], names, "x", 0).coincidence is None


def test_alert_needs_two_months_below_50():
    low = [Calibration(APPS["chatgpt_app_manual"], 10, 4, 1, 25.0, None, None)]
    ok = [Calibration(APPS["chatgpt_app_manual"], 10, 4, 3, 75.0, None, None)]
    gemini_low = [Calibration(APPS["gemini_app_manual"], 10, 4, 1, 25.0, None, None)]
    assert chatgpt_alert(low, low) is True
    assert chatgpt_alert(low, ok) is False
    assert chatgpt_alert(low, []) is False
    assert chatgpt_alert(gemini_low, gemini_low) is False


def test_ai_patients_of_the_month_appear_in_the_report():
    ctx = build_monthly_context(_data(OCT, ai_patients={SEP: 1, OCT: 3, NOV: 7}))
    assert ctx["atribucion"]["este_mes"] == 3
    assert [h["pacientes"] for h in ctx["atribucion"]["historial"]] == [1, 3]  # not November
    html = render_monthly(ctx)
    assert "registraste <b>3 pacientes</b>" in html and "setiembre" in html


def test_report_without_ai_patients_invites_to_count_them():
    html = render_monthly(build_monthly_context(_data(OCT)))
    assert "no registraste pacientes por IA" in html and "¿Cómo nos conociste?" in html
