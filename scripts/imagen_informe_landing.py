"""Landing image of the free diagnostic: its new cover page (redesign 28/09/2026).

Builds the diagnostic from the fictional DEMO in dev (scripts/ejemplo_diagnostico.py, never a
client's data), renders page 1 at double resolution and saves web/marca/producto-diagnostico
.webp and .jpg (under 200 KB each), used by the "Así se ve tu diagnóstico" section and the
"Diagnóstico" tab. Run it again whenever the report design changes:

    python scripts/imagen_informe_landing.py
"""

import sys
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
import capturas_producto as demo  # noqa: E402
import ejemplo_diagnostico as ejemplo  # noqa: E402

from visible_ia import db  # noqa: E402
from visible_ia.config import get_settings  # noqa: E402


def main() -> None:
    settings = get_settings()
    conn = db.connect(settings, "dev", autocommit=True)
    try:
        pdf, _ = ejemplo.build_example(conn, settings)
    finally:
        demo._cleanup(conn)
        conn.close()
        print("demo borrado de dev")
    cover = ejemplo.pdf_pages(pdf, scale=2.0)[0]
    with tempfile.TemporaryDirectory() as tmp:
        png = Path(tmp) / "portada.png"
        png.write_bytes(cover)
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_content("<html><body></body></html>")
            demo._encode(page, png, "producto-diagnostico", 1190)
            browser.close()


if __name__ == "__main__":
    main()
