import re
from datetime import date

from visible_ia.informes.contexto import build_context, reason_filter, reason_targets
from visible_ia.informes.profundo import (
    Answer,
    Candidate,
    ModelChooser,
    candidates,
    competitor_reasons,
    missing_pages,
    question_table,
    split_sentences,
    validate_picks,
)
from visible_ia.informes.render import render_diagnostic
from visible_ia.motor.tarifas import openai_rates

LARCO, PARDO, BENAVIDES, ME = 1, 2, 3, 9
DAY = date(2026, 9, 26)
TEXT_A = (
    "Te recomiendo **Clínica Sonrisa Larco**, que destaca por sus más de 600 reseñas y su "
    "tecnología de implantes guiados. También Centro Dental Pardo, con especialistas en "
    "rehabilitación oral. Atiende la Dra. Ana Pérez Soto en Larco."
)
TEXT_B = "Para implantes en Miraflores, Tu Clínica Dental tiene muy buenas opiniones de pacientes."


def _answer(rid, text, clinics, question_id=1, form="M", urls=(), surface="chatgpt_api"):
    return Answer(rid, surface, question_id, f"Pregunta {question_id}", form, DAY, text,
                  frozenset(clinics), tuple(urls))  # fmt: skip


def test_sentences_are_literal_substrings():
    sentences = split_sentences(
        "- Uno es muy bueno por sus reseñas.\n2. Dos destaca en tecnología."
    )
    assert sentences == ["Uno es muy bueno por sus reseñas.", "Dos destaca en tecnología."]
    assert all(s in "- Uno es muy bueno por sus reseñas.\n2. Dos destaca en tecnología."
               for s in sentences)  # fmt: skip


def test_candidates_only_from_answers_that_name_the_clinic():
    answers = [_answer(1, TEXT_A, {LARCO, PARDO}), _answer(2, TEXT_A, {PARDO})]
    got = candidates(answers, LARCO, ["Clínica Sonrisa Larco", "Sonrisa Larco"])
    assert [c.answer.id for c in got] == [1] and "600 reseñas" in got[0].sentence


def test_invented_or_invalid_picks_are_dropped():
    a = _answer(1, TEXT_A, {LARCO})
    real = Candidate(a, split_sentences(TEXT_A)[0])
    invented = Candidate(a, "Sonrisa Larco es la mejor clínica del Perú.")
    assert validate_picks([0, 1, 7, -1, 0], [real, invented]) == [real]


def test_model_failure_falls_back_to_literal_sentences():
    answers = [_answer(1, TEXT_A, {LARCO, PARDO})]

    def broken(name, sentences):
        raise RuntimeError("API caída")

    [r] = competitor_reasons([(LARCO, "Clínica Sonrisa Larco", 50.0)], answers,
                             {LARCO: ["Clínica Sonrisa Larco"]}, broken)  # fmt: skip
    assert r.quotes and all(q.sentence in q.answer.text for q in r.quotes)


def test_model_only_picks_numbers_and_cost_is_counted():
    class FakeResponse:
        def model_dump(self, mode):
            return {
                "output": [{"content": [{"type": "output_text", "text": '{"elegidas": [0, 5]}'}]}],
                "usage": {"input_tokens": 2400, "output_tokens": 120},
            }

    class FakeClient:
        class responses:  # noqa: N801
            @staticmethod
            def create(**kwargs):
                assert "Frases:" in kwargs["input"] and kwargs["model"] == "gpt-5-nano"
                return FakeResponse()

    chooser = ModelChooser(FakeClient(), openai_rates())
    answers = [_answer(1, TEXT_A, {LARCO})]
    [r] = competitor_reasons([(LARCO, "Clínica Sonrisa Larco", 50.0)], answers,
                             {LARCO: ["Clínica Sonrisa Larco"]}, chooser)  # fmt: skip
    assert len(r.quotes) == 1  # 5 is out of range and dropped
    assert chooser.calls == 1 and 0 < chooser.cost_usd < 0.001


def test_missing_pages_skip_own_websites_and_pages_cited_with_the_clinic():
    urls_rival = [
        ("https://www.doctoralia.pe/clinicas/sonrisa-larco", "doctoralia.pe", "doctoralia"),
        ("https://sonrisalarco.pe/implantes", "sonrisalarco.pe", "own_website"),
        ("https://limadentalrating.com/top", "limadentalrating.com", "directory"),
        ("https://www.google.com/maps/place/Sonrisa+Larco", "google.com", "google_profile"),
    ]
    answers = [
        _answer(1, TEXT_A, {LARCO}, urls=urls_rival),
        _answer(2, TEXT_A, {PARDO}, urls=urls_rival[:1]),
        _answer(3, TEXT_B, {ME}, urls=[urls_rival[2], ("https://tuclinica.pe/", "tuclinica.pe",
                                                       "own_website")]),
    ]  # fmt: skip
    pages, webs = missing_pages(answers, ME, [LARCO, PARDO], "https://tuclinica.pe")
    assert [(p.kind, p.answers) for p in pages] == [("Doctoralia", 2)]
    assert webs == {"competidores": 1, "tuya": 1}


def test_question_table_by_form():
    answers = [
        _answer(1, TEXT_A, {LARCO}, question_id=1, form="M"),
        _answer(2, TEXT_B, {ME, LARCO}, question_id=1, form="M"),
        _answer(3, TEXT_B, {ME}, question_id=2, form="P"),
    ]
    groups = question_table(answers, ME, LARCO)
    assert [g["forma"] for g in groups] == ["Mejor", "Procedimiento"]
    assert groups[0]["preguntas"][0] == {"pregunta": "Pregunta 1", "forma": "M", "total": 2,
                                         "tu": 1, "lider": 2}  # fmt: skip


def test_report_shows_the_new_sections_numbered_and_masked():
    from test_informe_diagnostico import _data

    data = _data()
    data.deep_answers = [
        _answer(10, "Te recomiendo Smiles Peru, que destaca por sus reseñas y su trato. "
                "La atiende la Dra. Ana Pérez Soto con mucha experiencia en Smiles Peru.",
                {1}, urls=[("https://www.doctoralia.pe/x", "doctoralia.pe", "doctoralia")]),
        _answer(11, "Clínica Odontologists tiene buenas opiniones de sus pacientes en Miraflores.",
                {4}, question_id=2, form="R"),
    ]  # fmt: skip
    data.reasons = competitor_reasons(reason_targets(data), data.deep_answers,
                                      data.market_names, None, reason_filter(data))  # fmt: skip
    html = render_diagnostic(build_context(data))
    sections = re.findall(r'data-seccion="([^"]+)"', html)
    assert sections == ["resumen", "competencia", "preguntas", "razones", "faltantes", "plan",
                        "metodo"]  # fmt: skip
    assert "destaca por sus reseñas" in html and "Ana Pérez" not in html
    assert "doctoralia.pe/x" in html and "None" not in html


def test_a_title_period_does_not_cut_the_sentence():
    [s] = split_sentences("En Centro Dental Pardo atiende la Dra. Lucía Rojas Vega, especialista.")
    assert s.startswith("En Centro Dental Pardo") and "Dra. Lucía" in s


def test_sentences_with_a_professional_name_are_not_candidates():
    text = (
        "Clínica Sonrisa Larco destaca por sus reseñas. "
        "En Clínica Sonrisa Larco atiende la Dra. Ana Pérez Soto."
    )
    got = candidates([_answer(1, text, {LARCO})], LARCO, ["Clínica Sonrisa Larco"],
                     keep=lambda s: "Dra." not in s)  # fmt: skip
    assert [c.sentence for c in got] == ["Clínica Sonrisa Larco destaca por sus reseñas."]
