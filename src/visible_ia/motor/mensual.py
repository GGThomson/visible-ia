"""Monthly run of the active markets, with the Director's OK (C8-T01, decided 27/09).

Day 1 the scheduled job only *estimates* (no money spent) and opens the issue "Corridas de
<mes>" with the cost per market. The Director approves by launching the workflow by hand in
"correr" mode: then every active market is run (or resumed if a run of the month was cut),
its answers are extracted, and the issue "Revisar corridas de <mes>" lists what to review.
A month over the budget or the SerpApi quota is not run: the issue says so.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date

import psycopg

from visible_ia.extractor.extraccion import ESTIMATED_COST_PER_ANSWER, extract_run, pending_answers
from visible_ia.motor.corrida import all_calls, create_run, execute, pending_calls, plan_of
from visible_ia.motor.presupuesto import BudgetCheck, MonthUsage, RunPlan, check, month_bounds

SURFACES = ["chatgpt_api", "google_ai_mode"]
REPETITIONS = 3
MONTHS = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
          "setiembre", "octubre", "noviembre", "diciembre")  # fmt: skip
ESTIMATE_PREFIX = "Corridas de"
REVIEW_PREFIX = "Revisar corridas de"


@dataclass
class MarketPlan:
    market_id: int
    name: str
    run_id: int | None  # existing run of the month (to resume), if any
    run_status: str | None
    plan: RunPlan
    answers_to_extract: int

    @property
    def calls(self) -> int:
        return self.plan.chatgpt_calls + self.plan.serpapi_calls


@dataclass
class MonthPlan:
    month: date
    markets: list[MarketPlan]
    budget: BudgetCheck
    extraction_usd: float

    @property
    def total(self) -> RunPlan:
        return RunPlan(
            sum(m.plan.chatgpt_calls for m in self.markets),
            sum(m.plan.serpapi_calls for m in self.markets),
        )

    @property
    def estimated_usd(self) -> float:
        return round(self.budget.estimated_cost_usd + self.extraction_usd, 2)

    @property
    def fits(self) -> bool:
        spent = self.budget.spent_usd + self.estimated_usd
        return self.budget.ok and spent <= self.budget.budget_usd + 1e-9


@dataclass
class MarketResult:
    name: str
    run_id: int | None
    status: str
    answers: int = 0
    total: int = 0
    cost_usd: float = 0.0
    mentions: int = 0
    to_review: int = 0
    new: int = 0
    failures: list[str] = field(default_factory=list)


def month_name(month: date) -> str:
    return f"{MONTHS[month.month - 1]} de {month.year}"


def active_markets(conn: psycopg.Connection) -> list[tuple[int, str]]:
    names = {"IMP": "Implantología", "EDE": "Estética dental", "MES": "Medicina estética",
             "DER": "Dermatología"}  # fmt: skip
    with conn.cursor() as cur:
        cur.execute(
            "select id, category_code, district from public.markets where active order by id"
        )
        return [
            (mid, f"{names.get(cat, cat)} · {district}") for mid, cat, district in cur.fetchall()
        ]


def _run_of_month(conn: psycopg.Connection, market_id: int, month: date) -> tuple[int, str] | None:
    with conn.cursor() as cur:
        cur.execute(
            "select id, status from public.runs "
            "where market_id = %s and month = %s and kind = 'api' "
            "order by id desc limit 1",
            (market_id, month),
        )
        return cur.fetchone()


def plan_month(
    conn: psycopg.Connection,
    usage: MonthUsage,
    *,
    budget_usd: float,
    serpapi_quota: int,
    now=None,
) -> MonthPlan:
    """What the month still needs, per active market, and whether it fits the budget."""
    from visible_ia.mercados.mercado import list_questions

    month, _ = month_bounds(now)
    markets = []
    for market_id, name in active_markets(conn):
        existing = _run_of_month(conn, market_id, month)
        if existing:
            run_id, status = existing
            plan = plan_of(pending_calls(conn, run_id))
            to_extract = (
                len(pending_answers(conn, run_id)) + plan.chatgpt_calls + plan.serpapi_calls
            )
        else:
            run_id, status = None, None
            plan = RunPlan.for_market(len(list_questions(conn, market_id)), REPETITIONS, SURFACES)
            to_extract = plan.chatgpt_calls + plan.serpapi_calls
        markets.append(MarketPlan(market_id, name, run_id, status, plan, to_extract))
    total = RunPlan(
        sum(m.plan.chatgpt_calls for m in markets), sum(m.plan.serpapi_calls for m in markets)
    )
    budget = check(total, usage, budget_usd=budget_usd, serpapi_quota=serpapi_quota)
    extraction = round(sum(m.answers_to_extract for m in markets) * ESTIMATED_COST_PER_ANSWER, 2)
    return MonthPlan(month, markets, budget, extraction)


def run_month(
    conn: psycopg.Connection,
    month_plan: MonthPlan,
    clients: dict[str, Callable],
    extractor: Callable,
    *,
    now=None,
) -> list[MarketResult]:
    """Launch or resume each market of the plan, then extract its answers. Never forced."""
    if not month_plan.fits:
        raise ValueError("El mes supera el presupuesto o la cuota: no se corre")
    results = []
    for m in month_plan.markets:
        run_id = m.run_id
        if run_id is None:
            run_id = create_run(
                conn,
                m.market_id,
                surfaces=SURFACES,
                repetitions=REPETITIONS,
                estimated_cost_usd=round(
                    m.plan.chatgpt_calls * month_plan.budget.cost_per_call_usd, 4
                ),
                forced=False,
                now=now,
            )
        result = MarketResult(m.name, run_id, "")
        if m.calls:
            summary = execute(conn, run_id, clients)
            result.status, result.failures = (
                summary.status,
                [
                    f"{f['surface']} {f['template_id']} rep {f['repetition']}: {f['error']}"
                    for f in summary.failures
                ],
            )
        extracted = extract_run(conn, run_id, extractor)
        result.failures += extracted.failures
        with conn.cursor() as cur:
            cur.execute(
                "select status, (select count(*) from public.responses where run_id = r.id), "
                "(select coalesce(sum(cost_usd), 0) from public.responses where run_id = r.id) "
                "from public.runs r where r.id = %s",
                (run_id,),
            )
            result.status, result.answers, cost = cur.fetchone()
            result.cost_usd = float(cost)
        result.total = len(all_calls(conn, run_id))
        result.mentions, result.to_review, result.new = (
            extracted.mentions,
            extracted.review,
            extracted.new,
        )
        results.append(result)
    return results


# --- issue texts ---------------------------------------------------------------------------


def _run_label(m: MarketPlan) -> str:
    if m.run_id is None:
        return "nueva"
    if not m.calls and not m.answers_to_extract:
        return f"corrida {m.run_id} ya hecha"
    return f"retomar corrida {m.run_id}"


def estimate_issue(mp: MonthPlan) -> tuple[str, str]:
    name = month_name(mp.month)
    title = f"{ESTIMATE_PREFIX} {name} · esperando tu OK"
    rows = "\n".join(
        f"| {m.name} | {m.plan.chatgpt_calls} | {m.plan.serpapi_calls} | {_run_label(m)} |"
        for m in mp.markets
    )
    b = mp.budget
    verdict = (
        "✅ Entra en el presupuesto y en la cuota."
        if mp.fits
        else "⛔ **No entra**: " + "; ".join(b.problems or ["el extractor superaría el tope"])
    )
    body = (
        f"Corrida mensual de **{name}** para {len(mp.markets)} "
        f"{'mercado activo' if len(mp.markets) == 1 else 'mercados activos'}. "
        "Todavía **no se gastó nada**.\n\n"
        "| Mercado | Llamadas ChatGPT | Búsquedas Google | Corrida |\n|---|---|---|---|\n"
        f"{rows}\n\n"
        f"- **Costo estimado:** ≈ US${mp.estimated_usd:.2f} "
        f"(ChatGPT ≈ US${b.estimated_cost_usd:.2f} + extractor ≤ US${mp.extraction_usd:.2f})\n"
        f"- **Gastado este mes:** US${b.spent_usd:.2f} de US${b.budget_usd:.2f}\n"
        f"- **SerpApi:** {mp.total.serpapi_calls} búsquedas; usadas {b.serpapi_used} de "
        f"{b.serpapi_quota}\n\n{verdict}\n\n"
        "**Para aprobar:** GitHub → Actions → *Corrida mensual* → *Run workflow* → modo "
        "`correr`. Si se corta, vuelve a lanzarlo en modo `correr`: retoma lo que falta."
    )
    return title, body


def review_issue(month: date, results: list[MarketResult]) -> tuple[str, str]:
    name = month_name(month)
    lines = []
    for r in results:
        lines.append(
            f"| {r.name} | {r.run_id} | {r.status} | {r.answers}/{r.total} | US${r.cost_usd:.2f} | "
            f"{r.new} nuevas · {r.to_review} dudosas |"
        )
    failures = [f"- {r.name}: {f}" for r in results for f in r.failures]
    body = (
        f"Corridas de **{name}** hechas. Falta tu revisión antes de calcular el puntaje.\n\n"
        "| Mercado | Corrida | Estado | Respuestas | Costo | Menciones |\n"
        "|---|---|---|---|---|---|\n"
        + "\n".join(lines)
        + "\n\n**Pasos** (en tu PC, con el entorno activado), por cada corrida:\n\n"
        "```\nvisible-ia revisar corrida <corrida> --env prod\n"
        "visible-ia revisar cerrar <corrida> --env prod\n"
        "visible-ia puntaje calcular <corrida> --env prod\n```\n"
        + (
            "\n**Fallas** (vuelve a lanzar el workflow en modo `correr` para reintentarlas):\n"
            + "\n".join(failures)
            if failures
            else ""
        )
    )
    return f"{REVIEW_PREFIX} {name}", body
