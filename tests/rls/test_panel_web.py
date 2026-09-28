"""The clinic panel end to end (C7-T03/T04) with a real browser and a real dev session.

Opening the panel with the session in the URL fragment is exactly what a magic link does.
Reuses the two-clinic world of the isolation test. Also a smoke test of the panel views'
structure. Needs Chromium; skipped without it.
"""

import json
import shutil

import pytest
from test_client_isolation import world  # noqa: F401 (pytest fixture)

from visible_ia import db
from visible_ia.config import get_settings
from visible_ia.informes.pdf import OUTPUT_DIR

pytestmark = pytest.mark.integration

WEB = OUTPUT_DIR.parent / "web"
VIEW_COLUMNS = {
    "v_panel_ranking": {
        "market_id",
        "month",
        "clinic_id",
        "clinic_name",
        "is_mine",
        "combined",
        "ci_low",
        "ci_high",
        "change",
        "window3_index",
        "detectable_diff",
        "chatgpt",
        "google",
    },  # fmt: skip
    "v_panel_evolution": {
        "site_id",
        "market_id",
        "month",
        "surface",
        "presence_index",
        "ci_low",
        "ci_high",
        "change",
        "window3_index",
        "n_responses",
    },  # fmt: skip
    "v_panel_sources": {"market_id", "month", "domain", "source_type", "answers"},
}


def test_panel_views_have_the_columns_the_page_uses():
    with db.connect(get_settings(), "dev") as conn, conn.cursor() as cur:
        for view, columns in VIEW_COLUMNS.items():
            cur.execute(
                "select column_name from information_schema.columns "
                "where table_schema = 'public' and table_name = %s",
                (view,),
            )
            assert columns <= {r[0] for r in cur.fetchall()}, view


@pytest.fixture
def site(world, tmp_path):  # noqa: F811
    copy = tmp_path / "web"
    shutil.copytree(WEB, copy)
    config = {"supabaseUrl": world["url"], "anonKey": world["anon"]}
    (copy / "config.js").write_text(f"window.VISIBLE_IA_CONFIG = {json.dumps(config)};")
    return copy


@pytest.fixture
def page():
    playwright = pytest.importorskip("playwright.sync_api")
    with playwright.sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception as exc:
            pytest.skip(str(exc))
        context = browser.new_context(viewport={"width": 390, "height": 844})
        yield context.new_page()
        browser.close()


def test_without_session_the_panel_sends_to_login(site, page):
    page.goto((site / "panel" / "index.html").as_uri())
    page.wait_for_url("**/login.html", timeout=15000)
    assert "Entra a tu panel" in page.inner_text("h1")


def test_magic_link_session_opens_only_my_panel(world, site, page):  # noqa: F811
    a = world["ids"]["A"]
    fragment = (
        f"#access_token={a['token']}&refresh_token={a['refresh']}"
        "&expires_in=3600&token_type=bearer&type=magiclink"
    )
    page.goto((site / "panel" / "index.html").as_uri() + fragment)
    page.wait_for_selector("#contenido:not([hidden])", timeout=20000)
    assert page.inner_text("#titulo") == "Clínica A"
    text = page.inner_text("#contenido")
    assert "Competidor A" in text and "Clínica B" not in text and "Competidor B" not in text
    assert "dominio-a.pe" in text and "dominio-b.pe" not in text
    assert "%" in page.inner_text("#combinado")
    assert "Primer mes" in page.inner_text("#cambio")
    assert page.inner_text("#google") == "—"  # no Google answers in this test market

    box = page.locator("#tareas input[type=checkbox]").first
    box.check()
    page.wait_for_timeout(1500)
    with db.connect(get_settings(), "dev") as conn, conn.cursor() as cur:
        cur.execute("select status from public.tasks where site_id = %s", (a["site"],))
        assert cur.fetchone()[0] == "done"
        cur.execute(
            "select status from public.tasks where site_id = %s", (world["ids"]["B"]["site"],)
        )
        assert cur.fetchone()[0] == "pending"

    page.click("#salir")
    page.wait_for_url("**/login.html", timeout=15000)
