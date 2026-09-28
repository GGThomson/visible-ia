"""Clients, sites and users against dev. The invitation uses the link-only mode (no e-mail
is sent) and the test deletes the auth users it creates."""

import uuid
from datetime import date

import pytest

from visible_ia import db
from visible_ia.clientes import (
    AuthAdmin,
    ClientError,
    add_site,
    create_client,
    find_user,
    invite_user,
)
from visible_ia.config import get_settings
from visible_ia.mercados.clinicas import ClinicRow, import_clinics, list_market_clinics
from visible_ia.mercados.mercado import create_market

pytestmark = pytest.mark.integration


@pytest.fixture
def market_clinics(tx):
    market = create_market(tx, "DER", "Surco")
    import_clinics(
        tx,
        market,
        [
            ClinicRow(
                name="Sede Uno", district="Surco", maps_url="https://maps.google.com/?cid=t-c-1"
            ),
            ClinicRow(
                name="Sede Dos", district="Surco", maps_url="https://maps.google.com/?cid=t-c-2"
            ),
        ],
        date(2026, 9, 27),
    )
    return market, [cid for cid, *_ in list_market_clinics(tx, market)]


def test_a_clinic_client_can_have_several_sites(tx, market_clinics):
    market, (one, two) = market_clinics
    client = create_client(tx, "clinic", "Grupo Dental Prueba", email="Dueño@Prueba.PE")
    s1, created1 = add_site(tx, client, one, market)
    s2, created2 = add_site(tx, client, two, market)
    again, created3 = add_site(tx, client, one, market)
    assert created1 and created2 and not created3
    assert again == s1 and s1 != s2
    with tx.cursor() as cur:
        cur.execute("select contact_email from public.clients where id = %s", (client,))
        assert cur.fetchone()[0] == "dueño@prueba.pe"


def test_site_must_be_a_clinic_of_that_market(tx, market_clinics):
    market, (one, _) = market_clinics
    client = create_client(tx, "clinic", "Clínica X")
    with pytest.raises(ClientError, match="no está en el mercado"):
        add_site(tx, client, one, market + 999_999)
    with pytest.raises(ClientError, match="no es una agencia"):
        create_client(tx, "clinic", "Hija", agency_id=client)


def test_inviting_twice_does_not_duplicate_the_user():
    """Uses an autocommit connection like the CLI: an open test transaction would hold the
    new user's row and block Supabase Auth on the second call."""
    settings = get_settings()
    auth = AuthAdmin(
        settings.supabase_url_dev, settings.supabase_service_role_key_dev.get_secret_value()
    )
    email = f"prueba-{uuid.uuid4().hex[:8]}@example.com"
    site = "https://visible-ia.pages.dev"
    conn = db.connect(settings, "dev", autocommit=True)
    client = create_client(conn, "clinic", "Clínica Invitada (prueba)")
    other = create_client(conn, "clinic", "Otra clínica (prueba)")
    first = None
    try:
        first = invite_user(conn, auth, client, email, site_url=site, link_only=True)
        assert first.created and first.link and first.link.startswith("http")
        second = invite_user(conn, auth, client, email.upper(), site_url=site, link_only=True)
        assert not second.created and second.user_id == first.user_id
        assert find_user(conn, email) == first.user_id
        with conn.cursor() as cur:
            cur.execute(
                "select count(*), max(role) from public.app_users where id = %s", (first.user_id,)
            )
            assert cur.fetchone() == (1, "clinic")
        with pytest.raises(ClientError, match="ya pertenece"):
            invite_user(conn, auth, other, email, site_url=site, link_only=True)
    finally:
        if first:
            auth.delete_user(first.user_id)  # cascades to app_users
        with conn.cursor() as cur:
            cur.execute("delete from public.clients where id = any(%s)", ([client, other],))
        conn.close()
