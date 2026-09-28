"""Render report templates to HTML (StrictUndefined: a missing value is an error, never blank).

The brand fonts (informes/fuentes/*.woff2, SIL OFL) are embedded as data URIs, so the PDF looks
the same on any PC and without internet.
"""

import base64
from functools import cache
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

HERE = Path(__file__).resolve().parent
TEMPLATES = HERE / "plantillas"
STYLES = HERE / "estilos.css"
FONTS = HERE / "fuentes"
FONT_FACES = (  # (family, weight, file)
    ("Source Serif 4", 600, "SourceSerif4-600.woff2"),
    ("IBM Plex Sans", 400, "IBMPlexSans-400.woff2"),
    ("IBM Plex Sans", 600, "IBMPlexSans-600.woff2"),
    ("IBM Plex Mono", 500, "IBMPlexMono-500.woff2"),
)


@cache
def fonts_css() -> str:
    faces = []
    for family, weight, name in FONT_FACES:
        data = base64.b64encode((FONTS / name).read_bytes()).decode()
        faces.append(
            f'@font-face {{ font-family: "{family}"; font-weight: {weight}; font-style: normal; '
            f'src: url(data:font/woff2;base64,{data}) format("woff2"); }}'
        )
    return "\n".join(faces)


def environment() -> Environment:
    return Environment(
        loader=FileSystemLoader(TEMPLATES),
        autoescape=select_autoescape(["html", "j2"]),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _render(name: str, context: dict[str, Any]) -> str:
    template = environment().get_template(name)
    return template.render(
        **context, estilos=STYLES.read_text(encoding="utf-8"), letras=fonts_css()
    )


def render_diagnostic(context: dict[str, Any]) -> str:
    return _render("diagnostico.html.j2", context)


def render_monthly(context: dict[str, Any]) -> str:
    return _render("mensual.html.j2", context)


def render_kit(context: dict[str, Any]) -> str:
    return _render("kit.html.j2", context)


def diagnostic_frame(context: dict[str, Any]) -> tuple[str, str]:
    """Header and footer of every page of the diagnostic PDF (Chromium templates)."""
    style = (
        "<style>*{-webkit-print-color-adjust:exact;print-color-adjust:exact}"
        ".f{width:100%;margin:0 15mm;display:flex;justify-content:space-between;"
        "align-items:center;font-family:'Segoe UI',Arial,sans-serif;font-size:8.5px;"
        "color:#51607A}.f img{height:14px}</style>"
    )
    brand = context["marca"]
    logo = f'<img src="{brand["logo_url"]}">' if brand.get("logo_url") else brand["nombre"]
    who = f"{context['clinica']['nombre']} · {context['mercado']['mes']}"
    header = f'{style}<div class="f">{logo}<span>{who}</span></div>'
    footer = (
        f'{style}<div class="f"><span>{brand["nombre"]} · {brand["lema"]}</span>'
        '<span>Página <span class="pageNumber"></span> de <span class="totalPages"></span>'
        "</span></div>"
    )
    return header, footer
