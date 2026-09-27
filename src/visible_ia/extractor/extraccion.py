"""Extract a whole run (HU-07): mentions -> matching -> source types, saved per answer.

Only answers without `extracted_at` are processed, so the command can be re-run after a cut
or a failure without paying twice. Each answer is committed on its own.
"""

import threading
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

import psycopg

from visible_ia.extractor import llm
from visible_ia.extractor.fuentes import classify
from visible_ia.extractor.matching import ClinicCandidate, load_market_clinics, match

MAX_CONCURRENCY = 4
# Upper bound per answer used by the budget guard (C4-T01 target).
ESTIMATED_COST_PER_ANSWER = 0.0005

Extractor = Callable[[str, list[str]], llm.Extraction]


@dataclass(frozen=True)
class PendingAnswer:
    response_id: int
    surface: str
    text: str
    raw: dict[str, Any]


@dataclass
class ExtractionSummary:
    extracted: int = 0
    mentions: int = 0
    matched: int = 0
    new: int = 0
    review: int = 0
    cost_usd: float = 0.0
    failures: list[str] = field(default_factory=list)


def run_market(conn: psycopg.Connection, run_id: int) -> int:
    with conn.cursor() as cur:
        cur.execute("select market_id from public.runs where id = %s", (run_id,))
        row = cur.fetchone()
    if row is None:
        raise ValueError(f"No existe la corrida {run_id}")
    return row[0]


def pending_answers(conn: psycopg.Connection, run_id: int) -> list[PendingAnswer]:
    with conn.cursor() as cur:
        cur.execute(
            "select id, surface, coalesce(text, ''), coalesce(raw, '{}'::jsonb) "
            "from public.responses where run_id = %s and extracted_at is null order by id",
            (run_id,),
        )
        return [PendingAnswer(*row) for row in cur.fetchall()]


def market_websites(conn: psycopg.Connection, market_id: int) -> set[str]:
    with conn.cursor() as cur:
        cur.execute(
            "select c.website from public.clinics c "
            "join public.clinic_markets cm on cm.clinic_id = c.id "
            "where cm.market_id = %s and c.website is not null",
            (market_id,),
        )
        return {row[0] for row in cur.fetchall() if row[0].strip()}


def save_extraction(
    conn: psycopg.Connection,
    answer: PendingAnswer,
    extraction: llm.Extraction,
    clinics: list[ClinicCandidate],
    websites: set[str],
    summary: ExtractionSummary,
) -> None:
    rows = []
    for mention in extraction.mentions:
        result = match(mention.raw_name, clinics)
        status = "review" if result.status == "review" else "auto"
        rows.append((answer.response_id, mention.position, mention.raw_name, result.clinic_id,
                     status, extraction.extractor_version))  # fmt: skip
        summary.mentions += 1
        if result.status == "matched":
            summary.matched += 1
        elif result.status == "new":
            summary.new += 1
        else:
            summary.review += 1
    with conn.transaction(), conn.cursor() as cur:
        cur.execute(
            "select id, url from public.sources where response_id = %s", (answer.response_id,)
        )
        for source_id, url in cur.fetchall():
            cur.execute(
                "update public.sources set source_type = %s where id = %s",
                (classify(url, websites), source_id),
            )
        if rows:
            cur.executemany(
                "insert into public.mentions (response_id, position, raw_name, clinic_id, status, "
                "extractor_version) values (%s, %s, %s, %s, %s, %s)",
                rows,
            )
        cur.execute(
            "update public.responses set extracted_at = %s, extractor_version = %s, "
            "extraction_cost_usd = %s where id = %s",
            (
                datetime.now(UTC),
                extraction.extractor_version,
                extraction.cost_usd,
                answer.response_id,
            ),
        )
    summary.extracted += 1
    summary.cost_usd += extraction.cost_usd


def extract_run(
    conn: psycopg.Connection,
    run_id: int,
    extractor: Extractor,
    *,
    on_progress: Callable[[PendingAnswer, llm.Extraction | None, Exception | None], None]
    | None = None,
    concurrency: int = MAX_CONCURRENCY,
) -> ExtractionSummary:
    """Extract every pending answer of the run with `extractor(text, link_texts)`."""
    market_id = run_market(conn, run_id)
    clinics = load_market_clinics(conn, market_id)
    websites = market_websites(conn, market_id)
    answers = pending_answers(conn, run_id)
    summary = ExtractionSummary()
    lock = threading.Lock()

    def work(answer: PendingAnswer) -> None:
        try:
            links = llm.link_texts_from_raw(answer.surface, answer.raw)
            extraction = extractor(answer.text, links)
        except Exception as exc:  # recorded; the answer stays pending for the next run
            with lock:
                summary.failures.append(
                    f"respuesta {answer.response_id}: {type(exc).__name__}: {exc}"
                )
            if on_progress:
                on_progress(answer, None, exc)
            return
        with lock:
            save_extraction(conn, answer, extraction, clinics, websites, summary)
        if on_progress:
            on_progress(answer, extraction, None)

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        for future in as_completed([pool.submit(work, a) for a in answers]):
            future.result()
    return summary
