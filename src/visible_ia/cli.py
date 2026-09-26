"""Command line interface for the operator."""

import typer

from visible_ia import __version__
from visible_ia.config import get_settings

app = typer.Typer(help="visible-ia: herramienta del operador.", no_args_is_help=True)
config_app = typer.Typer(help="Configuración y variables de entorno.", no_args_is_help=True)
app.add_typer(config_app, name="config")


@app.callback()
def main() -> None:
    """visible-ia: herramienta del operador."""


@app.command()
def version() -> None:
    """Muestra la versión instalada."""
    typer.echo(__version__)


@config_app.command("check")
def config_check(
    env: str = typer.Option(None, help="dev o prod (por defecto, VISIBLE_IA_ENV)."),
) -> None:
    """Dice qué variables faltan, sin mostrar ningún valor."""
    settings = get_settings()
    target = env or settings.visible_ia_env
    if target not in ("dev", "prod"):
        typer.echo(f"Entorno no válido: {target} (usa dev o prod).")
        raise typer.Exit(code=2)
    missing = settings.missing_required(target)
    later = settings.missing_later(target)
    typer.echo(f"Entorno: {target}")
    for name in missing:
        typer.echo(f"  FALTA (obligatoria): {name}")
    for name, task in later.items():
        typer.echo(f"  pendiente: {name} -> se necesita en {task}")
    if missing:
        raise typer.Exit(code=1)
    typer.echo("OK: están las variables obligatorias.")
