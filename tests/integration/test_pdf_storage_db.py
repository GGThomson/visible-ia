"""Upload a PDF to the private `informes` bucket in dev and record the report."""

from datetime import date

import httpx
import pytest

from visible_ia.config import get_settings
from visible_ia.informes.pdf import delete_object, ensure_bucket, record_report, upload
from visible_ia.mercados.clinicas import ClinicRow, import_clinics, list_market_clinics
from visible_ia.mercados.mercado import create_market

pytestmark = pytest.mark.integration


def test_upload_is_private_and_recorded(tx, tmp_path):
    settings = get_settings()
    url = settings.supabase_url_dev
    key = settings.supabase_service_role_key_dev.get_secret_value()
    ensure_bucket(supabase_url=url, service_role_key=key)

    pdf = tmp_path / "prueba.pdf"
    pdf.write_bytes(b"%PDF-1.4\n% visible-ia test\n")
    storage_path = "pruebas/prueba-automatica.pdf"
    try:
        stored = upload(pdf, storage_path, supabase_url=url, service_role_key=key)
        assert stored == f"informes/{storage_path}"
        anonymous = httpx.get(f"{url}/storage/v1/object/public/informes/{storage_path}")
        assert anonymous.status_code >= 400  # private bucket: no public URL
    finally:
        delete_object(storage_path, supabase_url=url, service_role_key=key)

    market = create_market(tx, "DER", "Surco")
    import_clinics(
        tx,
        market,
        [
            ClinicRow(
                name="Clínica PDF", district="Surco", maps_url="https://maps.google.com/?cid=t-pdf"
            )
        ],
        date(2026, 9, 27),
    )
    clinic_id = list_market_clinics(tx, market)[0][0]
    report_id = record_report(tx, clinic_id, date(2026, 9, 1), stored)
    with tx.cursor() as cur:
        cur.execute("select kind, pdf_path, brand from public.reports where id = %s", (report_id,))
        assert cur.fetchone() == ("diagnostic", stored, "visible-ia")
