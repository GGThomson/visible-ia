"""RLS of the landing form, tested with the public anon key against dev (C6-T03).

The anon key is in the web page: whatever it can do, anyone can do. It must only be able
to insert a new prospect with consent, and read nothing.
"""

import uuid

import httpx
import pytest

from visible_ia import db
from visible_ia.config import get_settings

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def api():
    settings = get_settings()
    anon = settings.supabase_anon_key_dev
    if not settings.supabase_url_dev or anon is None:
        pytest.skip("Faltan SUPABASE_URL_DEV o SUPABASE_ANON_KEY_DEV")
    key = anon.get_secret_value()
    headers = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    with httpx.Client(
        base_url=f"{settings.supabase_url_dev}/rest/v1", headers=headers, timeout=20
    ) as c:
        yield c


@pytest.fixture
def marker():
    """Unique name for this test's rows; they are deleted with the service role afterwards."""
    tag = f"TEST-RLS-{uuid.uuid4().hex[:8]}"
    yield tag
    with db.connect(get_settings(), "dev") as conn, conn.cursor() as cur:
        cur.execute("delete from public.prospects where name like %s", (f"{tag}%",))


def _prospect(tag, **extra):
    return {
        "name": tag,
        "clinic_name": "Clínica de prueba RLS",
        "district": "Miraflores",
        "category_code": "IMP",
        "contact": "+51 999 999 999",
        "utm": {"utm_source": "test"},
        "consent": True,
        **extra,
    }


def _insert(api, row):
    return api.post("/prospects", json=row, headers={"Prefer": "return=minimal"})


def test_anon_can_insert_a_request_with_consent(api, marker):
    assert _insert(api, _prospect(marker)).status_code == 201
    with db.connect(get_settings(), "dev") as conn, conn.cursor() as cur:
        cur.execute("select status, seen, utm from public.prospects where name = %s", (marker,))
        assert cur.fetchone() == ("new", False, {"utm_source": "test"})


@pytest.mark.parametrize(
    "extra",
    [
        {"consent": False},
        {"status": "client"},
        {"seen": True},
        {"do_not_contact": True},
        {"contact": "x"},
        {"consent_at": "2020-01-01T00:00:00Z"},
    ],
)
def test_anon_cannot_skip_consent_or_set_internal_fields(api, marker, extra):
    assert _insert(api, _prospect(marker, **extra)).status_code in (400, 401, 403)


def test_anon_cannot_read_prospects_or_any_table(api, marker):
    assert _insert(api, _prospect(marker)).status_code == 201
    response = api.get("/prospects", params={"select": "*"})
    assert response.status_code in (401, 403) or response.json() == []
    for table in ("markets", "clinics", "responses", "clients", "payments", "reports"):
        r = api.get(f"/{table}", params={"select": "*", "limit": "1"})
        assert r.status_code in (401, 403) or r.json() == [], table


def test_anon_cannot_update_or_delete(api, marker):
    assert _insert(api, _prospect(marker)).status_code == 201
    api.patch("/prospects", params={"name": f"eq.{marker}"}, json={"status": "client"})
    api.delete("/prospects", params={"name": f"eq.{marker}"})
    with db.connect(get_settings(), "dev") as conn, conn.cursor() as cur:
        cur.execute("select status from public.prospects where name = %s", (marker,))
        assert cur.fetchall() == [("new",)]
