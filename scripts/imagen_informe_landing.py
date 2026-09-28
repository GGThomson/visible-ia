"""Image of page 1 of the diagnostic report for the landing (C9b, "Así se ve tu diagnóstico").

Uses the real report template with FICTIONAL clinics (never a client's data) and saves
web/marca/informe-ejemplo.jpg. Run it again whenever the report design changes:

    python scripts/imagen_informe_landing.py
"""

from datetime import date
from pathlib import Path

from playwright.sync_api import sync_playwright

from visible_ia.informes.contexto import ClinicInfo, ExampleAnswer, ReportData, build_context
from visible_ia.informes.render import render_diagnostic
from visible_ia.puntaje.indice import RankingRow

OUT = Path(__file__).resolve().parents[1] / "web" / "marca" / "informe-ejemplo.jpg"
A4_WIDTH, A4_HEIGHT = 794, 1123  # CSS pixels at 96 dpi

LARCO, PARDO, BENAVIDES, ANGAMOS, TU = 1, 2, 3, 4, 5


def _row(cid, name, combined, low, high, chatgpt, google):
    return RankingRow(cid, name, combined, low, high, chatgpt, google, 2.0, 5.0)


RANKING = [
    _row(LARCO, "Clínica Sonrisa Larco", 50, 38, 62, 56.7, 43.3),
    _row(PARDO, "Centro Dental Pardo", 36.7, 26, 49, 26.7, 46.7),
    _row(BENAVIDES, "Implantes Benavides", 30, 20, 43, 36.7, 23.3),
    _row(ANGAMOS, "Odonto Angamos", 16.7, 9, 28, 20, 13.3),
    _row(TU, "Tu Clínica Dental", 10, 5, 20, 16.7, 3.3),
]

DATA = ReportData(
    clinic=ClinicInfo(TU, "Tu Clínica Dental", 4.9, 1135, date(2026, 9, 27), None),
    category="IMP",
    district="Miraflores",
    month=date(2026, 9, 1),
    ranking=RANKING,
    examples=[
        ExampleAnswer(
            "chatgpt_api",
            "¿Cuál es la mejor clínica de implantes dentales en Miraflores?",
            date(2026, 9, 26),
            "Te recomiendo Clínica Sonrisa Larco, con muy buenas reseñas. "
            "También Centro Dental Pardo e Implantes Benavides.",
            [(1, "Clínica Sonrisa Larco", LARCO), (2, "Centro Dental Pardo", PARDO),
             (3, "Implantes Benavides", BENAVIDES)],
        ),
        ExampleAnswer(
            "google_ai_mode",
            "¿Dónde me pongo implantes dentales en Miraflores?",
            date(2026, 9, 26),
            "Destacan Centro Dental Pardo y Clínica Sonrisa Larco.",
            [(1, "Centro Dental Pardo", PARDO), (2, "Clínica Sonrisa Larco", LARCO)],
        ),
    ],
    citations=[
        (1, "chatgpt_api", "sonrisalarco.pe", "own_website"),
        (1, "chatgpt_api", "doctoralia.pe", "doctoralia"),
        (2, "google_ai_mode", "google.com", "google_profile"),
    ],
    total_answers=60,
    detectable_diff=10.7,
    google_without_names=0,
    market_names={r.clinic_id: [r.name] for r in RANKING},
)


def main() -> None:
    html = render_diagnostic(build_context(DATA))
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": A4_WIDTH, "height": A4_HEIGHT},
                                device_scale_factor=2)
        page.set_content(html, wait_until="load")
        page.evaluate("document.fonts.ready")
        # Screen view of the print template: add the A4 margins the PDF gets from @page.
        page.add_style_tag(content="body { padding: 16mm 15mm; }")
        page.screenshot(path=str(OUT), type="jpeg", quality=82,
                        clip={"x": 0, "y": 0, "width": A4_WIDTH, "height": A4_HEIGHT})
        browser.close()
    print(f"{OUT} ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
