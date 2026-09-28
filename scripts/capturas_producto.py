"""Product screenshots for the landing ("Qué recibes cada mes", C9b), from a DEMO in dev.

Builds a demo market in DEV only (Implantes · San Isidro) with fictional clinics, three months
of fake measurements, a client with its site, checklist, AI-patient counts and a panel user;
takes the screenshots; and deletes everything it created. Never prod, never real clinics.

    python scripts/capturas_producto.py            # images (WebP + JPG) into web/marca/
    python scripts/capturas_producto.py --video    # also tries a short panel video (WebM)

Images are converted with Chromium itself (canvas -> WebP/JPEG): no extra dependency.
"""

import base64
import json
import shutil
import sys
import tempfile
import uuid
from datetime import date, datetime
from pathlib import Path

import httpx
from playwright.sync_api import sync_playwright

from visible_ia import db
from visible_ia.atribucion import kit_context, save_count
from visible_ia.checklist import generate
from visible_ia.clientes import PANEL_PATH, AuthAdmin, add_site, create_client, link_user
from visible_ia.config import get_settings
from visible_ia.extractor.fuentes import classify
from visible_ia.informes.contexto import load_brand
from visible_ia.informes.mensual import build_monthly_context, load_monthly_data
from visible_ia.informes.render import render_kit, render_monthly
from visible_ia.mercados.clinicas import ClinicRow, import_clinics, list_market_clinics
from visible_ia.mercados.mercado import create_market, list_questions
from visible_ia.mercados.plantillas import read_templates, upsert_templates
from visible_ia.motor.corrida import Call, create_run, save_response
from visible_ia.motor.modelos import Citation, EngineResponse
from visible_ia.puntaje.indice import calculate

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
OUT = WEB / "marca"
# Real product screenshots are no longer on the landing (illustrations since 29/09): kept in
# salida/ for sales decks and WhatsApp.
SHOTS = ROOT / "salida" / "capturas-producto"
CATEGORY, DISTRICT = "IMP", "San Isidro"  # dev's IMP Miraflores holds phase-1 real samples
MONTHS = [date(2026, 7, 1), date(2026, 8, 1), date(2026, 9, 1)]
ME = "Tu Clínica Dental"
# name, rating, reviews, website, answers (of 60) that name it in Jul / Aug / Sep
CLINICS = [
    ("Clínica Sonrisa Larco", 4.8, 640, "https://sonrisalarco.pe/", (28, 30, 30)),
    ("Centro Dental Pardo", 4.7, 410, "https://dentalpardo.pe/", (20, 22, 22)),
    ("Implantes Benavides", 4.6, 380, "https://implantesbenavides.pe/", (18, 18, 18)),
    ("Odonto Angamos", 4.5, 220, "https://odontoangamos.pe/", (12, 10, 10)),
    ("Dental Camino Real", 4.4, 150, None, (6, 8, 8)),
    (ME, 4.9, 1135, "https://tuclinicadental.pe/", (3, 6, 15)),
]
MAX_KB = 200
# Fictional reasons and pages, so the deeper diagnostic (C-008) has something to quote.
REASONS = {
    "Clínica Sonrisa Larco": [
        "destaca por sus más de 600 reseñas y por usar implantes guiados por computadora",
        "tiene especialistas en implantología y da garantía escrita de sus tratamientos",
    ],
    "Centro Dental Pardo": [
        "es muy valorada por su trato cercano y por explicar los precios desde la primera cita",
        "ofrece la evaluación con tomografía incluida",
    ],
    "Implantes Benavides": [
        "cuenta con más de 15 años de experiencia en implantes y carga inmediata",
        "recibe buenas opiniones en Doctoralia por su puntualidad",
    ],
    "Odonto Angamos": ["atiende también los sábados, con horarios amplios"],
    "Dental Camino Real": ["es una opción económica en San Isidro"],
    ME: ["tiene excelentes reseñas en Google Maps"],
}
PAGES = {
    "Clínica Sonrisa Larco": ["https://www.doctoralia.pe/clinicas/clinica-sonrisa-larco",
                              "https://cuantomecuesta.com/implantes-dentales-san-isidro"],
    "Centro Dental Pardo": ["https://www.doctoralia.pe/clinicas/centro-dental-pardo",
                            "https://cuantomecuesta.com/implantes-dentales-san-isidro"],
    "Implantes Benavides": ["https://www.instagram.com/implantesbenavides/",
                            "https://elcomercio.pe/salud/implantes-dentales-guia-lima"],
    "Odonto Angamos": ["https://www.google.com/maps/place/Odonto+Angamos"],
    "Dental Camino Real": [],
    ME: ["https://www.google.com/maps/place/Tu+Clinica+Dental"],
}  # fmt: skip


def _cleanup(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "select id from public.markets where category_code = %s and district = %s",
            (CATEGORY, DISTRICT),
        )
        markets = [r[0] for r in cur.fetchall()]
        if not markets:
            return
        cur.execute(
            "select clinic_id from public.clinic_markets where market_id = any(%s)", (markets,)
        )
        clinics = [r[0] for r in cur.fetchall()]
        cur.execute(
            "select u.id from public.app_users u join public.sites s on s.client_id = u.client_id "
            "where s.market_id = any(%s)",
            (markets,),
        )
        users = [str(r[0]) for r in cur.fetchall()]
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
    settings = get_settings()
    admin = AuthAdmin(
        settings.supabase_url_dev, settings.supabase_service_role_key_dev.get_secret_value()
    )
    for user in users:
        admin.delete_user(user)


def _build(conn) -> dict:
    upsert_templates(conn, read_templates())
    market = create_market(conn, CATEGORY, DISTRICT)
    rows = [
        ClinicRow(name=n, district=DISTRICT, maps_url=f"https://maps.google.com/?cid=demo-{i}",
                  rating=r, review_count=c, website=w)
        for i, (n, r, c, w, _) in enumerate(CLINICS)
    ]  # fmt: skip
    import_clinics(conn, market, rows, date(2026, 9, 27))
    ids = {name: cid for cid, name, *_ in list_market_clinics(conn, market)}
    questions = list_questions(conn, market)
    for m_index, month in enumerate(MONTHS):
        run = create_run(conn, market, surfaces=["chatgpt_api", "google_ai_mode"], repetitions=3,
                         estimated_cost_usd=0, forced=False,
                         now=datetime(month.year, month.month, 15))  # fmt: skip
        answer_index = 0
        for surface in ("chatgpt_api", "google_ai_mode"):
            for q in questions:
                for rep in (1, 2, 3):
                    i = answer_index
                    named = [
                        name for k, (name, *_, counts) in enumerate(CLINICS)
                        if (i * 7 + k * 11 + m_index * 5) % 60 < counts[m_index]
                    ]  # fmt: skip
                    cites = []
                    for name, _, _, w, _ in CLINICS:
                        if name in named:
                            cites += ([w] if w and i % 2 == 0 else []) + PAGES[name][: 1 + i % 2]
                    lines = [
                        f"{k}. {name}: {REASONS[name][(i + k) % len(REASONS[name])]}."
                        for k, name in enumerate(named, start=1)
                    ]
                    if "Centro Dental Pardo" in named and i % 4 == 0:
                        lines.append("En Centro Dental Pardo atiende la Dra. Lucía Rojas Vega.")
                    text = (
                        "Te recomiendo estas clínicas de implantes en San Isidro:\n"
                        + "\n".join(lines)
                        if named
                        else "Sin nombres."
                    )
                    save_response(
                        conn, run, Call(q.id, q.template_id, q.text, surface, rep),
                        EngineResponse(surface=surface, provider="demo", text=text,
                                       citations=[Citation(url=u) for u in cites]),
                    )  # fmt: skip
                    answer_index += 1
        with conn.cursor() as cur:
            cur.execute(
                "select id, text from public.responses where run_id = %s order by id", (run,)
            )
            for response_id, text in cur.fetchall():
                for pos, name in enumerate(
                    [n for n, *_ in CLINICS if n in text and text != "Sin nombres."], start=1
                ):
                    cur.execute(
                        "insert into public.mentions (response_id, position, raw_name, clinic_id) "
                        "values (%s, %s, %s, %s)",
                        (response_id, pos, name, ids[name]),
                    )
            cur.execute("update public.runs set status = 'reviewed' where id = %s", (run,))
            cur.execute(
                "select s.id, s.url from public.sources s join public.responses r "
                "on r.id = s.response_id where r.run_id = %s",
                (run,),
            )
            websites = {w for _, _, _, w, _ in CLINICS if w}
            for source_id, url in cur.fetchall():
                cur.execute(
                    "update public.sources set source_type = %s where id = %s",
                    (classify(url, websites), source_id),
                )
        calculate(conn, run)
    client = create_client(conn, "clinic", "Demo capturas (dev)")
    site, _ = add_site(conn, client, ids[ME], market)
    generate(conn, site)
    with conn.cursor() as cur:
        cur.execute(
            "update public.tasks set status = 'done' where id = "
            "(select id from public.tasks where site_id = %s order by priority, id limit 1)",
            (site,),
        )
    save_count(conn, site, MONTHS[1], 1)
    save_count(conn, site, MONTHS[2], 3)
    return {"market": market, "client": client, "site": site}


def _session(conn, client: int) -> dict:
    settings = get_settings()
    url, anon = settings.supabase_url_dev, settings.supabase_anon_key_dev.get_secret_value()
    admin = AuthAdmin(url, settings.supabase_service_role_key_dev.get_secret_value())
    email, password = f"demo-capturas-{uuid.uuid4().hex[:6]}@example.com", uuid.uuid4().hex
    created = admin.client.post(
        f"{url}/auth/v1/admin/users",
        json={"email": email, "password": password, "email_confirm": True},
        headers=admin.headers,
    )
    created.raise_for_status()
    link_user(conn, created.json()["id"], client)
    tokens = httpx.post(
        f"{url}/auth/v1/token", params={"grant_type": "password"},
        json={"email": email, "password": password}, headers={"apikey": anon},
    ).json()  # fmt: skip
    return {"url": url, "anon": anon, "access": tokens["access_token"],
            "refresh": tokens["refresh_token"]}  # fmt: skip


def _encode(page, png: Path, name: str, width: int, out: Path = OUT) -> None:
    """PNG -> <out>/<name>.webp and .jpg (under MAX_KB), resized to `width`, in Chromium."""
    data = "data:image/png;base64," + base64.b64encode(png.read_bytes()).decode()
    for fmt, ext in (("image/webp", "webp"), ("image/jpeg", "jpg")):
        for quality in (0.9, 0.86, 0.82, 0.76, 0.7, 0.62):
            uri = page.evaluate(
                """async ([src, w, fmt, q]) => {
                    const img = new Image(); img.src = src; await img.decode();
                    const c = document.createElement('canvas');
                    c.width = w; c.height = Math.round(img.height * w / img.width);
                    const x = c.getContext('2d'); x.fillStyle = '#fff'; x.fillRect(0, 0, c.width, c.height);
                    x.drawImage(img, 0, 0, c.width, c.height);
                    return c.toDataURL(fmt, q);
                }""",
                [data, width, fmt, quality],
            )
            raw = base64.b64decode(uri.split(",", 1)[1])
            if len(raw) <= MAX_KB * 1024:
                break
        (out / f"{name}.{ext}").write_bytes(raw)
        print(f"  {name}.{ext}: {len(raw) / 1024:.0f} KB")


def _a4_top(browser, html: str, png: Path, height: int = 1000) -> None:
    page = browser.new_page(viewport={"width": 794, "height": height}, device_scale_factor=1.5)
    page.set_content(html, wait_until="load")
    page.evaluate("document.fonts.ready")
    page.add_style_tag(content="body { padding: 16mm 15mm; }")
    page.screenshot(path=str(png), clip={"x": 0, "y": 0, "width": 794, "height": height})
    page.close()


def main(video: bool) -> None:
    settings = get_settings()
    conn = db.connect(settings, "dev", autocommit=True)
    tmp = Path(tempfile.mkdtemp())
    SHOTS.mkdir(parents=True, exist_ok=True)
    try:
        _cleanup(conn)
        demo = _build(conn)
        auth = _session(conn, demo["client"])
        site_copy = tmp / "web"
        shutil.copytree(WEB, site_copy)
        (site_copy / "config.js").write_text(
            "window.VISIBLE_IA_CONFIG = "
            + json.dumps({"supabaseUrl": auth["url"], "anonKey": auth["anon"]}) + ";"
        )
        panel = (site_copy / "panel" / "index.html").as_uri() + (
            f"#access_token={auth['access']}&refresh_token={auth['refresh']}"
            "&expires_in=3600&token_type=bearer&type=magiclink"
        )
        with sync_playwright() as p:
            browser = p.chromium.launch()
            shots = {}
            page = browser.new_page(viewport={"width": 1200, "height": 750}, device_scale_factor=2)
            page.goto(panel)
            page.wait_for_selector("#contenido:not([hidden])", timeout=30000)
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(800)
            shots["producto-panel"] = tmp / "panel.png"
            page.screenshot(path=str(shots["producto-panel"]))
            page.evaluate(
                "window.scrollTo(0, document.getElementById('h-tareas').getBoundingClientRect().top"
                " + window.scrollY - 24)"
            )
            page.wait_for_timeout(300)
            shots["producto-checklist"] = tmp / "checklist.png"
            page.screenshot(path=str(shots["producto-checklist"]))
            page.close()

            data = load_monthly_data(conn, demo["site"], MONTHS[-1])
            shots["producto-mensual"] = tmp / "mensual.png"
            _a4_top(browser, render_monthly(build_monthly_context(data, load_brand())),
                    shots["producto-mensual"])  # fmt: skip
            shots["producto-kit"] = tmp / "kit.png"
            kit = kit_context(ME, "https://tuclinicadental.pe/", load_brand(),
                              settings.site_url.rstrip("/") + PANEL_PATH)  # fmt: skip
            _a4_top(browser, render_kit(kit), shots["producto-kit"])

            encoder = browser.new_page()
            encoder.set_content("<html><body></body></html>")
            # Double resolution for sharp images on retina screens (the frame shows ~920 px).
            for name, png in shots.items():
                _encode(encoder, png, name, 1840 if "panel" in name or "checklist" in name else 1190,
                        SHOTS)  # fmt: skip
            # producto-diagnostico (the report's cover) comes from scripts/imagen_informe_landing.py

            if video:
                ctx = browser.new_context(viewport={"width": 1200, "height": 750},
                                          record_video_dir=str(tmp / "video"),
                                          record_video_size={"width": 960, "height": 600})  # fmt: skip
                vp = ctx.new_page()
                vp.goto(panel)
                vp.wait_for_selector("#contenido:not([hidden])", timeout=30000)
                vp.wait_for_timeout(900)
                for y in range(0, 2400, 60):
                    vp.evaluate(f"window.scrollTo(0, {y})")
                    vp.wait_for_timeout(60)
                vp.wait_for_timeout(700)
                ctx.close()
                recorded = Path(vp.video.path())
                size = recorded.stat().st_size
                print(f"  video: {size / 1024:.0f} KB")
                if size < 1.5 * 1024 * 1024:
                    shutil.copy(recorded, SHOTS / "producto-panel.webm")
                else:
                    print("  video > 1.5 MB: not used")
            browser.close()
    finally:
        _cleanup(conn)
        conn.close()
        shutil.rmtree(tmp, ignore_errors=True)
        print("demo borrado de dev")


if __name__ == "__main__":
    main(video="--video" in sys.argv)
