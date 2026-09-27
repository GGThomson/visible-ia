"""Render report templates to HTML (StrictUndefined: a missing value is an error, never blank)."""

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

HERE = Path(__file__).resolve().parent
TEMPLATES = HERE / "plantillas"
STYLES = HERE / "estilos.css"


def environment() -> Environment:
    return Environment(
        loader=FileSystemLoader(TEMPLATES),
        autoescape=select_autoescape(["html", "j2"]),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_diagnostic(context: dict[str, Any]) -> str:
    template = environment().get_template("diagnostico.html.j2")
    return template.render(**context, estilos=STYLES.read_text(encoding="utf-8"))
