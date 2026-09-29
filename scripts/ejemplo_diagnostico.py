"""Example of the free diagnostic (C-008 + redesign), from the fictional DEMO in dev.

Reuses the demo of scripts/capturas_producto.py (Implantes · San Isidro, fictional clinics),
generates the diagnostic exactly like `visible-ia informe diagnostico` (gpt-5-nano picks the
literal reasons, ~US$0.0001, recorded in dev's monthly budget), saves the PDF and one image per
page in salida/, and deletes the demo. Never prod.

    python scripts/ejemplo_diagnostico.py   # -> salida/ejemplo-diagnostico.pdf + -pagina-N.png
"""

import base64
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
import capturas_producto as demo  # noqa: E402

from visible_ia import db  # noqa: E402
from visible_ia.cli import _add_reasons  # noqa: E402
from visible_ia.config import get_settings  # noqa: E402
from visible_ia.informes.contexto import build_context, load_brand, load_report_data  # noqa: E402
from visible_ia.informes.pdf import OUTPUT_DIR, html_to_pdf  # noqa: E402
from visible_ia.informes.render import diagnostic_frame, render_diagnostic  # noqa: E402

PDFJS = "https://cdn.jsdelivr.net/npm/pdfjs-dist@4.10.38/build"


def pdf_pages(pdf: bytes, scale: float = 2.0) -> list[bytes]:
    """Every page of a PDF as PNG, rendered by pdf.js inside Chromium (no extra dependency)."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content("<html><body></body></html>")
        uris = page.evaluate(
            f"""async ([data, scale]) => {{
                const pdfjs = await import('{PDFJS}/pdf.min.mjs');
                pdfjs.GlobalWorkerOptions.workerSrc = '{PDFJS}/pdf.worker.min.mjs';
                const bytes = Uint8Array.from(atob(data), c => c.charCodeAt(0));
                const doc = await pdfjs.getDocument({{data: bytes}}).promise;
                const out = [];
                for (let i = 1; i <= doc.numPages; i++) {{
                    const pg = await doc.getPage(i);
                    const vp = pg.getViewport({{scale}});
                    const c = document.createElement('canvas');
                    c.width = vp.width; c.height = vp.height;
                    await pg.render({{canvasContext: c.getContext('2d'), viewport: vp}}).promise;
                    out.push(c.toDataURL('image/png'));
                }}
                return out;
            }}""",
            [base64.b64encode(pdf).decode(), scale],
        )
        browser.close()
    return [base64.b64decode(u.split(",", 1)[1]) for u in uris]


def build_example(conn, settings) -> tuple[bytes, dict]:
    """Demo in dev -> (PDF bytes, context). The caller deletes the demo."""
    demo._cleanup(conn)
    built = demo._build(conn)
    with conn.cursor() as cur:
        cur.execute("select clinic_id from public.sites where id = %s", (built["site"],))
        (clinic_id,) = cur.fetchone()
    data = load_report_data(conn, clinic_id, built["market"], demo.MONTHS[-1])
    _add_reasons(conn, data, settings, market_id=built["market"], use_model=True)
    context = build_context(data, load_brand())
    html = render_diagnostic(context)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "ejemplo-diagnostico.html").write_text(html, encoding="utf-8")
    pdf = OUTPUT_DIR / "ejemplo-diagnostico.pdf"
    html_to_pdf(html, pdf, *diagnostic_frame(context))
    return pdf.read_bytes(), context


def main() -> None:
    settings = get_settings()
    conn = db.connect(settings, "dev", autocommit=True)
    try:
        pdf, _ = build_example(conn, settings)
    finally:
        demo._cleanup(conn)
        conn.close()
        print("demo borrado de dev")
    for old in OUTPUT_DIR.glob("ejemplo-diagnostico-pagina-*.png"):
        old.unlink()
    pages = pdf_pages(pdf, scale=1.5)
    for i, png in enumerate(pages, start=1):
        (OUTPUT_DIR / f"ejemplo-diagnostico-pagina-{i}.png").write_bytes(png)
    print(f"PDF: {OUTPUT_DIR / 'ejemplo-diagnostico.pdf'} · {len(pages)} páginas")


if __name__ == "__main__":
    main()
