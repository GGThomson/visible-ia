import threading
import time

import pytest

from visible_ia.mercados.mercado import create_market
from visible_ia.motor.corrida import (
    RunError,
    create_run,
    execute,
    pending_calls,
    progress_by_surface,
    summary,
)
from visible_ia.motor.modelos import Citation, EngineResponse

pytestmark = pytest.mark.integration

SURFACES = ["chatgpt_api", "google_ai_mode"]


class FakeEngine:
    """Answers every question; the calls whose global number is in `fail_on` raise."""

    def __init__(self, surface, fail_on=(), interrupt_on=None, counter=None):
        self.surface = surface
        self.fail_on = set(fail_on)
        self.interrupt_on = interrupt_on
        self.counter = counter if counter is not None else {"n": 0}
        self.lock = threading.Lock()

    def __call__(self, question: str) -> EngineResponse:
        with self.lock:
            self.counter["n"] += 1
            n = self.counter["n"]
        if n == self.interrupt_on:
            raise KeyboardInterrupt
        if n in self.fail_on:
            raise RuntimeError(f"fallo simulado en la llamada {n}")
        return EngineResponse(
            surface=self.surface,
            provider="fake",
            model="fake-1",
            text=f"Respuesta a: {question}",
            citations=[
                Citation(url="https://www.clinica.pe/?utm_source=openai", title="Clínica"),
                Citation(url="https://clinica.pe/", title="duplicada tras normalizar"),
                Citation(url="https://www.doctoralia.pe/implantes", title="Doctoralia"),
            ],
            searches=1,
            cost_usd=0.01 if self.surface == "chatgpt_api" else 0.0,
            raw={"n": n},
        )


def _run(tx, reps=3, surfaces=SURFACES):
    market_id = create_market(tx, "DER", "Surco")
    return create_run(
        tx, market_id, surfaces=surfaces, repetitions=reps, estimated_cost_usd=0.9, forced=False
    )


def _clients(**kwargs):
    counter = {"n": 0}
    return {s: FakeEngine(s, counter=counter, **kwargs) for s in SURFACES}


def test_full_run_saves_every_call_with_sources(tx):
    run_id = _run(tx)
    assert len(pending_calls(tx, run_id)) == 60

    result = execute(tx, run_id, _clients())

    assert result.status == "complete" and result.done == result.total == 60
    assert result.cost_usd == pytest.approx(0.30)
    assert progress_by_surface(tx, run_id) == {"chatgpt_api": (30, 30), "google_ai_mode": (30, 30)}
    with tx.cursor() as cur:
        cur.execute(
            "select r.provider, r.model, r.text, r.no_answer, q.version "
            "from public.responses r join public.questions q on q.id = r.question_id "
            "where r.run_id = %s limit 1",
            (run_id,),
        )
        provider, model, text, no_answer, version = cur.fetchone()
        assert (provider, model, no_answer, version) == ("fake", "fake-1", False, 1)
        assert text.startswith("Respuesta a: ")
        cur.execute(
            "select distinct s.url, s.domain from public.sources s "
            "join public.responses r on r.id = s.response_id where r.run_id = %s order by 1",
            (run_id,),
        )
        assert cur.fetchall() == [
            ("https://clinica.pe/", "clinica.pe"),
            ("https://www.clinica.pe/", "clinica.pe"),
            ("https://www.doctoralia.pe/implantes", "doctoralia.pe"),
        ]
        cur.execute(
            "select actual_cost_usd, started_at, finished_at from public.runs where id = %s",
            (run_id,),
        )
        cost, started, finished = cur.fetchone()
        assert float(cost) == pytest.approx(0.30) and started and finished


def test_failure_on_call_7_leaves_run_incomplete_and_resume_completes_without_duplicates(tx):
    run_id = _run(tx)
    first = execute(tx, run_id, _clients(fail_on={7}), concurrency=1)

    assert first.status == "incomplete"
    assert first.done == 59
    assert len(first.failures) == 1 and "llamada 7" in first.failures[0]["error"]
    assert first.failures[0]["template_id"].startswith("DER-")
    assert len(pending_calls(tx, run_id)) == 1

    second = execute(tx, run_id, _clients())
    assert second.status == "complete" and second.done == 60 and second.failures == []
    with tx.cursor() as cur:
        cur.execute(
            "select count(*), count(distinct (question_id, surface, repetition)) "
            "from public.responses where run_id = %s",
            (run_id,),
        )
        assert cur.fetchone() == (60, 60)


def test_interrupt_keeps_what_was_saved_and_resume_finishes(tx):
    run_id = _run(tx, surfaces=["chatgpt_api"])
    with pytest.raises(KeyboardInterrupt):
        execute(
            tx, run_id, {"chatgpt_api": FakeEngine("chatgpt_api", interrupt_on=12)}, concurrency=1
        )

    cut = summary(tx, run_id)
    assert cut.status == "incomplete"
    # Calls 1-11 are saved; a call already in flight when the cut arrives may also finish.
    assert cut.done in (11, 12)
    assert len(pending_calls(tx, run_id)) == 30 - cut.done

    done = execute(tx, run_id, {"chatgpt_api": FakeEngine("chatgpt_api")})
    assert done.status == "complete" and done.done == 30
    with tx.cursor() as cur:
        cur.execute("select count(*) from public.responses where run_id = %s", (run_id,))
        assert cur.fetchone()[0] == 30


def test_empty_answer_is_saved_as_no_answer(tx):
    run_id = _run(tx, reps=1, surfaces=["google_ai_mode"])

    def empty(question):
        return EngineResponse(surface="google_ai_mode", provider="serpapi", text="", empty=True)

    result = execute(tx, run_id, {"google_ai_mode": empty})
    assert result.status == "complete"
    with tx.cursor() as cur:
        cur.execute("select bool_and(no_answer) from public.responses where run_id = %s", (run_id,))
        assert cur.fetchone()[0] is True


def test_concurrency_is_three_for_chatgpt_and_one_for_google(tx):
    run_id = _run(tx, reps=1)
    active = {s: 0 for s in SURFACES}
    peak = {s: 0 for s in SURFACES}
    lock = threading.Lock()

    def engine(surface):
        def call(question):
            with lock:
                active[surface] += 1
                peak[surface] = max(peak[surface], active[surface])
            time.sleep(0.05)
            with lock:
                active[surface] -= 1
            return EngineResponse(surface=surface, provider="fake", text="ok")

        return call

    execute(tx, run_id, {s: engine(s) for s in SURFACES})
    assert peak == {"chatgpt_api": 3, "google_ai_mode": 1}


def test_missing_client_and_unknown_run_are_errors(tx):
    run_id = _run(tx)
    with pytest.raises(RunError, match="google_ai_mode"):
        execute(tx, run_id, {"chatgpt_api": FakeEngine("chatgpt_api")})
    with pytest.raises(RunError, match="No existe"):
        pending_calls(tx, 999_999_999)
