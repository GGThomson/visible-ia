"""Budget and quota guard (HU-05): a run that would exceed them does not start.

The OpenAI budget is in US$ per calendar month (America/Lima). The SerpApi free plan is a
monthly quota of searches. Overriding the guard needs the operator to type SI, and the run
records it (runs.forced).
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

import psycopg

from visible_ia.motor.tarifas import OpenAIRates, openai_rates

LIMA = ZoneInfo("America/Lima")


@dataclass(frozen=True)
class RunPlan:
    """How many calls a run still has to make, per surface."""

    chatgpt_calls: int = 0
    serpapi_calls: int = 0

    @classmethod
    def for_market(cls, questions: int, repetitions: int, surfaces: list[str]) -> "RunPlan":
        calls = questions * repetitions
        return cls(
            chatgpt_calls=calls if "chatgpt_api" in surfaces else 0,
            serpapi_calls=calls if "google_ai_mode" in surfaces else 0,
        )


@dataclass(frozen=True)
class MonthUsage:
    spent_usd: float
    serpapi_used: int


@dataclass(frozen=True)
class BudgetCheck:
    plan: RunPlan
    cost_per_call_usd: float
    estimated_cost_usd: float
    spent_usd: float
    budget_usd: float
    serpapi_used: int
    serpapi_quota: int
    problems: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.problems

    def explain(self) -> str:
        p = self.plan
        lines = [
            f"ChatGPT (API): {p.chatgpt_calls} llamadas × ≈ US${self.cost_per_call_usd:.3f} "
            f"= ≈ US${self.estimated_cost_usd:.2f}",
            f"  Gastado este mes: US${self.spent_usd:.2f} de US${self.budget_usd:.2f} "
            f"→ quedaría en US${self.spent_usd + self.estimated_cost_usd:.2f}",
            f"Google Modo IA (SerpApi): {p.serpapi_calls} búsquedas",
            f"  Usadas este mes: {self.serpapi_used} de {self.serpapi_quota} "
            f"→ quedarían {self.serpapi_quota - self.serpapi_used - p.serpapi_calls}",
        ]
        if self.problems:
            lines.append("BLOQUEADA:")
            lines += [f"  - {problem}" for problem in self.problems]
        return "\n".join(lines)


def check(
    plan: RunPlan,
    usage: MonthUsage,
    *,
    budget_usd: float,
    serpapi_quota: int,
    rates: OpenAIRates | None = None,
) -> BudgetCheck:
    """Decide whether a run fits the monthly budget and quota (reaching the cap exactly is ok)."""
    per_call = (rates or openai_rates()).estimated_call_cost()
    estimated = round(plan.chatgpt_calls * per_call, 4)
    problems = []
    if usage.spent_usd + estimated > budget_usd + 1e-9:
        problems.append(
            f"superaría el presupuesto de OpenAI: US${usage.spent_usd:.2f} gastados + "
            f"≈ US${estimated:.2f} de esta corrida > US${budget_usd:.2f} (MONTHLY_BUDGET_USD)"
        )
    if usage.serpapi_used + plan.serpapi_calls > serpapi_quota:
        problems.append(
            f"superaría la cuota de SerpApi: {usage.serpapi_used} usadas + "
            f"{plan.serpapi_calls} de esta corrida > {serpapi_quota} (SERPAPI_MONTHLY_QUOTA)"
        )
    return BudgetCheck(
        plan=plan,
        cost_per_call_usd=per_call,
        estimated_cost_usd=estimated,
        spent_usd=usage.spent_usd,
        budget_usd=budget_usd,
        serpapi_used=usage.serpapi_used,
        serpapi_quota=serpapi_quota,
        problems=problems,
    )


def month_bounds(now: datetime | None = None) -> tuple[date, date]:
    """First day of the current Lima month and of the next one."""
    today = (now or datetime.now(UTC)).astimezone(LIMA).date()
    start = today.replace(day=1)
    end = date(start.year + start.month // 12, start.month % 12 + 1, 1)
    return start, end


def month_usage(
    conn: psycopg.Connection,
    now: datetime | None = None,
    *,
    serpapi_account_used: int | None = None,
) -> MonthUsage:
    """Money spent on OpenAI and SerpApi searches used this Lima month, from the database.

    The SerpApi account counter (when given) wins if it is higher: it also counts searches
    made outside a run, such as the live tests.
    """
    start, end = month_bounds(now)
    with conn.cursor() as cur:
        cur.execute(
            "select coalesce(sum(r.cost_usd) filter (where r.surface = 'chatgpt_api'), 0), "
            "       count(*) filter (where r.surface = 'google_ai_mode') "
            "from public.responses r "
            "where (r.created_at at time zone 'America/Lima') >= %s "
            "  and (r.created_at at time zone 'America/Lima') < %s",
            (start, end),
        )
        spent, serpapi_used = cur.fetchone()
    return MonthUsage(float(spent), max(int(serpapi_used), serpapi_account_used or 0))


def authorize(
    result: BudgetCheck,
    *,
    force: bool,
    prompt: Callable[[str], str],
    echo: Callable[[str], None] = print,
) -> bool:
    """True when the run may start; it is forced when this returns True and not `result.ok`.

    A blocked run only starts with --forzar AND the operator typing SI in the terminal.
    """
    echo(result.explain())
    if result.ok:
        return True
    if not force:
        echo("No se ejecuta. Para forzarla: --forzar (pide confirmación).")
        return False
    answer = prompt("Vas a superar el presupuesto o la cuota. Escribe SI para forzar la corrida")
    if answer.strip() != "SI":
        echo("Cancelado.")
        return False
    echo("Corrida forzada: quedará registrada como forzada.")
    return True
