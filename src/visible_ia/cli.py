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
presupuesto_app = typer.Typer(
    help="Presupuesto de OpenAI y cuota de SerpApi.", no_args_is_help=True
)
app.add_typer(presupuesto_app, name="presupuesto")
corrida_app = typer.Typer(
    help="Corridas del motor (ChatGPT API y Google Modo IA).", no_args_is_help=True
)
app.add_typer(corrida_app, name="corrida")
muestra_app = typer.Typer(
    help="Muestras manuales de las apps (no entran al índice).", no_args_is_help=True
)
app.add_typer(muestra_app, name="muestra")
revisar_app = typer.Typer(help="Revisión de las menciones extraídas.", no_args_is_help=True)
app.add_typer(revisar_app, name="revisar")
puntaje_app = typer.Typer(
    help="Índice de presencia, ranking, fuentes y brecha.", no_args_is_help=True
)
app.add_typer(puntaje_app, name="puntaje")

SURFACES_API = ("chatgpt_api", "google_ai_mode")


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


def _connect_or_exit(target: str, *, autocommit: bool = False):
    try:
        return db.connect(get_settings(), target, autocommit=autocommit)
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


def _parse_surfaces(value: str) -> list[str]:
    surfaces = [s.strip() for s in value.split(",") if s.strip()]
    unknown = [s for s in surfaces if s not in SURFACES_API]
    if not surfaces or unknown:
        typer.echo(f"Superficies no válidas: {value} (usa {','.join(SURFACES_API)}).")
        raise typer.Exit(code=2)
    return surfaces


def _serpapi_account_used(settings) -> int | None:
    from visible_ia.motor.google_ai_mode import SerpApiError, account_usage

    key = settings.serpapi_api_key
    if key is None or not key.get_secret_value().strip():
        return None
    try:
        return account_usage(key.get_secret_value())
    except (SerpApiError, OSError) as exc:
        typer.echo(f"Aviso: no se pudo leer la cuenta de SerpApi ({exc}); se usa la base.")
        return None


@presupuesto_app.command("ver")
def presupuesto_ver(
    preguntas: int = typer.Option(10, help="Preguntas por corrida."),
    reps: int = typer.Option(3, help="Repeticiones por pregunta."),
    superficies: str = typer.Option(",".join(SURFACES_API), help="Superficies separadas por coma."),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Muestra el gasto del mes y si una corrida entraría en el presupuesto (no llama a OpenAI)."""
    from visible_ia.motor.presupuesto import RunPlan, check, month_usage

    settings = get_settings()
    plan = RunPlan.for_market(preguntas, reps, _parse_surfaces(superficies))
    with _connect_or_exit(_resolve_env(env)) as conn:
        usage = month_usage(conn, serpapi_account_used=_serpapi_account_used(settings))
    result = check(
        plan,
        usage,
        budget_usd=settings.monthly_budget_usd,
        serpapi_quota=settings.serpapi_monthly_quota,
    )
    typer.echo(result.explain())
    if not result.ok:
        raise typer.Exit(code=1)


def _engine_clients(settings, surfaces: list[str]) -> dict:
    """Real clients for the requested surfaces; exits if a key is missing."""
    clients = {}
    if "chatgpt_api" in surfaces:
        import openai

        from visible_ia.motor import chatgpt_api

        key = settings.openai_api_key
        if key is None or not key.get_secret_value().strip():
            typer.echo("Falta OPENAI_API_KEY en .env")
            raise typer.Exit(code=1)
        oa = openai.OpenAI(
            api_key=key.get_secret_value(),
            max_retries=0,
            timeout=chatgpt_api.TIMEOUT_SECONDS,
        )
        clients["chatgpt_api"] = lambda q: chatgpt_api.ask(q, client=oa)
    if "google_ai_mode" in surfaces:
        import httpx

        from visible_ia.motor import google_ai_mode

        key = settings.serpapi_api_key
        if key is None or not key.get_secret_value().strip():
            typer.echo("Falta SERPAPI_API_KEY en .env")
            raise typer.Exit(code=1)
        http = httpx.Client(timeout=google_ai_mode.TIMEOUT_SECONDS)
        secret = key.get_secret_value()
        clients["google_ai_mode"] = lambda q: google_ai_mode.ask(q, api_key=secret, client=http)
    return clients


def _budget_ok(conn, settings, plan, forzar: bool):
    """Runs the HU-05 guard. Returns (allowed, forced, estimated_cost)."""
    from visible_ia.motor.presupuesto import authorize, check, month_usage

    usage = month_usage(conn, serpapi_account_used=_serpapi_account_used(settings))
    result = check(
        plan,
        usage,
        budget_usd=settings.monthly_budget_usd,
        serpapi_quota=settings.serpapi_monthly_quota,
    )
    allowed = authorize(result, force=forzar, prompt=typer.prompt, echo=typer.echo)
    return allowed, allowed and not result.ok, result.estimated_cost_usd


def _run_and_report(conn, run_id: int, clients: dict) -> None:
    from visible_ia.motor.corrida import execute

    def progress(call, answer, error):
        label = f"{call.surface:<15} {call.template_id} rep {call.repetition}"
        if error is not None:
            typer.echo(f"  ✗ {label}: {type(error).__name__}: {str(error)[:120]}")
        else:
            extra = " (sin respuesta de IA)" if answer.empty else ""
            typer.echo(f"  ✓ {label}  US${answer.cost_usd:.4f}{extra}")

    typer.echo(f"Corrida {run_id}: lanzando (Ctrl+C la corta; luego: corrida reanudar {run_id})")
    try:
        result = execute(conn, run_id, clients, on_progress=progress)
    except KeyboardInterrupt:
        typer.echo(
            f"\nCortada. Lo hecho quedó guardado. Reanuda con: visible-ia corrida reanudar {run_id}"
        )
        raise typer.Exit(code=130) from None
    typer.echo(
        f"Corrida {run_id}: {result.status} · {result.done}/{result.total} respuestas · "
        f"costo US${result.cost_usd:.4f}"
    )
    if result.failures:
        typer.echo(f"{len(result.failures)} llamadas fallaron (reanuda para reintentarlas).")
        raise typer.Exit(code=1)


@corrida_app.command("lanzar")
def corrida_lanzar(
    mercado: int = typer.Option(..., help="Id del mercado."),
    superficies: str = typer.Option(",".join(SURFACES_API), help="Superficies separadas por coma."),
    reps: int = typer.Option(3, min=1, help="Repeticiones por pregunta."),
    forzar: bool = typer.Option(False, "--forzar", help="Permite superar el tope (pide SI)."),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Crea una corrida del mercado y hace todas sus llamadas (respeta el presupuesto)."""
    from visible_ia.mercados.mercado import MarketError, list_questions
    from visible_ia.motor.corrida import create_run
    from visible_ia.motor.presupuesto import RunPlan

    surfaces = _parse_surfaces(superficies)
    target = _resolve_env(env)
    _confirm_prod(target)
    settings = get_settings()
    with _connect_or_exit(target, autocommit=True) as conn:
        try:
            questions = list_questions(conn, mercado)
        except MarketError as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from None
        plan = RunPlan.for_market(len(questions), reps, surfaces)
        allowed, forced, estimated = _budget_ok(conn, settings, plan, forzar)
        if not allowed:
            raise typer.Exit(code=1)
        clients = _engine_clients(settings, surfaces)
        run_id = create_run(
            conn,
            mercado,
            surfaces=surfaces,
            repetitions=reps,
            estimated_cost_usd=estimated,
            forced=forced,
        )
        _run_and_report(conn, run_id, clients)


@corrida_app.command("reanudar")
def corrida_reanudar(
    corrida: int = typer.Argument(..., help="Id de la corrida."),
    forzar: bool = typer.Option(False, "--forzar", help="Permite superar el tope (pide SI)."),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Hace solo las llamadas que faltan de una corrida."""
    from visible_ia.motor.corrida import RunError, pending_calls, plan_of

    target = _resolve_env(env)
    _confirm_prod(target)
    settings = get_settings()
    with _connect_or_exit(target, autocommit=True) as conn:
        try:
            calls = pending_calls(conn, corrida)
        except RunError as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from None
        if not calls:
            typer.echo(f"La corrida {corrida} no tiene llamadas pendientes.")
            return
        plan = plan_of(calls)
        allowed, forced, _ = _budget_ok(conn, settings, plan, forzar)
        if not allowed:
            raise typer.Exit(code=1)
        if forced:
            with conn.transaction(), conn.cursor() as cur:
                cur.execute("update public.runs set forced = true where id = %s", (corrida,))
        clients = _engine_clients(settings, sorted({c.surface for c in calls}))
        _run_and_report(conn, corrida, clients)


@corrida_app.command("ver")
def corrida_ver(
    corrida: int = typer.Argument(..., help="Id de la corrida."),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Muestra el avance, el costo y lo que falló de una corrida."""
    from visible_ia.motor.corrida import RunError, progress_by_surface, summary

    with _connect_or_exit(_resolve_env(env)) as conn:
        try:
            result = summary(conn, corrida)
        except RunError as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from None
        typer.echo(
            f"Corrida {corrida}: {result.status} · {result.done}/{result.total} respuestas · "
            f"costo US${result.cost_usd:.4f}"
        )
        for surface, (done, total) in progress_by_surface(conn, corrida).items():
            typer.echo(f"  {surface:<15} {done}/{total}")
        for failure in result.failures:
            typer.echo(
                f"  ✗ {failure['surface']} {failure['template_id']} rep {failure['repetition']}: "
                f"{failure['error']}"
            )


@muestra_app.command("cargar")
def muestra_cargar(
    mercado: int = typer.Option(..., help="Id del mercado."),
    pregunta: int = typer.Option(..., min=1, max=10, help="N.º de la pregunta (1 a 10)."),
    superficie: str = typer.Option(
        ..., help="chatgpt_app_manual, gemini_app_manual o google_ai_mode_manual."
    ),
    archivo: Path = typer.Option(
        None, exists=True, dir_okay=False, help="Archivo con la respuesta (si no, abre el editor)."
    ),
    fuentes: str = typer.Option("", help="URLs citadas, separadas por espacios."),
    fecha: str = typer.Option(None, help="Fecha de la consulta, AAAA-MM-DD (por defecto, hoy)."),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Guarda una respuesta pegada de la app de ChatGPT, Gemini o Google (manual / app)."""
    from visible_ia.mercados.mercado import MarketError
    from visible_ia.motor.manual import ManualError, parse_sources, save_manual, split_pasted

    if archivo is not None:
        text = archivo.read_text(encoding="utf-8")
    else:
        text = typer.edit(
            "\n# Pega arriba la respuesta completa de la app. Las líneas con # se ignoran.\n"
            "# Pega las URLs citadas en líneas que empiecen con 'fuente: '.\n"
        )
        text = text or ""
    body, pasted_urls = split_pasted(text)
    urls = parse_sources(fuentes) + pasted_urls
    taken_on = date.fromisoformat(fecha) if fecha else date.today()
    target = _resolve_env(env)
    _confirm_prod(target)
    with _connect_or_exit(target) as conn:
        try:
            category = _market_category(conn, mercado)
            run_id, rep, _ = save_manual(
                conn,
                mercado,
                f"{category}-{pregunta:02d}",
                superficie,
                body,
                urls,
                taken_on=taken_on,
            )
        except (ManualError, MarketError) as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from None
    typer.echo(
        f"Muestra guardada (manual / app, no entra al índice): corrida {run_id}, "
        f"{category}-{pregunta:02d}, {superficie}, repetición {rep}, {len(urls)} fuentes."
    )


def _market_category(conn, market_id: int) -> str:
    from visible_ia.mercados.mercado import MarketError

    with conn.cursor() as cur:
        cur.execute("select category_code from public.markets where id = %s", (market_id,))
        row = cur.fetchone()
    if row is None:
        raise MarketError(f"No existe el mercado {market_id}")
    return row[0]


@muestra_app.command("importar")
def muestra_importar(
    archivo: Path = typer.Argument(..., exists=True, dir_okay=False, help="CSV de registro."),
    crear_mercados: bool = typer.Option(
        False, "--crear-mercados", help="Crea (inactivos) los mercados que falten."
    ),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Importa respuestas manuales con el formato de registro.csv de la fase 1."""
    from visible_ia.motor.manual import import_registry

    target = _resolve_env(env)
    _confirm_prod(target)
    with _connect_or_exit(target) as conn:
        result = import_registry(conn, archivo, create_markets=crear_mercados)
    for market in result.markets_created:
        typer.echo(f"Mercado creado (inactivo): {market}")
    for surface, count in sorted(result.by_surface.items()):
        typer.echo(f"  {surface:<22} {count}")
    typer.echo(f"Importadas: {result.imported} · ya estaban: {result.already_there}")
    for skipped in result.skipped:
        typer.echo(f"  omitida: {skipped}")


# --- extractor (C4) ------------------------------------------------------------------------


def _openai_key(settings) -> str:
    key = settings.openai_api_key
    if key is None or not key.get_secret_value().strip():
        typer.echo("Falta OPENAI_API_KEY en .env")
        raise typer.Exit(code=1)
    return key.get_secret_value()


@app.command("extraer")
def extraer(
    corrida: int = typer.Argument(..., help="Id de la corrida."),
    forzar: bool = typer.Option(False, "--forzar", help="Permite superar el tope (pide SI)."),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Extrae, asocia y clasifica las respuestas pendientes de una corrida (gpt-5-nano)."""
    import openai

    from visible_ia.extractor import llm
    from visible_ia.extractor.extraccion import (
        ESTIMATED_COST_PER_ANSWER,
        extract_run,
        pending_answers,
    )
    from visible_ia.motor.presupuesto import month_usage

    target = _resolve_env(env)
    _confirm_prod(target)
    settings = get_settings()
    with _connect_or_exit(target, autocommit=True) as conn:
        pending = pending_answers(conn, corrida)
        if not pending:
            typer.echo(f"La corrida {corrida} no tiene respuestas pendientes de extraer.")
            return
        usage = month_usage(conn)
        estimated = len(pending) * ESTIMATED_COST_PER_ANSWER
        budget = settings.monthly_budget_usd
        typer.echo(
            f"Extractor (gpt-5-nano): {len(pending)} respuestas × ≤ US${ESTIMATED_COST_PER_ANSWER} "
            f"= ≤ US${estimated:.3f}\n  Gastado este mes: US${usage.spent_usd:.2f} de "
            f"US${budget:.2f} → quedaría en ≤ US${usage.spent_usd + estimated:.2f}"
        )
        if usage.spent_usd + estimated > budget:
            if not forzar:
                typer.echo("BLOQUEADA: superaría el presupuesto. Para forzarla: --forzar.")
                raise typer.Exit(code=1)
            if typer.prompt("Escribe SI para superar el presupuesto").strip() != "SI":
                typer.echo("Cancelado.")
                raise typer.Exit(code=1)
        client = openai.OpenAI(
            api_key=_openai_key(settings), max_retries=0, timeout=llm.TIMEOUT_SECONDS
        )
        prompt = llm.load_prompt()

        def extractor(text, links):
            return llm.extract(text, link_texts=links, client=client, prompt=prompt)

        def progress(answer, extraction, error):
            if error is not None:
                typer.echo(f"  ✗ respuesta {answer.response_id}: {type(error).__name__}: {error}")
            else:
                names = ", ".join(m.raw_name for m in extraction.mentions) or "(ninguna)"
                typer.echo(f"  ✓ {answer.response_id} {answer.surface:<15} {names[:110]}")

        result = extract_run(conn, corrida, extractor, on_progress=progress)
    typer.echo(
        f"Extraídas: {result.extracted} respuestas · {result.mentions} menciones "
        f"({result.matched} asociadas, {result.new} nuevas, {result.review} a revisar) · "
        f"costo US${result.cost_usd:.4f}"
    )
    if result.failures:
        typer.echo(
            f"{len(result.failures)} fallaron; vuelve a ejecutar extraer para reintentarlas."
        )
        raise typer.Exit(code=1)


def _mentions_table(rows):
    from rich.table import Table

    table = Table(show_lines=False)
    for column in ("id", "pos", "nombre en la respuesta", "clínica", "estado"):
        table.add_column(column)
    for r in rows:
        clinic = f"{r.clinic_id}: {r.clinic_name}" if r.clinic_id else "— nueva —"
        table.add_row(str(r.mention_id), str(r.position), r.raw_name, clinic, r.status)
    return table


REVIEW_HELP = (
    "Enter = seguir · a <id> <clínica> = asociar · n <id> [nombre] = nueva clínica · "
    "d <id> = descartar · u <id> <id_destino> = unir · q = salir"
)


@revisar_app.command("corrida")
def revisar_corrida(
    corrida: int = typer.Argument(..., help="Id de la corrida."),
    todas: bool = typer.Option(False, "--todas", help="Muestra también las respuestas sin dudas."),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Revisa las menciones respuesta por respuesta (por defecto, solo las nuevas o dudosas)."""
    from rich.console import Console

    from visible_ia.extractor import revision

    console = Console()
    target = _resolve_env(env)
    _confirm_prod(target)
    with _connect_or_exit(target, autocommit=True) as conn:
        by_response: dict[int, list] = {}
        for row in revision.run_mentions(conn, corrida):
            by_response.setdefault(row.response_id, []).append(row)
        for response_id, rows in by_response.items():
            doubtful = any(r.status == "review" or r.clinic_id is None for r in rows)
            if not todas and not doubtful:
                continue
            while True:
                rows = [
                    r for r in revision.run_mentions(conn, corrida) if r.response_id == response_id
                ]
                first = rows[0]
                console.rule(
                    f"Respuesta {response_id} · {first.surface} · "
                    f"{first.template_id} rep {first.repetition}"
                )
                console.print(" ".join(first.text.split())[:600])
                console.print(_mentions_table([r for r in rows if r.status != "discarded"]))
                command = typer.prompt(REVIEW_HELP, default="", show_default=False).strip()
                if not command:
                    break
                if command == "q":
                    return
                parts = command.split(maxsplit=2)
                try:
                    if parts[0] == "a":
                        revision.associate(conn, corrida, int(parts[1]), int(parts[2]))
                    elif parts[0] == "n":
                        name = parts[2] if len(parts) > 2 else None
                        revision.create_clinic_for(conn, corrida, int(parts[1]), name)
                    elif parts[0] == "d":
                        revision.discard(conn, corrida, int(parts[1]))
                    elif parts[0] == "u":
                        revision.merge(conn, corrida, int(parts[1]), int(parts[2]))
                    else:
                        console.print("Comando no válido.")
                except (revision.ReviewError, ValueError, IndexError) as exc:
                    console.print(f"[red]{exc}[/red]")
        left = revision.pending_review(conn, corrida)
    typer.echo(
        f"Fin. Menciones en revisión: {left}. Para cerrar: visible-ia revisar cerrar {corrida}"
    )


@revisar_app.command("exportar")
def revisar_exportar(
    corrida: int = typer.Argument(..., help="Id de la corrida."),
    archivo: Path = typer.Option(None, help="CSV de salida (por defecto, revision-<id>.csv)."),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Exporta las menciones a un CSV para revisarlas en Excel (columna 'accion')."""
    from visible_ia.extractor.revision import export_csv

    archivo = archivo or Path(f"revision-{corrida}.csv")
    with _connect_or_exit(_resolve_env(env)) as conn:
        n = export_csv(conn, corrida, archivo)
    typer.echo(
        f"{n} menciones en {archivo}. En 'accion' escribe ok, asociar (con clinica_destino), "
        "nueva (nombre_nueva opcional), descartar o unir (con unir_con)."
    )


@revisar_app.command("importar")
def revisar_importar(
    corrida: int = typer.Argument(..., help="Id de la corrida."),
    archivo: Path = typer.Argument(..., exists=True, dir_okay=False, help="CSV revisado."),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Aplica las correcciones de un CSV exportado con 'revisar exportar'."""
    from visible_ia.extractor.revision import apply_csv

    target = _resolve_env(env)
    _confirm_prod(target)
    with _connect_or_exit(target) as conn:
        result = apply_csv(conn, corrida, archivo)
    for action, count in sorted(result.by_action.items()):
        typer.echo(f"  {action:<10} {count}")
    for clinic in result.clinics_created:
        typer.echo(f"  clínica creada: {clinic}")
    for error in result.errors:
        typer.echo(f"  error: {error}")
    if result.errors:
        raise typer.Exit(code=1)


@revisar_app.command("nuevas")
def revisar_nuevas(
    mercado: int = typer.Argument(..., help="Id del mercado."),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Clínicas mencionadas que no están en el mercado, con sus apariciones (HU-09)."""
    from rich.console import Console
    from rich.table import Table

    from visible_ia.extractor.revision import new_clinics

    with _connect_or_exit(_resolve_env(env)) as conn:
        rows = new_clinics(conn, mercado)
    table = Table(title=f"Clínicas nuevas · mercado {mercado}")
    for column in ("nombre", "respuestas", "menciones"):
        table.add_column(column)
    for name, responses, mentions in rows:
        table.add_row(name, str(responses), str(mentions))
    Console().print(table)


@revisar_app.command("cerrar")
def revisar_cerrar(
    corrida: int = typer.Argument(..., help="Id de la corrida."),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Marca la corrida como revisada (si no queda nada en revisión)."""
    from visible_ia.extractor.revision import ReviewError, close_review

    target = _resolve_env(env)
    _confirm_prod(target)
    with _connect_or_exit(target) as conn:
        try:
            close_review(conn, corrida)
        except ReviewError as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from None
    typer.echo(f"Corrida {corrida}: revisada.")


@revisar_app.command("reasociar")
def revisar_reasociar(
    corrida: int = typer.Argument(..., help="Id de la corrida."),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Vuelve a asociar las menciones automáticas tras cambiar la lista de clínicas (sin costo)."""
    from visible_ia.extractor.revision import reassociate

    target = _resolve_env(env)
    _confirm_prod(target)
    with _connect_or_exit(target, autocommit=True) as conn:
        counts = reassociate(conn, corrida)
    typer.echo(
        f"Corrida {corrida}: {counts['matched']} asociadas, {counts['new']} nuevas, "
        f"{counts['review']} a revisar · {counts['changed']} menciones cambiaron · "
        f"{counts['sources_changed']} fuentes reclasificadas"
    )


# --- score (C5) ----------------------------------------------------------------------------


def _parse_month(value: str | None) -> date | None:
    if not value:
        return None
    try:
        year, month = (int(x) for x in value.split("-")[:2])
        return date(year, month, 1)
    except ValueError:
        typer.echo(f"Mes no válido: {value} (usa AAAA-MM)")
        raise typer.Exit(code=2) from None


def _fmt(value, suffix: str = "") -> str:
    return "—" if value is None else f"{value:.0f}{suffix}" if suffix else f"{value:.1f}"


@puntaje_app.command("calcular")
def puntaje_calcular(
    corrida: int = typer.Argument(..., help="Id de una corrida revisada."),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Calcula el índice del mes de una corrida revisada y lo guarda (sin costo)."""
    from visible_ia.puntaje.indice import ScoreError, calculate

    target = _resolve_env(env)
    _confirm_prod(target)
    with _connect_or_exit(target, autocommit=True) as conn:
        try:
            market_id, month, scores = calculate(conn, corrida)
        except ScoreError as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from None
    clinics = len({s.clinic_id for s in scores})
    typer.echo(
        f"Mercado {market_id} · {month:%Y-%m}: puntaje de {clinics} clínicas guardado. "
        f"Ver: visible-ia puntaje ranking {market_id}"
    )


@puntaje_app.command("ranking")
def puntaje_ranking(
    mercado: int = typer.Argument(..., help="Id del mercado."),
    mes: str = typer.Option(None, help="AAAA-MM (por defecto, el último calculado)."),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Ranking del mercado por índice combinado, con su margen (HU-10, HU-11)."""
    from rich.console import Console
    from rich.table import Table

    from visible_ia.puntaje.indice import ScoreError, ranking

    with _connect_or_exit(_resolve_env(env)) as conn:
        try:
            month, rows = ranking(conn, mercado, _parse_month(mes))
        except ScoreError as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from None
    table = Table(title=f"Mercado {mercado} · {month:%Y-%m} · índice de presencia (0–100)")
    for column in (
        "#",
        "clínica",
        "combinado",
        "margen 95 %",
        "ChatGPT",
        "Google",
        "posición media",
        "cuota",
    ):
        table.add_column(column, justify="left" if column == "clínica" else "right")
    for i, r in enumerate(rows, start=1):
        table.add_row(
            str(i), r.name, _fmt(r.combined), f"{_fmt(r.ci_low, '')}–{_fmt(r.ci_high, '')}",
            _fmt(r.chatgpt), _fmt(r.google), _fmt(r.avg_position), _fmt(r.mention_share, " %"),
        )  # fmt: skip
    Console().print(table)
