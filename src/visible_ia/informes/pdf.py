"""HTML -> PDF with Playwright (Chromium), and storage of the report (C6-T02).

First time on a machine: `uv run playwright install chromium`.
The PDF is saved in salida/ and, when asked, uploaded to the private Supabase Storage bucket
`informes` with the service_role key (never exposed to the browser).
"""

import re
import unicodedata
from datetime import date
from pathlib import Path

import httpx
import psycopg

OUTPUT_DIR = Path(__file__).resolve().parents[3] / "salida"
BUCKET = "informes"


class PdfError(RuntimeError):
    pass


def html_to_pdf(
    html: str, path: Path, header: str | None = None, footer: str | None = None
) -> Path:
    """Render with headless Chromium in A4, using the page's own @page size and margins.
    With `header`/`footer` (Chromium templates) they repeat on every page."""
    from playwright.sync_api import Error as PlaywrightError
    from playwright.sync_api import sync_playwright

    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_page()
                page.set_content(html, wait_until="load")
                page.evaluate("document.fonts.ready")  # web fonts (or their fallback) in place
                extra = {}
                if header or footer:
                    extra = {
                        "display_header_footer": True,
                        "header_template": header or "<span></span>",
                        "footer_template": footer or "<span></span>",
                    }
                page.pdf(
                    path=str(path),
                    format="A4",
                    print_background=True,
                    prefer_css_page_size=True,
                    **extra,
                )
            finally:
                browser.close()
    except PlaywrightError as exc:
        if "Executable doesn't exist" in str(exc):
            raise PdfError("Falta Chromium: ejecuta 'uv run playwright install chromium'") from None
        raise
    return path


def slug(text: str) -> str:
    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", plain).strip("-")[:60]


def report_filename(clinic_name: str, month: date) -> str:
    return f"diagnostico-{slug(clinic_name)}-{month:%Y-%m}.pdf"


def upload(
    path: Path,
    storage_path: str,
    *,
    supabase_url: str,
    service_role_key: str,
    client: httpx.Client | None = None,
) -> str:
    """Upload (or replace) a PDF in the private bucket. Returns 'informes/<storage_path>'."""
    own = client is None
    client = client or httpx.Client(timeout=60)
    headers = {
        "apikey": service_role_key,
        "Authorization": f"Bearer {service_role_key}",
        "Content-Type": "application/pdf",
        "x-upsert": "true",
    }
    try:
        response = client.post(
            f"{supabase_url}/storage/v1/object/{BUCKET}/{storage_path}",
            content=path.read_bytes(),
            headers=headers,
        )
    finally:
        if own:
            client.close()
    if response.status_code >= 300:
        raise PdfError(f"Storage respondió {response.status_code}: {response.text[:200]}")
    return f"{BUCKET}/{storage_path}"


def record_report(
    conn: psycopg.Connection, clinic_id: int, month: date, pdf_path: str, brand: str = "visible-ia"
) -> int:
    with conn.transaction(), conn.cursor() as cur:
        cur.execute(
            "insert into public.reports (kind, clinic_id, month, pdf_path, brand) "
            "values ('diagnostic', %s, %s, %s, %s) returning id",
            (clinic_id, month, pdf_path, brand),
        )
        return cur.fetchone()[0]


def ensure_bucket(
    *, supabase_url: str, service_role_key: str, client: httpx.Client | None = None
) -> bool:
    """Create the private `informes` bucket if missing. Returns True when it was created."""
    own = client is None
    client = client or httpx.Client(timeout=30)
    headers = {"apikey": service_role_key, "Authorization": f"Bearer {service_role_key}"}
    try:
        found = client.get(f"{supabase_url}/storage/v1/bucket/{BUCKET}", headers=headers)
        if found.status_code == 200:
            if found.json().get("public"):
                raise PdfError(f"El bucket {BUCKET} es público: debe ser privado")
            return False
        created = client.post(
            f"{supabase_url}/storage/v1/bucket",
            json={"id": BUCKET, "name": BUCKET, "public": False},
            headers=headers,
        )
    finally:
        if own:
            client.close()
    if created.status_code >= 300:
        raise PdfError(f"No se pudo crear el bucket: {created.status_code} {created.text[:200]}")
    return True


def delete_object(
    storage_path: str,
    *,
    supabase_url: str,
    service_role_key: str,
    client: httpx.Client | None = None,
) -> None:
    own = client is None
    client = client or httpx.Client(timeout=30)
    headers = {"apikey": service_role_key, "Authorization": f"Bearer {service_role_key}"}
    try:
        client.delete(f"{supabase_url}/storage/v1/object/{BUCKET}/{storage_path}", headers=headers)
    finally:
        if own:
            client.close()
