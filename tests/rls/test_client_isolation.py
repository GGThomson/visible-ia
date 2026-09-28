"""Client isolation (PRD §6 "each client sees only its data"), with two real signed-in users.

Two clinics A and B, each in its own market, with a user, a reviewed run, scores, sources,
a report and tasks. Every table and panel view is queried as A and as B through the REST API
with their own session: A never sees anything of B (and vice versa). Data is committed in dev
for the test (the users sign in over HTTP) and deleted afterwards.
"""

import uuid
from datetime import date

import httpx
import pytest

from visible_ia import db
from visible_ia.clientes import AuthAdmin, add_site, create_client, link_user
from visible_ia.config import get_settings
from visible_ia.informes.pdf import record_report
from visible_ia.mercados.clinicas import ClinicRow, import_clinics, list_market_clinics
from visible_ia.mercados.mercado import create_market, list_questions
from visible_ia.mercados.plantillas import read_templates, upsert_templates
from visible_ia.motor.corrida import Call, create_run, save_response
from visible_ia.motor.modelos import Citation, EngineResponse
from visible_ia.puntaje.indice import calculate

pytestmark = pytest.mark.integration

MARKETS = {"A": ("IMP", "San Isidro"), "B": ("IMP", "Surco")}  # used by no other test
TABLES = ("monthly_scores", "mentions", "sources", "reports", "tasks", "sites", "clients",
          "clinics", "markets", "runs", "app_users")  # fmt: skip
VIEWS = ("v_panel_ranking", "v_panel_evolution", "v_panel_sources")
PRIVATE = ("prospects", "payments", "heartbeats", "questions", "aliases", "clinic_markets")


def _cleanup(conn):
    with conn.cursor() as cur:
        cur.execute(
            "select id from public.markets where (category_code = %s and district = %s) "
            "or (category_code = %s and district = %s)",
            (*MARKETS["A"], *MARKETS["B"]),
        )
        markets = [r[0] for r in cur.fetchall()]
        if not markets:
            return
        cur.execute(
            "select clinic_id from public.clinic_markets where market_id = any(%s)", (markets,)
        )
        clinics = [r[0] for r in cur.fetchall()]
        cur.execute("delete from public.reports where clinic_id = any(%s)", (clinics,))
        cur.execute(
            "delete from public.clients where id in (select client_id from public.sites "
            "where market_id = any(%s))",
            (markets,),
        )
        cur.execute("delete from public.monthly_scores where market_id = any(%s)", (markets,))
        cur.execute("delete from public.runs where market_id = any(%s)", (markets,))
        cur.execute("delete from public.markets where id = any(%s)", (markets,))
        cur.execute("delete from public.clinics where id = any(%s)", (clinics,))


@pytest.fixture(scope="module")
def world():
    settings = get_settings()
    if settings.supabase_anon_key_dev is None:
        pytest.skip("Falta SUPABASE_ANON_KEY_DEV")
    url = settings.supabase_url_dev
    anon = settings.supabase_anon_key_dev.get_secret_value()
    admin = AuthAdmin(url, settings.supabase_service_role_key_dev.get_secret_value())
    conn = db.connect(settings, "dev", autocommit=True)
    upsert_templates(conn, read_templates())
    _cleanup(conn)
    users, ids = {}, {}
    try:
        for side, (category, district) in MARKETS.items():
            market = create_market(conn, category, district)
            import_clinics(
                conn,
                market,
                [
                    ClinicRow(
                        name=f"Clínica {side}",
                        district=district,
                        maps_url=f"https://maps.google.com/?cid=rls-{side}-1",
                    ),
                    ClinicRow(
                        name=f"Competidor {side}",
                        district=district,
                        maps_url=f"https://maps.google.com/?cid=rls-{side}-2",
                    ),
                ],  # fmt: skip
                date(2026, 9, 27),
            )
            clinics = {name: cid for cid, name, *_ in list_market_clinics(conn, market)}
            clinic = clinics[f"Clínica {side}"]
            client = create_client(conn, "clinic", f"Cliente RLS {side}")
            site, _ = add_site(conn, client, clinic, market)
            run = create_run(conn, market, surfaces=["chatgpt_api"], repetitions=1,
                             estimated_cost_usd=0, forced=False)  # fmt: skip
            q = list_questions(conn, market)[0]
            answer = EngineResponse(
                surface="chatgpt_api",
                provider="fake",
                text=f"Secreto de {side}: Clínica {side}",
                citations=[Citation(url=f"https://dominio-{side.lower()}.pe/")],
            )
            save_response(conn, run, Call(q.id, q.template_id, q.text, "chatgpt_api", 1), answer)
            with conn.cursor() as cur:
                cur.execute(
                    "insert into public.mentions (response_id, position, raw_name, clinic_id) "
                    "select id, 1, %s, %s from public.responses where run_id = %s",
                    (f"Clínica {side}", clinic, run),
                )
                cur.execute("update public.runs set status = 'reviewed' where id = %s", (run,))
                cur.execute(
                    "insert into public.tasks (site_id, code) values (%s, 'ficha_google')", (site,)
                )
            calculate(conn, run)
            record_report(conn, clinic, date(2026, 9, 1), f"informes/rls/{side}.pdf")
            email = f"rls-{side.lower()}-{uuid.uuid4().hex[:6]}@example.com"
            password = uuid.uuid4().hex
            created = admin.client.post(
                f"{url}/auth/v1/admin/users",
                json={"email": email, "password": password, "email_confirm": True},
                headers=admin.headers,
            )
            created.raise_for_status()
            user_id = created.json()["id"]
            users[side] = user_id
            link_user(conn, user_id, client)
            session = httpx.post(
                f"{url}/auth/v1/token", params={"grant_type": "password"},
                json={"email": email, "password": password}, headers={"apikey": anon},
            ).json()  # fmt: skip
            token = session["access_token"]
            ids[side] = {
                "market": market, "clinic": clinic, "competitor": clinics[f"Competidor {side}"],
                "client": client, "site": site, "run": run, "token": token, "user": user_id,
                "refresh": session["refresh_token"],
            }  # fmt: skip
        yield {"url": url, "anon": anon, "ids": ids}
    finally:
        for user_id in users.values():
            admin.delete_user(user_id)
        _cleanup(conn)
        conn.close()


def _get(world, side, path, **params):
    headers = {"apikey": world["anon"]}
    if side:
        headers["Authorization"] = f"Bearer {world['ids'][side]['token']}"
    return httpx.get(f"{world['url']}/rest/v1/{path}", params=params, headers=headers, timeout=20)


def _rows(world, side, path, **params):
    r = _get(world, side, path, select=params.pop("select", "*"), **params)
    assert r.status_code == 200, (path, r.status_code, r.text[:200])
    return r.json()


def _values(rows, *keys):
    return {row[k] for row in rows for k in keys if k in row and row[k] is not None}


@pytest.mark.parametrize("me, other", [("A", "B"), ("B", "A")])
def test_each_table_shows_only_my_data(world, me, other):
    mine, theirs = world["ids"][me], world["ids"][other]
    checks = {
        "monthly_scores": ("market_id", mine["market"], theirs["market"]),
        "markets": ("id", mine["market"], theirs["market"]),
        "runs": ("market_id", mine["market"], theirs["market"]),
        "sites": ("id", mine["site"], theirs["site"]),
        "clients": ("id", mine["client"], theirs["client"]),
        "tasks": ("site_id", mine["site"], theirs["site"]),
        "reports": ("clinic_id", mine["clinic"], theirs["clinic"]),
        "app_users": ("id", mine["user"], theirs["user"]),
    }
    for table in TABLES:
        rows = _rows(world, me, table)
        if table in checks:
            key, own, foreign = checks[table]
            seen = _values(rows, key)
            assert own in seen, (table, "no veo lo mío")
            assert foreign not in seen, (table, "veo lo del otro")
        if table == "clinics":
            assert mine["clinic"] in _values(rows, "id") and mine["competitor"] in _values(
                rows, "id"
            )
            assert theirs["clinic"] not in _values(rows, "id")
        if table in ("mentions", "sources"):
            text = str(rows)
            assert (
                rows and f"Clínica {other}" not in text and f"dominio-{other.lower()}" not in text
            )


@pytest.mark.parametrize("me, other", [("A", "B"), ("B", "A")])
def test_each_panel_view_shows_only_my_markets(world, me, other):
    mine, theirs = world["ids"][me], world["ids"][other]
    ranking = _rows(world, me, "v_panel_ranking")
    assert _values(ranking, "market_id") == {mine["market"]}
    assert {r["clinic_name"] for r in ranking} == {f"Clínica {me}", f"Competidor {me}"}
    assert [r["clinic_id"] for r in ranking if r["is_mine"]] == [mine["clinic"]]
    evolution = _rows(world, me, "v_panel_evolution")
    assert _values(evolution, "site_id") == {mine["site"]}
    sources = _rows(world, me, "v_panel_sources")
    assert _values(sources, "domain") == {f"dominio-{me.lower()}.pe"}
    assert theirs["market"] not in _values(sources, "market_id")


def test_raw_answer_text_is_never_readable(world):
    assert _get(world, "A", "responses", select="text").status_code in (401, 403)
    assert _get(world, "A", "responses", select="raw").status_code in (401, 403)
    ids = _rows(world, "A", "responses", select="id,run_id")
    assert _values(ids, "run_id") == {world["ids"]["A"]["run"]}


def test_private_tables_and_anon_see_nothing(world):
    for table in PRIVATE:
        r = _get(world, "A", table, select="*")
        assert r.status_code in (401, 403) or r.json() == [], table
    for path in (*TABLES, *VIEWS):
        r = _get(world, None, path, select="*")
        assert r.status_code in (401, 403) or r.json() == [], path


def test_a_clinic_marks_only_its_own_tasks(world):
    a, b = world["ids"]["A"], world["ids"]["B"]
    headers = {"apikey": world["anon"], "Authorization": f"Bearer {a['token']}",
               "Prefer": "return=representation"}  # fmt: skip
    own = httpx.patch(f"{world['url']}/rest/v1/tasks", params={"site_id": f"eq.{a['site']}"},
                      json={"status": "done"}, headers=headers)  # fmt: skip
    assert own.status_code == 200 and own.json()[0]["status"] == "done"
    foreign = httpx.patch(f"{world['url']}/rest/v1/tasks", params={"site_id": f"eq.{b['site']}"},
                          json={"status": "done"}, headers=headers)  # fmt: skip
    assert foreign.status_code == 200 and foreign.json() == []
    other_column = httpx.patch(
        f"{world['url']}/rest/v1/tasks",
        params={"site_id": f"eq.{a['site']}"},
        json={"code": "otra"},
        headers=headers,
    )
    assert other_column.status_code in (400, 401, 403)
    rows = _rows(world, "B", "tasks")
    assert [r["status"] for r in rows] == ["pending"]
