"""Command line interface for the operator."""

from datetime import date
from pathlib import Path

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
mercado_app = typer.Typer(help="Mercados (rubro + distrito) y sus preguntas.", no_args_is_help=True)
app.add_typer(mercado_app, name="mercado")
clinicas_app = typer.Typer(help="Clínicas de cada mercado y sus alias.", no_args_is_help=True)
app.add_typer(clinicas_app, name="clinicas")
alias_app = typer.Typer(help="Alias de una clínica.", no_args_is_help=True)
clinicas_app.add_typer(alias_app, name="alias")


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


def _connect_or_exit(target: str):
    try:
        return db.connect(get_settings(), target)
    except db.MissingDatabaseUrl as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from None


@mercado_app.command("crear")
def mercado_crear(
    rubro: str = typer.Option(..., help="IMP, EDE, MES o DER."),
    distrito: str = typer.Option(..., help="Miraflores, San Isidro o Surco."),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Crea el mercado y genera sus 10 preguntas desde las plantillas del rubro."""
    from visible_ia.mercados.mercado import MarketError, create_market, list_questions

    target = _resolve_env(env)
    _confirm_prod(target)
    with _connect_or_exit(target) as conn:
        try:
            market_id = create_market(conn, rubro.upper(), distrito)
        except MarketError as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from None
        typer.echo(f"Mercado {market_id} creado: {rubro.upper()} · {distrito}")
        for q in list_questions(conn, market_id):
            typer.echo(f"  {q.template_id}  {q.text}")


@mercado_app.command("listar")
def mercado_listar(env: str = typer.Option(None, help="dev o prod.")) -> None:
    """Lista los mercados."""
    from visible_ia.mercados.mercado import list_markets

    with _connect_or_exit(_resolve_env(env)) as conn:
        for market_id, category, district, version, active in list_markets(conn):
            state = "activo" if active else "inactivo"
            typer.echo(f"{market_id}  {category} · {district}  (banco v{version}, {state})")


@mercado_app.command("preguntas")
def mercado_preguntas(
    market_id: int,
    version: int = typer.Option(None, help="Versión del banco (por defecto, la actual)."),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Muestra las preguntas del mercado."""
    from visible_ia.mercados.mercado import MarketError, list_questions

    with _connect_or_exit(_resolve_env(env)) as conn:
        try:
            questions = list_questions(conn, market_id, version)
        except MarketError as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from None
    for q in questions:
        typer.echo(f"{q.template_id}  (v{q.version})  {q.text}")


@mercado_app.command("editar-pregunta")
def mercado_editar_pregunta(
    market_id: int,
    plantilla: str = typer.Option(..., help="Id de la plantilla, p. ej. IMP-03."),
    texto: str = typer.Option(..., help="Nuevo texto de la pregunta."),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Cambia una pregunta (crea una versión nueva del banco si ya hubo corridas)."""
    from visible_ia.mercados.mercado import MarketError, edit_question

    target = _resolve_env(env)
    _confirm_prod(target)
    with _connect_or_exit(target) as conn:
        try:
            version = edit_question(conn, market_id, plantilla.upper(), texto)
        except MarketError as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from None
    typer.echo(f"Pregunta {plantilla.upper()} actualizada (banco v{version}).")


@clinicas_app.command("importar")
def clinicas_importar(
    archivo: Path = typer.Argument(..., exists=True, dir_okay=False, help="CSV de clínicas."),
    mercado: int = typer.Option(..., help="Id del mercado."),
    fecha_dato: str = typer.Option(
        None, help="Fecha de ★ y reseñas (AAAA-MM-DD); hoy si se omite."
    ),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Importa clínicas desde un CSV y las asocia al mercado (informa filas con errores)."""
    from visible_ia.mercados.clinicas import InvalidClinicsFile, import_clinics, read_clinics_csv

    target = _resolve_env(env)
    try:
        rows, errors = read_clinics_csv(archivo)
        data_date = date.fromisoformat(fecha_dato) if fecha_dato else date.today()
    except (InvalidClinicsFile, ValueError) as exc:
        typer.echo(f"No se pudo leer el archivo: {exc}")
        raise typer.Exit(code=1) from None
    for err in errors:
        typer.echo(f"  fila {err.line}: {err.message} (omitida)")
    _confirm_prod(target)
    with _connect_or_exit(target) as conn:
        try:
            created, updated = import_clinics(conn, mercado, rows, data_date)
        except InvalidClinicsFile as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from None
    typer.echo(
        f"Mercado {mercado}: {created} clínicas nuevas, {updated} actualizadas, "
        f"{len(errors)} filas con errores."
    )


@clinicas_app.command("listar")
def clinicas_listar(
    mercado: int = typer.Option(..., help="Id del mercado."),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Lista las clínicas del mercado."""
    from visible_ia.mercados.clinicas import list_market_clinics

    with _connect_or_exit(_resolve_env(env)) as conn:
        for clinic_id, name, rating, reviews, data_date in list_market_clinics(conn, mercado):
            stars = f"{rating}★" if rating is not None else "sin ★"
            typer.echo(f"{clinic_id}  {name}  ({stars}, {reviews or 0} reseñas, dato {data_date})")


@alias_app.command("agregar")
def alias_agregar(
    clinica: int = typer.Argument(..., help="Id de la clínica."),
    alias: str = typer.Argument(..., help="Otro nombre con que la IA la menciona."),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Agrega un alias a la clínica."""
    from visible_ia.mercados.alias import AliasError, add_alias

    target = _resolve_env(env)
    _confirm_prod(target)
    with _connect_or_exit(target) as conn:
        try:
            added = add_alias(conn, clinica, alias)
        except AliasError as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from None
    typer.echo("Alias agregado." if added else "La clínica ya tenía ese alias.")


@alias_app.command("listar")
def alias_listar(
    clinica: int = typer.Argument(..., help="Id de la clínica."),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Lista los alias de la clínica."""
    from visible_ia.mercados.alias import list_aliases

    with _connect_or_exit(_resolve_env(env)) as conn:
        for alias in list_aliases(conn, clinica):
            typer.echo(alias)


@alias_app.command("quitar")
def alias_quitar(
    clinica: int = typer.Argument(..., help="Id de la clínica."),
    alias: str = typer.Argument(..., help="Alias a quitar."),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Quita un alias de la clínica."""
    from visible_ia.mercados.alias import remove_alias

    target = _resolve_env(env)
    _confirm_prod(target)
    with _connect_or_exit(target) as conn:
        removed = remove_alias(conn, clinica, alias)
    typer.echo("Alias quitado." if removed else "La clínica no tenía ese alias.")
