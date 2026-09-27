"""Command line interface for the operator."""

import typer

from visible_ia import __version__, db
from visible_ia.config import get_settings
from visible_ia.heartbeat import HeartbeatError, diagnose_supabase_url, run_heartbeat

app = typer.Typer(help="visible-ia: herramienta del operador.", no_args_is_help=True)
config_app = typer.Typer(help="Configuración y variables de entorno.", no_args_is_help=True)
app.add_typer(config_app, name="config")
db_app = typer.Typer(help="Base de datos: migraciones.", no_args_is_help=True)
app.add_typer(db_app, name="db")
plantillas_app = typer.Typer(help="Plantillas de preguntas por rubro.", no_args_is_help=True)
app.add_typer(plantillas_app, name="plantillas")


def _confirm_prod(target: str) -> None:
    if target == "prod":
        answer = typer.prompt("Vas a modificar PRODUCCIÓN. Escribe SI para continuar")
        if answer.strip() != "SI":
            typer.echo("Cancelado.")
            raise typer.Exit(code=1)


@app.callback()
def main() -> None:
    """visible-ia: herramienta del operador."""


@app.command()
def version() -> None:
    """Muestra la versión instalada."""
    typer.echo(__version__)


@app.command()
def heartbeat(env: str = typer.Option(None, help="dev o prod.")) -> None:
    """Hace actividad real en Supabase para que el plan gratis no pause el proyecto."""
    target = _resolve_env(env)
    settings = get_settings()
    url = settings.value(f"SUPABASE_URL_{target.upper()}")
    key = settings.value(f"SUPABASE_SERVICE_ROLE_KEY_{target.upper()}")
    if not url or key is None or not key.get_secret_value():
        typer.echo(
            f"Faltan SUPABASE_URL_{target.upper()} o SUPABASE_SERVICE_ROLE_KEY_{target.upper()}"
        )
        raise typer.Exit(code=1)
    problem = diagnose_supabase_url(url)
    if problem:
        typer.echo(f"SUPABASE_URL_{target.upper()} no es la URL de la API: {problem}")
        raise typer.Exit(code=1)
    try:
        result = run_heartbeat(url, key.get_secret_value(), target)
    except HeartbeatError as exc:
        typer.echo(f"Heartbeat falló ({target}): {exc}")
        raise typer.Exit(code=1) from None
    typer.echo(f"Heartbeat OK ({target}): latido guardado, {result.old_deleted} viejos borrados.")


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
        _confirm_prod(target)
        for path in pending:
            db.apply_migration(conn, path)
            typer.echo(f"  aplicada: {path.name}")
    typer.echo("Listo.")


@plantillas_app.command("cargar")
def plantillas_cargar(env: str = typer.Option(None, help="dev o prod.")) -> None:
    """Carga (o actualiza) las 40 plantillas aprobadas desde data/plantillas-preguntas.csv."""
    from visible_ia.mercados.plantillas import InvalidTemplates, read_templates, upsert_templates

    target = _resolve_env(env)
    try:
        templates = read_templates()
    except InvalidTemplates as exc:
        typer.echo(f"El CSV de plantillas no es válido: {exc}")
        raise typer.Exit(code=1) from None
    _confirm_prod(target)
    try:
        with db.connect(get_settings(), target) as conn:
            n = upsert_templates(conn, templates)
    except db.MissingDatabaseUrl as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from None
    typer.echo(f"Entorno: {target} · plantillas cargadas: {n}")
