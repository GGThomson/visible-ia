from datetime import date
from decimal import Decimal

import pytest

from visible_ia.pagos import (
    DUE_SOON,
    OVERDUE,
    UP_TO_DATE,
    ClientStatus,
    PaymentError,
    net_of_igv,
    next_month,
    overdue_issue,
    parse_amount,
    status_for,
)

OLD_CLIENT = date(2026, 8, 20)
SEP, OCT, NOV = date(2026, 9, 1), date(2026, 10, 1), date(2026, 11, 1)


def status(today, paid, created=OLD_CLIENT):
    return status_for(today, created, set(paid), grace_days=5, notice_days=7)


@pytest.mark.parametrize(
    "today, paid, expected",
    [
        (date(2026, 10, 10), {OCT}, UP_TO_DATE),
        (date(2026, 10, 24), {OCT}, UP_TO_DATE),  # November starts in 8 days
        (date(2026, 10, 25), {OCT}, DUE_SOON),  # ... in 7 days
        (date(2026, 10, 25), {OCT, NOV}, UP_TO_DATE),  # paid in advance
        (date(2026, 10, 3), {SEP}, DUE_SOON),  # October unpaid, within grace
        (date(2026, 10, 6), {SEP}, DUE_SOON),  # last day of grace
        (date(2026, 10, 7), {SEP}, OVERDUE),
        (date(2026, 10, 7), set(), OVERDUE),
    ],
)
def test_status_by_date(today, paid, expected):
    assert status(today, paid)[0] == expected


def test_new_client_gets_grace_from_its_start_date():
    created = date(2026, 10, 20)
    assert status(date(2026, 10, 24), set(), created)[0] == DUE_SOON
    late, detail = status(date(2026, 10, 26), set(), created)
    assert late == OVERDUE and "25/10" in detail and "(1 d)" in detail


def test_details_name_the_month():
    assert status(date(2026, 10, 10), {OCT})[1] == "pagado hasta octubre 2026"
    assert status(date(2026, 10, 26), {OCT})[1] == "noviembre 2026 vence el 06/11"
    assert status(date(2026, 12, 3), {NOV})[1] == "diciembre 2026 sin pagar; vence el 06/12"


def test_next_month_wraps_the_year():
    assert next_month(date(2026, 12, 1)) == date(2027, 1, 1)


@pytest.mark.parametrize(
    "value, expected", [("349", "349"), ("349,50", "349.50"), (" 10.5 ", "10.5")]
)
def test_amounts_in_soles(value, expected):
    assert parse_amount(value) == Decimal(expected)


@pytest.mark.parametrize("value", ["0", "-5", "abc", "10.555", ""])
def test_bad_amounts_are_rejected(value):
    with pytest.raises(PaymentError):
        parse_amount(value)


def test_igv_is_configurable():
    assert net_of_igv(Decimal("349"), includes_igv=False) == Decimal("349")
    assert net_of_igv(Decimal("349"), includes_igv=True) == Decimal("295.76")


def test_issue_lists_only_overdue_clients():
    rows = [
        ClientStatus(1, "Clínica A", OVERDUE, "octubre 2026 sin pagar; venció el 06/10 (3 d)", SEP),
        ClientStatus(2, "Clínica B", DUE_SOON, "…", OCT),
        ClientStatus(3, "Clínica C", UP_TO_DATE, "…", OCT),
    ]
    title, body = overdue_issue(rows)
    assert title == "Pagos atrasados (1)"
    assert "Clínica A (cliente 1)" in body and "Clínica B" not in body
    assert overdue_issue(rows[1:]) is None
