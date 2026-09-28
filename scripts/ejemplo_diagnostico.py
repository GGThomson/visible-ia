"""Example of the deeper free diagnostic (C-008), from the fictional DEMO in dev.

Reuses the demo of scripts/capturas_producto.py (Implantes · San Isidro, fictional clinics),
generates the diagnostic with gpt-5-nano picking the literal reasons (~US$0.001, recorded in
dev's monthly budget), saves the PDF and images of each page in salida/, and deletes the demo.

    python scripts/imagen_informe_landing.py   # (unrelated) landing image
    python scripts/ejemplo_diagnostico.py       # -> salida/ejemplo-diagnostico*.{pdf,png}
"""

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
from visible_ia.informes.render import render_diagnostic  # noqa: E402

A4 = (794, 1123)


def main() -> None:
    settings = get_settings()
    conn = db.connect(settings, "dev", autocommit=True)
    try:
        demo._cleanup(conn)
        built = demo._build(conn)
        with conn.cursor() as cur:
            cur.execute("select clinic_id from public.sites where id = %s", (built["site"],))
            (clinic_id,) = cur.fetchone()
        data = load_report_data(conn, clinic_id, built["market"], demo.MONTHS[-1])
        _add_reasons(conn, data, settings, market_id=built["market"], use_model=True)
        html = render_diagnostic(build_context(data, load_brand()))
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        pdf = OUTPUT_DIR / "ejemplo-diagnostico.pdf"
        (OUTPUT_DIR / "ejemplo-diagnostico.html").write_text(html, encoding="utf-8")
        html_to_pdf(html, pdf)
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": A4[0], "height": A4[1]},
                                    device_scale_factor=1.5)  # fmt: skip
            page.emulate_media(media="print")
            page.set_content(html, wait_until="load")
            page.evaluate("document.fonts.ready")
            page.add_style_tag(content="body { padding: 16mm 15mm; }")
            for name in ("razones", "preguntas", "faltantes"):
                loc = page.locator(f'[data-seccion="{name}"]')
                if loc.count():
                    loc.screenshot(path=str(OUTPUT_DIR / f"ejemplo-diagnostico-{name}.png"))
            browser.close()
        pages = pdf.read_bytes().count(b"/Type /Page") - pdf.read_bytes().count(b"/Type /Pages")
        print(f"PDF: {pdf} · {pages} páginas")
    finally:
        demo._cleanup(conn)
        conn.close()
        print("demo borrado de dev")


if __name__ == "__main__":
    main()
