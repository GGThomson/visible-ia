"""Command line interface for the operator."""

import typer

from visible_ia import __version__, db
from visible_ia.config import get_settings

app = typer.Typer(help="visible-ia: herramienta del operador.", no_args_is_help=True)
config_app = typer.Typer(help="Configuración y variables de entorno.", no_args_is_help=True)
app.add_typer(config_app, name="config")
db_app = typer.Typer(help="Base de datos: migraciones.", no_args_is_help=True)
app.add_typer(db_app, name="db")


@app.callback()
def main() -> None:
    """visible-ia: herramienta del operador."""


@app.command()
def version() -> None:
    """Muestra la versión instalada."""
    typer.echo(__version__)


def _resolve_env(env: str | None) -> str:
    target = env or get_settings().visible_ia_env
    if target not in ("dev", "prod"):
        typer.echo(f"Entorno no válido: {target} (usa dev o prod).")
        raise typer.Exit(code=2)
    return target


@config_app.command("check")
def config_check(
    env: str = typer.Option(None, help="dev o prod (por defecto, VISIBLE_IA_ENV)."),
) -> None:
    """Dice qué variables faltan, sin mostrar ningún valor."""
    settings = get_settings()
    target = _resolve_env(env)
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


@db_app.command("status")
def db_status(env: str = typer.Option(None, help="dev o prod.")) -> None:
    """Lista las migraciones pendientes del entorno."""
    target = _resolve_env(env)
    try:
        with db.connect(get_settings(), target) as conn:
            pending = db.pending_migrations(conn)
    except db.MissingDatabaseUrl as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from None
    typer.echo(f"Entorno: {target}")
    if not pending:
        typer.echo("Sin migraciones pendientes.")
    for path in pending:
        typer.echo(f"  pendiente: {path.name}")


@db_app.command("migrate")
def db_migrate(
    env: str = typer.Option(None, help="dev o prod."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Solo muestra qué se aplicaría."),
) -> None:
    """Aplica en orden las migraciones pendientes (en prod pide confirmación)."""
    target = _resolve_env(env)
    try:
        conn = db.connect(get_settings(), target)
    except db.MissingDatabaseUrl as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from None
    with conn:
        pending = db.pending_migrations(conn)
        typer.echo(f"Entorno: {target} · pendientes: {len(pending)}")
        if not pending or dry_run:
            for path in pending:
                typer.echo(f"  se aplicaría: {path.name}")
            return
        if target == "prod":
            answer = typer.prompt("Vas a modificar PRODUCCIÓN. Escribe SI para continuar")
            if answer.strip() != "SI":
                typer.echo("Cancelado.")
                raise typer.Exit(code=1)
        for path in pending:
            db.apply_migration(conn, path)
            typer.echo(f"  aplicada: {path.name}")
    typer.echo("Listo.")
