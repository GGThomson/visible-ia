"""Resumable runs (HU-04): 10 questions × N repetitions × surfaces, saved as they arrive.

Each answer is committed as soon as it arrives, so a run cut halfway (Ctrl+C, a crash, a
failed call) keeps what it already has; resuming only makes the missing calls. The unique
key (run, question, surface, repetition) makes a duplicate impossible.
"""

import threading
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import psycopg
from psycopg.types.json import Jsonb

from visible_ia.mercados.mercado import current_version, list_questions
from visible_ia.motor import google_ai_mode
from visible_ia.motor.modelos import EngineResponse
from visible_ia.motor.presupuesto import RunPlan, month_bounds

MAX_CONCURRENCY_PER_SURFACE = 3
# Lower caps for surfaces that rate-limit parallel calls.
SURFACE_CONCURRENCY = {"google_ai_mode": google_ai_mode.MAX_CONCURRENCY}

Client = Callable[[str], EngineResponse]


class RunError(ValueError):
    pass


@dataclass(frozen=True)
class Call:
    question_id: int
    template_id: str
    text: str
    surface: str
    repetition: int


@dataclass(frozen=True)
class RunSummary:
    run_id: int
    status: str
    done: int
    total: int
    cost_usd: float
    failures: list[dict]


# --- sources -------------------------------------------------------------------------------


def normalize_url(url: str) -> str:
    """Drop utm_* parameters and the fragment (the rest of the URL is kept as is)."""
    parts = urlsplit(url.strip())
    query = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)]
    query = [(k, v) for k, v in query if not k.lower().startswith("utm_")]
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), ""))


def domain_of(url: str) -> str:
    host = (urlsplit(url.strip()).hostname or "").lower()
    return host.removeprefix("www.")


# --- database ------------------------------------------------------------------------------


def create_run(
    conn: psycopg.Connection,
    market_id: int,
    *,
    surfaces: list[str],
    repetitions: int,
    estimated_cost_usd: float,
    forced: bool,
    now: datetime | None = None,
) -> int:
    version = current_version(conn, market_id)
    month, _ = month_bounds(now)
    with conn.transaction(), conn.cursor() as cur:
        cur.execute(
            "insert into public.runs (market_id, month, kind, status, estimated_cost_usd, forced, "
            "question_set_version, surfaces, repetitions) "
            "values (%s, %s, 'api', 'pending', %s, %s, %s, %s, %s) returning id",
            (market_id, month, estimated_cost_usd, forced, version, surfaces, repetitions),
        )
        (run_id,) = cur.fetchone()
    return run_id


def _run_row(conn: psycopg.Connection, run_id: int) -> tuple:
    with conn.cursor() as cur:
        cur.execute(
            "select market_id, question_set_version, surfaces, repetitions, status, kind, "
            "forced, failures from public.runs where id = %s",
            (run_id,),
        )
        row = cur.fetchone()
    if row is None:
        raise RunError(f"No existe la corrida {run_id}")
    return row


def all_calls(conn: psycopg.Connection, run_id: int) -> list[Call]:
    market_id, version, surfaces, repetitions, *_ = _run_row(conn, run_id)
    questions = list_questions(conn, market_id, version)
    return [
        Call(q.id, q.template_id, q.text, surface, rep)
        for surface in surfaces
        for q in questions
        for rep in range(1, repetitions + 1)
    ]


def pending_calls(conn: psycopg.Connection, run_id: int) -> list[Call]:
    with conn.cursor() as cur:
        cur.execute(
            "select question_id, surface, repetition from public.responses where run_id = %s",
            (run_id,),
        )
        done = set(cur.fetchall())
    return [
        c for c in all_calls(conn, run_id) if (c.question_id, c.surface, c.repetition) not in done
    ]


def plan_of(calls: list[Call]) -> RunPlan:
    return RunPlan(
        chatgpt_calls=sum(c.surface == "chatgpt_api" for c in calls),
        serpapi_calls=sum(c.surface == "google_ai_mode" for c in calls),
    )


def save_response(
    conn: psycopg.Connection, run_id: int, call: Call, answer: EngineResponse
) -> bool:
    """Store one answer and its sources in a single transaction. False if it already existed."""
    with conn.transaction(), conn.cursor() as cur:
        cur.execute(
            "insert into public.responses (run_id, question_id, surface, repetition, provider, "
            "model, text, raw, cost_usd, no_answer) "
            "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
            "on conflict (run_id, question_id, surface, repetition) do nothing returning id",
            (
                run_id,
                call.question_id,
                call.surface,
                call.repetition,
                answer.provider,
                answer.model,
                answer.text,
                Jsonb(answer.raw),
                answer.cost_usd,
                answer.empty,
            ),
        )
        row = cur.fetchone()
        if row is None:
            return False
        sources = []
        seen = set()
        for citation in answer.citations:
            url = normalize_url(citation.url)
            if url not in seen and domain_of(url):
                seen.add(url)
                sources.append((row[0], url, domain_of(url)))
        if sources:
            cur.executemany(
                "insert into public.sources (response_id, url, domain) values (%s, %s, %s)",
                sources,
            )
    return True


def _set_status(conn: psycopg.Connection, run_id: int, status: str, **fields) -> None:
    sets = ["status = %s"] + [f"{name} = %s" for name in fields]
    values = [status] + [Jsonb(v) if name == "failures" else v for name, v in fields.items()]
    # Column names come from the callers in this module, never from user input.
    with conn.transaction(), conn.cursor() as cur:
        cur.execute(f"update public.runs set {', '.join(sets)} where id = %s", (*values, run_id))


def _refresh_cost(conn: psycopg.Connection, run_id: int) -> float:
    with conn.transaction(), conn.cursor() as cur:
        cur.execute(
            "update public.runs set actual_cost_usd = "
            "(select coalesce(sum(cost_usd), 0) from public.responses where run_id = %s) "
            "where id = %s returning actual_cost_usd",
            (run_id, run_id),
        )
        return float(cur.fetchone()[0])


def summary(conn: psycopg.Connection, run_id: int) -> RunSummary:
    *_, status, _kind, _forced, failures = _run_row(conn, run_id)
    total = len(all_calls(conn, run_id))
    with conn.cursor() as cur:
        cur.execute(
            "select count(*), coalesce(sum(cost_usd), 0) from public.responses where run_id = %s",
            (run_id,),
        )
        done, cost = cur.fetchone()
    return RunSummary(run_id, status, done, total, float(cost), failures or [])


def progress_by_surface(conn: psycopg.Connection, run_id: int) -> dict[str, tuple[int, int]]:
    """surface -> (done, total)."""
    totals: dict[str, int] = {}
    for call in all_calls(conn, run_id):
        totals[call.surface] = totals.get(call.surface, 0) + 1
    with conn.cursor() as cur:
        cur.execute(
            "select surface, count(*) from public.responses where run_id = %s group by surface",
            (run_id,),
        )
        done = dict(cur.fetchall())
    return {s: (done.get(s, 0), t) for s, t in totals.items()}


# --- execution -----------------------------------------------------------------------------


def execute(
    conn: psycopg.Connection,
    run_id: int,
    clients: dict[str, Client],
    *,
    on_progress: Callable[[Call, EngineResponse | None, Exception | None], None] | None = None,
    concurrency: int = MAX_CONCURRENCY_PER_SURFACE,
    now: Callable[[], datetime] = datetime.now,
) -> RunSummary:
    """Make the missing calls (at most `concurrency` at a time per surface) and save each one.

    Interrupting (Ctrl+C) leaves the run 'incomplete' with everything already saved.
    """
    calls = pending_calls(conn, run_id)
    missing = {c.surface for c in calls} - set(clients)
    if missing:
        raise RunError(f"Falta el cliente de: {', '.join(sorted(missing))}")
    _set_status(conn, run_id, "running", started_at=now().astimezone(), failures=[])

    lock = threading.Lock()  # one writer at a time on the shared connection
    failures: list[dict] = []

    def work(call: Call) -> None:
        try:
            answer = clients[call.surface](call.text)
        except Exception as exc:  # any failure is recorded, never lost
            with lock:
                failures.append(
                    {
                        "question_id": call.question_id,
                        "template_id": call.template_id,
                        "surface": call.surface,
                        "repetition": call.repetition,
                        "error": f"{type(exc).__name__}: {exc}"[:500],
                    }
                )
            if on_progress:
                on_progress(call, None, exc)
            return
        with lock:
            save_response(conn, run_id, call, answer)
        if on_progress:
            on_progress(call, answer, None)

    by_surface: dict[str, list[Call]] = {}
    for call in calls:
        by_surface.setdefault(call.surface, []).append(call)
    pools = {
        s: ThreadPoolExecutor(max_workers=min(concurrency, SURFACE_CONCURRENCY.get(s, concurrency)))
        for s in by_surface
    }
    try:
        futures = [pools[c.surface].submit(work, c) for c in calls]
        for future in as_completed(futures):
            future.result()
    finally:
        # On Ctrl+C, queued calls are cancelled but calls in flight (already paid) finish
        # and are saved before the run is closed.
        for pool in pools.values():
            pool.shutdown(wait=True, cancel_futures=True)
        with lock:
            _refresh_cost(conn, run_id)
            left = pending_calls(conn, run_id)
            status = "complete" if not left else "incomplete"
            _set_status(
                conn,
                run_id,
                status,
                finished_at=now().astimezone(),
                failures=list(failures),
            )
    return summary(conn, run_id)
