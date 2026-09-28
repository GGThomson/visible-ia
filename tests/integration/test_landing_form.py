"""The landing form end to end: a real browser fills it and the row lands in dev (C6-T03).

Needs Chromium (`uv run playwright install chromium`) and the dev anon key; the page is
served from a temporary copy of web/ with a config.js pointing to dev.
"""

import json
import shutil
import uuid

import pytest

from visible_ia import db
from visible_ia.config import get_settings
from visible_ia.informes.pdf import OUTPUT_DIR

pytestmark = pytest.mark.integration

WEB = OUTPUT_DIR.parent / "web"


@pytest.fixture
def page_url(tmp_path):
    settings = get_settings()
    if settings.supabase_anon_key_dev is None:
        pytest.skip("Falta SUPABASE_ANON_KEY_DEV")
    site = tmp_path / "web"
    shutil.copytree(WEB, site)
    config = {
        "supabaseUrl": settings.supabase_url_dev,
        "anonKey": settings.supabase_anon_key_dev.get_secret_value(),
    }
    (site / "config.js").write_text(
        f"window.VISIBLE_IA_CONFIG = {json.dumps(config)};", encoding="utf-8"
    )
    return (site / "index.html").as_uri() + "?utm_source=prueba&utm_campaign=c6"


@pytest.fixture
def browser_page():
    playwright = pytest.importorskip("playwright.sync_api")
    with playwright.sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except Exception as exc:  # Chromium not installed
            pytest.skip(str(exc))
        yield browser.new_page()
        browser.close()


@pytest.fixture
def tag():
    value = f"TEST-FORM-{uuid.uuid4().hex[:8]}"
    yield value
    with db.connect(get_settings(), "dev") as conn, conn.cursor() as cur:
        cur.execute("delete from public.prospects where name like %s", (f"{value}%",))


def _fill(page, tag, consent=True):
    page.fill("input[name=name]", tag)
    page.fill("input[name=clinic_name]", "Clínica de prueba")
    page.select_option("select[name=category_code]", "IMP")
    page.select_option("select[name=district]", "Miraflores")
    page.fill("input[name=contact]", "+51 999 999 999")
    if consent:
        page.check("input[name=consent]")


def _rows(tag):
    with db.connect(get_settings(), "dev") as conn, conn.cursor() as cur:
        cur.execute(
            "select clinic_name, category_code, district, utm, consent from public.prospects "
            "where name = %s",
            (tag,),
        )
        return cur.fetchall()


def test_form_sends_the_request_with_utm(browser_page, page_url, tag):
    browser_page.goto(page_url)
    _fill(browser_page, tag)
    browser_page.click("#enviar")
    browser_page.wait_for_selector("#resultado:not([hidden])", timeout=15000)
    [(clinic, category, district, utm, consent)] = _rows(tag)
    assert (clinic, category, district, consent) == ("Clínica de prueba", "IMP", "Miraflores", True)
    assert utm["utm_source"] == "prueba" and utm["utm_campaign"] == "c6"


def test_without_consent_nothing_is_sent(browser_page, page_url, tag):
    browser_page.goto(page_url)
    _fill(browser_page, tag, consent=False)
    browser_page.click("#enviar")
    browser_page.wait_for_selector("#error:not([hidden])")
    assert "autorización" in browser_page.inner_text("#error")
    assert _rows(tag) == []


def test_honeypot_pretends_success_and_sends_nothing(browser_page, page_url, tag):
    browser_page.goto(page_url)
    _fill(browser_page, tag)
    browser_page.evaluate("document.querySelector('input[name=website]').value = 'spam'")
    browser_page.click("#enviar")
    browser_page.wait_for_selector("#resultado:not([hidden])")
    assert _rows(tag) == []
