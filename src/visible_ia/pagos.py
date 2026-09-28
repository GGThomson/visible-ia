"""Manual payments and the "up to date" status of each client (C9-T01, HU-23).

Clients pay in advance, one payment per month of service (the period, stored as its 1st day).
A period is due on its 1st day, or on the day the client was created if that is later, plus
a few days of grace. For today's date:

- overdue ("atrasado"): the current period is unpaid and its due date has passed;
- due soon ("vence pronto"): the current period is unpaid but still within the grace days,
  or it is paid and the next one is unpaid and starts within the notice days;
- up to date ("al día"): otherwise.

Clinics that belong to an agency are billed to the agency, so only clients without a parent
agency are listed. Amounts are what the client paid, in soles; whether they include IGV is a
setting, because the tax regime is still pending (estrategia).
"""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo

import psycopg

LIMA = ZoneInfo("America/Lima")
IGV_RATE = Decimal("0.18")
METHODS = {"link": "link", "yape": "yape", "transferencia": "transfer"}
UP_TO_DATE, DUE_SOON, OVERDUE = "al día", "vence pronto", "atrasado"
ISSUE_PREFIX = "Pagos atrasados"


class PaymentError(ValueError):
    pass


@dataclass(frozen=True)
class ClientStatus:
    client_id: int
    name: str
    status: str
    detail: str
    last_period: date | None


def today_lima() -> date:
    return datetime.now(LIMA).date()


def next_month(month: date) -> date:
    return date(month.year + month.month // 12, month.month % 12 + 1, 1)


def parse_amount(value: str) -> Decimal:
    try:
        amount = Decimal(value.replace(",", ".").strip())
    except InvalidOperation:
        raise PaymentError(f"Monto no válido: {value}") from None
    if amount <= 0 or amount != amount.quantize(Decimal("0.01")):
        raise PaymentError(f"Monto no válido: {value} (en soles, con hasta 2 decimales)")
    return amount


def net_of_igv(amount: Decimal, *, includes_igv: bool) -> Decimal:
    """What stays after IGV: the whole amount if prices do not include it."""
    if not includes_igv:
        return amount
    return (amount / (1 + IGV_RATE)).quantize(Decimal("0.01"))


def month_name(month: date) -> str:
    names = ("enero febrero marzo abril mayo junio julio agosto setiembre octubre noviembre "
             "diciembre").split()  # fmt: skip
    return f"{names[month.month - 1]} {month.year}"


def status_for(
    today: date, created: date, paid: set[date], *, grace_days: int, notice_days: int
) -> tuple[str, str]:
    """(status, detail) of one client from the periods it has paid."""
    current = today.replace(day=1)
    upcoming = next_month(current)
    if current not in paid:
        due = max(current, created) + timedelta(days=grace_days)
        if today > due:
            late = (today - due).days
            return OVERDUE, f"{month_name(current)} sin pagar; venció el {due:%d/%m} ({late} d)"
        return DUE_SOON, f"{month_name(current)} sin pagar; vence el {due:%d/%m}"
    if upcoming not in paid and (upcoming - today).days <= notice_days:
        due = upcoming + timedelta(days=grace_days)
        return DUE_SOON, f"{month_name(upcoming)} vence el {due:%d/%m}"
    return UP_TO_DATE, f"pagado hasta {month_name(max(paid))}"


# --- database ------------------------------------------------------------------------------


def register_payment(
    conn: psycopg.Connection,
    client_id: int,
    amount: Decimal,
    method: str,
    period: date,
    *,
    paid_on: date,
    reference: str | None = None,
) -> tuple[int, bool]:
    """Record a payment. Returns (payment id, whether that period already had a payment)."""
    if method not in METHODS:
        raise PaymentError(f"Medio no válido: {method} (usa {', '.join(METHODS)})")
    if period.day != 1:
        raise PaymentError("El periodo es un mes (AAAA-MM)")
    with conn.transaction(), conn.cursor() as cur:
        cur.execute("select parent_agency_id from public.clients where id = %s", (client_id,))
        row = cur.fetchone()
        if row is None:
            raise PaymentError(f"No existe el cliente {client_id}")
        if row[0] is not None:
            raise PaymentError(
                f"El cliente {client_id} es de la agencia {row[0]}: registra el pago a la agencia"
            )
        cur.execute(
            "select 1 from public.payments where client_id = %s and period = %s",
            (client_id, period),
        )
        repeated = cur.fetchone() is not None
        reference = (reference or "").strip() or None
        cur.execute(
            "insert into public.payments (client_id, period, amount_pen, method, paid_on, "
            "reference) values (%s, %s, %s, %s, %s, %s) returning id",
            (client_id, period, amount, METHODS[method], paid_on, reference),
        )
        return cur.fetchone()[0], repeated


def client_statuses(
    conn: psycopg.Connection, today: date, *, grace_days: int, notice_days: int
) -> list[ClientStatus]:
    """Status of every active client billed directly, overdue first."""
    with conn.cursor() as cur:
        cur.execute(
            "select c.id, c.name, (c.created_at at time zone 'America/Lima')::date, "
            "coalesce(array_agg(p.period) filter (where p.period is not null), '{}') "
            "from public.clients c left join public.payments p on p.client_id = c.id "
            "where c.status = 'active' and c.parent_agency_id is null "
            "group by c.id order by c.name"
        )
        rows = cur.fetchall()
    out = []
    for client_id, name, created, periods in rows:
        paid = set(periods)
        status, detail = status_for(
            today, created, paid, grace_days=grace_days, notice_days=notice_days
        )
        out.append(ClientStatus(client_id, name, status, detail, max(paid) if paid else None))
    order = {OVERDUE: 0, DUE_SOON: 1, UP_TO_DATE: 2}
    return sorted(out, key=lambda s: order[s.status])


def month_total(conn: psycopg.Connection, month: date) -> Decimal:
    """What was paid during a calendar month (by payment date)."""
    with conn.cursor() as cur:
        cur.execute(
            "select coalesce(sum(amount_pen), 0) from public.payments "
            "where paid_on >= %s and paid_on < %s",
            (month, next_month(month)),
        )
        return cur.fetchone()[0]


def overdue_issue(statuses: list[ClientStatus]) -> tuple[str, str] | None:
    """Title and body of the daily notice, or None when nobody is overdue."""
    late = [s for s in statuses if s.status == OVERDUE]
    if not late:
        return None
    lines = "\n".join(f"- {s.name} (cliente {s.client_id}): {s.detail}" for s in late)
    body = (
        f"{len(late)} clientes con el pago atrasado:\n\n{lines}\n\n"
        "Cuando paguen, regístralo y el aviso se cierra solo al día siguiente:\n\n"
        "```\nvisible-ia pago registrar <cliente> --monto <S/> --medio yape --periodo <AAAA-MM> "
        "--env prod\nvisible-ia pagos estado --env prod\n```"
    )
    return f"{ISSUE_PREFIX} ({len(late)})", body
