"""Manual samples from the consumer apps (HU-06): pasted by the operator, never in the index.

They live in a run of kind 'manual' (one per market and month) and only feed the extractor
and the monthly calibration (PRD §5.4). The phase-1 registry (registro.csv) can be imported
as well; it is the start of the extractor evaluation set (C4-T05).
"""

import csv
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import psycopg

from visible_ia.mercados.mercado import create_market, list_questions
from visible_ia.motor.corrida import Call, save_response
from visible_ia.motor.modelos import MANUAL_SURFACES, Citation, EngineResponse

PHASE1_QUESTIONS_CSV = Path(__file__).resolve().parents[3] / "data" / "fase1-preguntas.csv"
SURFACE_BY_AI = {
    "ChatGPT": "chatgpt_app_manual",
    "Gemini": "gemini_app_manual",
    "Google AI": "google_ai_mode_manual",
}
URL = re.compile(r"https?://\S+")


class ManualError(ValueError):
    pass


@dataclass
class ImportResult:
    by_surface: dict[str, int] = field(default_factory=dict)
    already_there: int = 0
    skipped: list[str] = field(default_factory=list)
    markets_created: list[str] = field(default_factory=list)

    @property
    def imported(self) -> int:
        return sum(self.by_surface.values())


def parse_sources(value: str) -> list[str]:
    """URLs found in a free-text field (one per line, spaces or commas)."""
    return [u.rstrip(".,;)") for u in URL.findall(value or "")]


def manual_run(conn: psycopg.Connection, market_id: int, taken_on: date) -> int:
    """The manual run of that market and month, created if needed."""
    month = taken_on.replace(day=1)
    with conn.transaction(), conn.cursor() as cur:
        cur.execute(
            "select id from public.runs where market_id = %s and month = %s and kind = 'manual' "
            "order by id limit 1",
            (market_id, month),
        )
        row = cur.fetchone()
        if row:
            return row[0]
        cur.execute(
            "insert into public.runs (market_id, month, kind, status, question_set_version, "
            "surfaces, repetitions) "
            "select id, %s, 'manual', 'complete', question_set_version, %s, 1 "
            "from public.markets where id = %s returning id",
            (month, list(MANUAL_SURFACES), market_id),
        )
        row = cur.fetchone()
    if row is None:
        raise ManualError(f"No existe el mercado {market_id}")
    return row[0]


def save_manual(
    conn: psycopg.Connection,
    market_id: int,
    template_id: str,
    surface: str,
    text: str,
    sources: list[str],
    *,
    taken_on: date,
    repetition: int | None = None,
    extra: dict[str, Any] | None = None,
) -> tuple[int, int, bool]:
    """Store one pasted answer. Returns (run_id, repetition, saved); saved is False when that
    repetition was already there (importing twice changes nothing)."""
    if surface not in MANUAL_SURFACES:
        raise ManualError(f"Superficie no válida: {surface} (usa {', '.join(MANUAL_SURFACES)})")
    text = (text or "").strip()
    if not text:
        raise ManualError("La respuesta está vacía")
    question = next(
        (q for q in list_questions(conn, market_id) if q.template_id == template_id), None
    )
    if question is None:
        raise ManualError(f"El mercado {market_id} no tiene la pregunta {template_id}")
    run_id = manual_run(conn, market_id, taken_on)
    if repetition is None:
        with conn.cursor() as cur:
            cur.execute(
                "select coalesce(max(repetition), 0) + 1 from public.responses "
                "where run_id = %s and question_id = %s and surface = %s",
                (run_id, question.id, surface),
            )
            (repetition,) = cur.fetchone()
    answer = EngineResponse(
        surface=surface,
        provider="manual",
        model=surface.removesuffix("_manual"),
        text=text,
        citations=[Citation(url=u) for u in sources],
        raw={"origen": "manual / app", "fecha": taken_on.isoformat(), **(extra or {})},
    )
    call = Call(question.id, template_id, question.text, surface, repetition)
    saved = save_response(conn, run_id, call, answer)
    return run_id, repetition, saved


def _phase1_questions(path: Path = PHASE1_QUESTIONS_CSV) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return {r["pregunta_id"]: r for r in csv.DictReader(f)}


def _market_id(
    conn: psycopg.Connection, category: str, district: str, create: bool, result: ImportResult
) -> int | None:
    with conn.cursor() as cur:
        cur.execute(
            "select id from public.markets where category_code = %s and district = %s",
            (category, district),
        )
        row = cur.fetchone()
    if row:
        return row[0]
    if not create:
        return None
    market_id = create_market(conn, category, district)
    with conn.transaction(), conn.cursor() as cur:
        # Created only to hold evaluation samples: an inactive market is never measured.
        cur.execute("update public.markets set active = false where id = %s", (market_id,))
    result.markets_created.append(f"{category} · {district}")
    return market_id


def import_registry(
    conn: psycopg.Connection,
    csv_path: Path,
    *,
    create_markets: bool = False,
    questions_csv: Path = PHASE1_QUESTIONS_CSV,
) -> ImportResult:
    """Import the phase-1 registry (fecha, ia, pregunta_id, repeticion, respuesta, ...)."""
    questions = _phase1_questions(questions_csv)
    result = ImportResult()
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    for n, row in enumerate(rows, start=2):
        label = f"fila {n} ({row.get('ia')} {row.get('pregunta_id')})"
        surface = SURFACE_BY_AI.get((row.get("ia") or "").strip())
        if surface is None:
            result.skipped.append(f"{label}: superficie no admitida")
            continue
        question = questions.get((row.get("pregunta_id") or "").strip())
        if question is None:
            result.skipped.append(f"{label}: pregunta sin equivalencia en {questions_csv.name}")
            continue
        template_id = question["plantilla"]
        market_id = _market_id(
            conn, template_id.split("-")[0], question["distrito"], create_markets, result
        )
        if market_id is None:
            result.skipped.append(
                f"{label}: no existe el mercado {template_id.split('-')[0]} · "
                f"{question['distrito']} (usa --crear-mercados)"
            )
            continue
        extra: dict[str, Any] = {
            "importado_de": csv_path.name,
            "pregunta_original": question["texto_original"],
            "pregunta_id_fase1": question["pregunta_id"],
            "modo": row.get("modo"),
            "busco_web": row.get("busco_web"),
            "notas": row.get("notas") or None,
        }
        if question["mercado_original"] != question["distrito"]:
            # The original asked about Lima: useful to evaluate the extractor, not to calibrate.
            extra["mercado_original"] = question["mercado_original"]
            extra["excluir_calibracion"] = True
        _, _, saved = save_manual(
            conn,
            market_id,
            template_id,
            surface,
            row["respuesta"],
            parse_sources(row.get("fuentes_citadas") or ""),
            taken_on=date.fromisoformat(row["fecha"].strip()),
            repetition=int(row.get("repeticion") or 1),
            extra=extra,
        )
        if saved:
            result.by_surface[surface] = result.by_surface.get(surface, 0) + 1
        else:
            result.already_there += 1
    return result


def split_pasted(text: str) -> tuple[str, list[str]]:
    """Separate a pasted answer from its 'fuente: <url>' lines; '#' lines are comments."""
    body: list[str] = []
    urls: list[str] = []
    for line in (text or "").splitlines():
        if line.startswith("#"):
            continue
        if line.lower().startswith("fuente:"):
            urls += parse_sources(line)
        else:
            body.append(line)
    return "\n".join(body).strip(), urls
