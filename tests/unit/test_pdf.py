"""PDF of the diagnostic report. Needs Chromium (`uv run playwright install chromium`);
skipped where it is not installed (e.g. the CI)."""

import time

import pytest
from test_informe_diagnostico import _data  # same folder (pytest rootdir-relative import)

from visible_ia.informes.contexto import build_context
from visible_ia.informes.pdf import PdfError, html_to_pdf, report_filename
from visible_ia.informes.render import render_diagnostic


def _pdf(tmp_path, data):
    try:
        start = time.monotonic()
        path = html_to_pdf(render_diagnostic(build_context(data)), tmp_path / "informe.pdf")
        return path, time.monotonic() - start
    except PdfError as exc:
        pytest.skip(str(exc))


def test_pdf_is_short_and_small(tmp_path):
    from pypdf import PdfReader

    path, seconds = _pdf(tmp_path, _data())
    reader = PdfReader(path)
    # Redesign (Director, 28/09): about 6 pages plus the annex. PRD HU-14 still says <= 4:
    # pending the Director's OK to update it.
    assert 1 <= len(reader.pages) <= 8
    assert path.stat().st_size < 2 * 1024 * 1024
    assert seconds < 60
    text = " ".join(page.extract_text() for page in reader.pages)
    assert "Clínica Odontologists" in text and "No garantizamos un puesto #1" in text


def test_filename_is_safe():
    from datetime import date

    name = report_filename("Dr. Aldo | Implantes Dentales y Rehabilitación Oral", date(2026, 9, 1))
    assert name == "diagnostico-dr-aldo-implantes-dentales-y-rehabilitacion-oral-2026-09.pdf"
