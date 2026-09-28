"""Payments and client statuses against dev (inside a rolled-back transaction)."""

from datetime import date
from decimal import Decimal

import pytest

from visible_ia.clientes import create_client
from visible_ia.pagos import (
    DUE_SOON,
    OVERDUE,
    UP_TO_DATE,
    PaymentError,
    client_statuses,
    month_total,
    register_payment,
)

pytestmark = pytest.mark.integration

OCT = date(2026, 10, 1)


def _statuses(conn, today):
    rows = client_statuses(conn, today, grace_days=5, notice_days=7)
    return {s.name: s for s in rows if s.name.startswith("Pago test")}


def test_register_and_status(tx):
    with tx.cursor() as cur:
        cur.execute("update public.clients set status = 'paused' where status = 'active'")
    paid = create_client(tx, "clinic", "Pago test al día")
    unpaid = create_client(tx, "clinic", "Pago test atrasado")
    agency = create_client(tx, "agency", "Pago test agencia")
    child = create_client(tx, "clinic", "Pago test clínica de agencia", agency_id=agency)
    with tx.cursor() as cur:  # all of them started in August
        cur.execute(
            "update public.clients set created_at = '2026-08-15' where id = any(%s)",
            ([paid, unpaid, agency, child],),
        )

    payment_id, repeated = register_payment(
        tx, paid, Decimal("349"), "yape", OCT, paid_on=date(2026, 10, 2), reference=" op-1 "
    )
    assert payment_id and not repeated
    _, repeated = register_payment(tx, paid, Decimal("1"), "link", OCT, paid_on=date(2026, 10, 2))
    assert repeated
    with tx.cursor() as cur:
        cur.execute("select method, reference from public.payments where id = %s", (payment_id,))
        assert cur.fetchone() == ("yape", "op-1")

    statuses = _statuses(tx, date(2026, 10, 10))
    assert statuses["Pago test al día"].status == UP_TO_DATE
    assert statuses["Pago test atrasado"].status == OVERDUE
    assert statuses["Pago test agencia"].status == OVERDUE
    assert "Pago test clínica de agencia" not in statuses  # billed to its agency
    assert list(statuses)[0] != "Pago test al día"  # overdue first
    assert _statuses(tx, date(2026, 10, 28))["Pago test al día"].status == DUE_SOON
    assert month_total(tx, OCT) == Decimal("350")


def test_bad_payments_are_rejected(tx):
    agency = create_client(tx, "agency", "Pago test agencia")
    child = create_client(tx, "clinic", "Pago test hija", agency_id=agency)
    with pytest.raises(PaymentError, match="agencia"):
        register_payment(tx, child, Decimal("349"), "yape", OCT, paid_on=OCT)
    with pytest.raises(PaymentError, match="Medio"):
        register_payment(tx, agency, Decimal("349"), "efectivo", OCT, paid_on=OCT)
    with pytest.raises(PaymentError, match="No existe"):
        register_payment(tx, 10**9, Decimal("349"), "yape", OCT, paid_on=OCT)
