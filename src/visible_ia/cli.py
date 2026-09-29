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
    labels = {"up": "sube", "down": "baja", "no_clear_change": "sin cambio claro",
              "first_month": "primer mes"}  # fmt: skip
    columns = ("#", "clínica", "combinado", "margen 95 %", "ChatGPT", "Google", "posición media",
               "cuota", "cambio", "ventana 3 m")  # fmt: skip
    for column in columns:
        table.add_column(column, justify="left" if column == "clínica" else "right")
    for i, r in enumerate(rows, start=1):
        table.add_row(
            str(i), r.name, _fmt(r.combined), f"{_fmt(r.ci_low, '')}–{_fmt(r.ci_high, '')}",
            _fmt(r.chatgpt), _fmt(r.google), _fmt(r.avg_position), _fmt(r.mention_share, " %"),
            labels.get(r.change or "", "—"), _fmt(r.window3),
        )  # fmt: skip
    Console().print(table)


@puntaje_app.command("fuentes")
def puntaje_fuentes(
    mercado: int = typer.Argument(..., help="Id del mercado."),
    mes: str = typer.Option(None, help="AAAA-MM (por defecto, la última corrida revisada)."),
    top: int = typer.Option(5, min=1, help="Dominios por tipo."),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Qué fuentes usa la IA en el mercado, por tipo, con el % de respuestas (HU-12)."""
    from rich.console import Console
    from rich.table import Table

    from visible_ia.puntaje.fuentes import (
        TYPE_LABELS,
        latest_reviewed_month,
        load_citations,
        top_sources,
        type_shares,
    )
    from visible_ia.puntaje.indice import ScoreError

    with _connect_or_exit(_resolve_env(env)) as conn:
        try:
            month = _parse_month(mes) or latest_reviewed_month(conn, mercado)
        except ScoreError as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from None
        citations, total = load_citations(conn, mercado, month)
    if not total:
        typer.echo(f"Sin respuestas revisadas en {month:%Y-%m}.")
        raise typer.Exit(code=1)
    console = Console()
    shares = type_shares(citations, total)
    console.print(
        f"Mercado {mercado} · {month:%Y-%m} · {total} respuestas. Respuestas que citan cada tipo: "
        + ", ".join(f"{TYPE_LABELS[t]} {p:.0f} %" for t, p in shares.items())
    )
    table = Table()
    for column in ("tipo", "dominio", "respuestas", "% de respuestas", "ChatGPT", "Google"):
        table.add_column(column, justify="left" if column in ("tipo", "dominio") else "right")
    for source_type, rows in top_sources(citations, total, per_type=top).items():
        for r in rows:
            table.add_row(
                TYPE_LABELS[source_type], r.domain, str(r.answers), f"{r.share:.0f} %",
                str(r.by_surface["chatgpt_api"]), str(r.by_surface["google_ai_mode"]),
            )  # fmt: skip
    console.print(table)


@puntaje_app.command("brecha")
def puntaje_brecha(
    mercado: int = typer.Argument(..., help="Id del mercado."),
    mes: str = typer.Option(None, help="AAAA-MM (por defecto, el último calculado)."),
    min_rating: float = typer.Option(4.5, help="★ mínimas para marcar brecha."),
    min_resenas: int = typer.Option(100, help="Reseñas mínimas para marcar brecha."),
    max_indice: float = typer.Option(10.0, help="Índice combinado máximo (0–100)."),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Brecha Maps vs IA: bien valoradas en Maps pero casi ausentes en la IA (HU-13)."""
    from rich.console import Console
    from rich.table import Table

    from visible_ia.puntaje.brecha import gap_table
    from visible_ia.puntaje.indice import ScoreError

    with _connect_or_exit(_resolve_env(env)) as conn:
        try:
            month, rows = gap_table(
                conn, mercado, _parse_month(mes),
                min_rating=min_rating, min_reviews=min_resenas, max_index=max_indice,
            )  # fmt: skip
        except ScoreError as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from None
    table = Table(
        title=f"Mercado {mercado} · {month:%Y-%m} · brecha: ★ ≥ {min_rating}, "
        f"reseñas ≥ {min_resenas}, índice ≤ {max_indice:.0f}"
    )
    for column in ("clínica", "★", "reseñas", "dato del", "índice combinado", "brecha"):
        table.add_column(column, justify="left" if column == "clínica" else "right")
    for r in rows:
        table.add_row(
            r.name, _fmt(r.rating), "—" if r.reviews is None else str(r.reviews),
            "—" if r.data_date is None else f"{r.data_date:%d/%m/%Y}", _fmt(r.combined_index),
            "SÍ" if r.gap else "",
        )  # fmt: skip
    Console().print(table)


# --- reports (C6) --------------------------------------------------------------------------

informe_app = typer.Typer(help="Informes en PDF.", no_args_is_help=True)
app.add_typer(informe_app, name="informe")


# gpt-5-nano only picks sentence numbers: 3 calls of ~2,500 tokens (US$0.001); this cap is a
# conservative guard against the monthly budget before calling it.
REASONS_ESTIMATE_USD = 0.01


def _add_reasons(conn, data, settings, *, market_id: int, use_model: bool) -> None:
    """Literal reasons for the top competitors (C-008); the model cost goes to the budget."""
    from visible_ia.informes.contexto import reason_filter, reason_targets
    from visible_ia.informes.profundo import MODEL, ModelChooser, competitor_reasons
    from visible_ia.motor.presupuesto import month_usage, record_llm_cost

    chooser = None
    if use_model and data.deep_answers and settings.openai_api_key:
        spent = month_usage(conn).spent_usd
        if spent + REASONS_ESTIMATE_USD > settings.monthly_budget_usd:
            typer.echo("Frases de la competencia sin IA: el presupuesto del mes está al límite.")
        else:
            import openai

            from visible_ia.motor.chatgpt_api import TIMEOUT_SECONDS
            from visible_ia.motor.tarifas import openai_rates

            client = openai.OpenAI(
                api_key=settings.openai_api_key.get_secret_value(),
                max_retries=1,
                timeout=TIMEOUT_SECONDS,
            )
            chooser = ModelChooser(client, openai_rates())
    elif use_model and data.deep_answers:
        typer.echo("Frases de la competencia sin IA: falta OPENAI_API_KEY.")
    data.reasons = competitor_reasons(
        reason_targets(data), data.deep_answers, data.market_names, chooser, reason_filter(data)
    )
    if chooser and chooser.calls:
        record_llm_cost(
            conn, "diagnostic_reasons", model=MODEL, calls=chooser.calls,
            cost_usd=chooser.cost_usd, market_id=market_id,
            clinic_id=data.clinic.id, month=data.month,
        )  # fmt: skip
        typer.echo(
            f"Frases elegidas con {MODEL}: {chooser.calls} llamadas, "
            f"US${chooser.cost_usd:.4f} (registrado en el presupuesto del mes)."
        )


def _diagnostic_pdf(conn, settings, clinic_id, market_id, month, chosen, use_model, out_dir):
    """Loads the stored data, picks the reasons and writes the free diagnostic (HTML + PDF).
    Raises ScoreError or PdfError. Returns (data, path of the PDF)."""
    from visible_ia.informes.contexto import (
        MAX_PAGES,
        build_context,
        load_brand,
        load_report_data,
    )
    from visible_ia.informes.pdf import html_to_pdf, page_count, report_filename
    from visible_ia.informes.render import diagnostic_frame, render_diagnostic

    data = load_report_data(conn, clinic_id, market_id, month, chosen)
    _add_reasons(conn, data, settings, market_id=market_id, use_model=use_model)
    path = out_dir / report_filename(data.clinic.name, data.month)
    path.parent.mkdir(parents=True, exist_ok=True)
    for compact in (False, True):  # over the page limit: again with one example answer
        context = build_context(data, load_brand(), compact=compact)
        html = render_diagnostic(context)
        path.with_suffix(".html").write_text(html, encoding="utf-8")
        html_to_pdf(html, path, *diagnostic_frame(context))
        if page_count(path) <= MAX_PAGES:
            break
    else:
        typer.echo(f"Aviso: {path.name} tiene {page_count(path)} páginas (máximo {MAX_PAGES}).")
    return data, path


@informe_app.command("diagnostico")
def informe_diagnostico(
    clinica: int = typer.Option(..., help="Id de la clínica prospecto."),
    mercado: int = typer.Option(..., help="Id del mercado."),
    competidores: str = typer.Option(
        None, help="Ids separados por coma (por defecto, los 3 mejores del ranking)."
    ),
    mes: str = typer.Option(None, help="AAAA-MM (por defecto, el último calculado)."),
    subir: bool = typer.Option(
        True, "--subir/--sin-subir", help="Subir el PDF a Supabase Storage y registrarlo."
    ),
    ia: bool = typer.Option(
        True, "--ia/--sin-ia", help="Elegir las frases de la competencia con gpt-5-nano (C-008)."
    ),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Genera el informe gratis de diagnóstico en PDF (HU-14, C-008)."""
    import time

    from visible_ia.informes.pdf import OUTPUT_DIR, PdfError, record_report, upload
    from visible_ia.puntaje.indice import ScoreError

    started = time.monotonic()
    target = _resolve_env(env)
    chosen = [int(c) for c in competidores.split(",")] if competidores else None
    settings = get_settings()
    with _connect_or_exit(target, autocommit=True) as conn:
        try:
            data, path = _diagnostic_pdf(
                conn, settings, clinica, mercado, _parse_month(mes), chosen, ia, OUTPUT_DIR
            )
        except (ScoreError, PdfError) as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from None
        typer.echo(f"PDF: {path} ({path.stat().st_size / 1024:.0f} KB)")
        if subir:
            _confirm_prod(target)
            url = settings.value(f"SUPABASE_URL_{target.upper()}")
            key = settings.value(f"SUPABASE_SERVICE_ROLE_KEY_{target.upper()}")
            try:
                stored = upload(
                    path,
                    f"diagnostico/{path.name}",
                    supabase_url=url,
                    service_role_key=key.get_secret_value(),
                )
            except PdfError as exc:
                typer.echo(f"No se pudo subir: {exc}")
                raise typer.Exit(code=1) from None
            report_id = record_report(conn, data.clinic.id, data.month, stored)
            typer.echo(f"Subido a Storage ({stored}) y registrado como informe {report_id}.")
    typer.echo(f"Listo en {time.monotonic() - started:.0f} s.")


diagnostico_app = typer.Typer(help="Diagnósticos gratis en lote (C-010).", no_args_is_help=True)
app.add_typer(diagnostico_app, name="diagnostico")


@diagnostico_app.command("lote")
def diagnostico_lote(
    archivo: Path = typer.Argument(..., help="Texto con un nombre o id por línea (# comenta)."),
    mercado: int = typer.Option(..., help="Id del mercado."),
    mes: str = typer.Option(None, help="AAAA-MM de los datos (por defecto, el último calculado)."),
    ia: bool = typer.Option(
        True, "--ia/--sin-ia", help="Elegir las frases de la competencia con gpt-5-nano."
    ),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Genera el diagnóstico gratis y un primer mensaje de WhatsApp por cada nombre de la
    lista, solo con datos ya medidos (sin corridas nuevas)."""
    from visible_ia.informes.contexto import load_brand, load_market_names
    from visible_ia.informes.lote import UnknownName, match, read_list, whatsapp_message
    from visible_ia.informes.pdf import OUTPUT_DIR, PdfError, slug
    from visible_ia.nicho import load_niche
    from visible_ia.puntaje.indice import ScoreError

    lines = read_list(archivo.read_text(encoding="utf-8"))
    if not lines:
        typer.echo(f"{archivo} no tiene nombres.")
        raise typer.Exit(code=2)
    target = _resolve_env(env)
    settings, niche, brand = get_settings(), load_niche(), load_brand()
    month = _parse_month(mes)
    messages, failed = [], []
    with _connect_or_exit(target, autocommit=True) as conn:
        names = load_market_names(conn, mercado)
        for line in lines:
            try:
                cid = match(line, names)
                out = OUTPUT_DIR / "diagnosticos" / (f"{month:%Y-%m}" if month else "ultimo")
                data, path = _diagnostic_pdf(conn, settings, cid, mercado, month, None, ia, out)
            except (UnknownName, ScoreError, PdfError) as exc:
                failed.append(line)
                typer.echo(f"✗ {exc}")
                continue
            text = whatsapp_message(data, niche, brand)
            path.with_name(f"whatsapp-{slug(data.clinic.name)}.txt").write_text(
                text + "\n", encoding="utf-8"
            )
            messages.append((data.clinic.name, path, text))
            typer.echo(f"✓ {data.clinic.name}: {path.name}")
    if messages:
        summary = messages[0][1].parent / "mensajes.md"
        blocks = [f"## {name}\n\nPDF: {path.name}\n\n{text}\n" for name, path, text in messages]
        summary.write_text("\n".join(blocks), encoding="utf-8")
        typer.echo(f"{len(messages)} diagnósticos y mensajes en {summary.parent}")
    if failed:
        typer.echo(f"Sin generar ({len(failed)}): {', '.join(failed)}")
        raise typer.Exit(code=1)


@informe_app.command("crear-bucket")
def informe_crear_bucket(env: str = typer.Option(None, help="dev o prod.")) -> None:
    """Crea el bucket privado 'informes' en Supabase Storage (una vez por entorno)."""
    from visible_ia.informes.pdf import PdfError, ensure_bucket

    target = _resolve_env(env)
    _confirm_prod(target)
    settings = get_settings()
    try:
        created = ensure_bucket(
            supabase_url=settings.value(f"SUPABASE_URL_{target.upper()}"),
            service_role_key=settings.value(
                f"SUPABASE_SERVICE_ROLE_KEY_{target.upper()}"
            ).get_secret_value(),
        )
    except PdfError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from None
    typer.echo("Bucket 'informes' creado (privado)." if created else "El bucket ya existía.")


# --- prospects (C6-T04) --------------------------------------------------------------------

prospectos_app = typer.Typer(help="Pedidos de informe gratis de la landing.", no_args_is_help=True)
app.add_typer(prospectos_app, name="prospectos")


@prospectos_app.command("nuevos")
def prospectos_nuevos(
    marcar: bool = typer.Option(True, "--marcar/--no-marcar", help="Marcarlos como vistos."),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Lista los pedidos no vistos (con contacto) y los marca como vistos."""
    from rich.console import Console
    from rich.table import Table

    from visible_ia.prospectos import CATEGORY_NAMES, list_unseen, mark_seen

    target = _resolve_env(env)
    with _connect_or_exit(target, autocommit=True) as conn:
        rows = list_unseen(conn)
        if not rows:
            typer.echo("No hay pedidos nuevos.")
            return
        table = Table(title=f"{len(rows)} pedidos nuevos ({target})")
        for column in ("fecha", "nombre", "clínica", "rubro", "distrito", "contacto", "origen"):
            table.add_column(column)
        for p in rows:
            table.add_row(
                f"{p.created_at:%d/%m %H:%M}", p.name, p.clinic_name,
                CATEGORY_NAMES.get(p.category_code or "", "—"), p.district or "—",
                p.contact, p.source or "—",
            )  # fmt: skip
        Console().print(table)
        if marcar:
            mark_seen(conn, [p.id for p in rows])
            typer.echo("Marcados como vistos.")


@prospectos_app.command("aviso")
def prospectos_aviso(env: str = typer.Option("prod", help="dev o prod.")) -> None:
    """Abre, actualiza o cierra el issue "Prospectos nuevos (n)" (para el job diario)."""
    import os

    from visible_ia.prospectos import sync_issue, unseen_clinics

    target = _resolve_env(env)
    settings = get_settings()
    url = settings.value(f"SUPABASE_URL_{target.upper()}")
    key = settings.value(f"SUPABASE_SERVICE_ROLE_KEY_{target.upper()}")
    token, repo = os.environ.get("GITHUB_TOKEN"), os.environ.get("GITHUB_REPOSITORY")
    if not (url and key and token and repo):
        typer.echo(
            "Faltan SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, GITHUB_TOKEN o GITHUB_REPOSITORY"
        )
        raise typer.Exit(code=1)
    clinics = unseen_clinics(url, key.get_secret_value())
    result = sync_issue(clinics, repo=repo, token=token)
    typer.echo(f"Prospectos sin revisar ({target}): {len(clinics)} · issue: {result}")


# --- clients, sites and panel users (C7) ---------------------------------------------------

cliente_app = typer.Typer(help="Clientes (clínicas y agencias).", no_args_is_help=True)
app.add_typer(cliente_app, name="cliente")
sede_app = typer.Typer(help="Sedes de un cliente (clínica × mercado).", no_args_is_help=True)
app.add_typer(sede_app, name="sede")
usuario_app = typer.Typer(help="Usuarios del panel.", no_args_is_help=True)
app.add_typer(usuario_app, name="usuario")

KIND_BY_TIPO = {"clinica": "clinic", "clínica": "clinic", "agencia": "agency"}


@cliente_app.command("crear")
def cliente_crear(
    nombre: str = typer.Option(..., help="Nombre del cliente."),
    tipo: str = typer.Option("clinica", help="clinica o agencia."),
    correo: str = typer.Option(None, help="Correo de contacto."),
    telefono: str = typer.Option(None, help="WhatsApp o teléfono de contacto."),
    agencia: int = typer.Option(None, help="Id de la agencia (si la clínica es de una agencia)."),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Crea un cliente."""
    from visible_ia.clientes import ClientError, create_client

    kind = KIND_BY_TIPO.get(tipo.lower())
    if kind is None:
        typer.echo("Tipo no válido: usa clinica o agencia.")
        raise typer.Exit(code=2)
    target = _resolve_env(env)
    _confirm_prod(target)
    with _connect_or_exit(target, autocommit=True) as conn:
        try:
            client_id = create_client(
                conn, kind, nombre, email=correo, phone=telefono, agency_id=agencia
            )
        except ClientError as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from None
    typer.echo(
        f"Cliente {client_id} creado: {nombre}. Agrega su sede: "
        f"visible-ia sede agregar {client_id} --clinica <id> --mercado <id>"
    )


@cliente_app.command("listar")
def cliente_listar(env: str = typer.Option(None, help="dev o prod.")) -> None:
    """Lista los clientes con sus sedes activas y usuarios."""
    from visible_ia.clientes import list_clients

    with _connect_or_exit(_resolve_env(env)) as conn:
        rows = list_clients(conn)
    if not rows:
        typer.echo("No hay clientes.")
    for cid, kind, name, status, sites, users in rows:
        tipo = "clínica" if kind == "clinic" else "agencia"
        typer.echo(f"{cid:>4}  {name}  ({tipo}, {status}) · {sites} sedes · {users} usuarios")


@sede_app.command("agregar")
def sede_agregar(
    cliente: int = typer.Argument(..., help="Id del cliente."),
    clinica: int = typer.Option(..., help="Id de la clínica (visible-ia clinicas listar)."),
    mercado: int = typer.Option(..., help="Id del mercado."),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Agrega una sede (una clínica de un mercado) al cliente."""
    from visible_ia.clientes import ClientError, add_site

    target = _resolve_env(env)
    _confirm_prod(target)
    with _connect_or_exit(target, autocommit=True) as conn:
        try:
            site_id, created = add_site(conn, cliente, clinica, mercado)
        except ClientError as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from None
    typer.echo(f"Sede {site_id} {'agregada' if created else 'ya existía'}.")


@usuario_app.command("invitar")
def usuario_invitar(
    cliente: int = typer.Argument(..., help="Id del cliente."),
    correo: str = typer.Argument(..., help="Correo del usuario."),
    enlace: bool = typer.Option(
        False, "--enlace", help="No enviar correo: mostrar el enlace para mandarlo por WhatsApp."
    ),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Da acceso al panel: crea el usuario (si no existe) y envía o muestra el enlace mágico."""
    from visible_ia.clientes import AuthAdmin, ClientError, invite_user

    target = _resolve_env(env)
    _confirm_prod(target)
    settings = get_settings()
    auth = AuthAdmin(
        settings.value(f"SUPABASE_URL_{target.upper()}"),
        settings.value(f"SUPABASE_SERVICE_ROLE_KEY_{target.upper()}").get_secret_value(),
    )
    with _connect_or_exit(target, autocommit=True) as conn:
        try:
            result = invite_user(
                conn, auth, cliente, correo, site_url=settings.site_url, link_only=enlace
            )
        except ClientError as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from None
    state = "nuevo" if result.created else "ya existía (no se duplicó)"
    typer.echo(f"Usuario {result.email}: {state}, vinculado al cliente {cliente}.")
    if result.link:
        typer.echo(f"Enlace de acceso (de un solo uso, vence pronto): {result.link}")
    else:
        typer.echo("Supabase le envió el enlace por correo.")


# --- monthly run (C8-T01) ------------------------------------------------------------------

mensual_app = typer.Typer(help="Corrida mensual de los mercados activos.", no_args_is_help=True)
app.add_typer(mensual_app, name="mensual")


def _month_plan(conn, settings):
    from visible_ia.motor.mensual import plan_month
    from visible_ia.motor.presupuesto import month_usage

    usage = month_usage(conn, serpapi_account_used=_serpapi_account_used(settings))
    return plan_month(
        conn,
        usage,
        budget_usd=settings.monthly_budget_usd,
        serpapi_quota=settings.serpapi_monthly_quota,
    )


def _post_issue(prefix, title, body, *, close=False):
    import os

    from visible_ia.github_issues import upsert_issue

    token, repo = os.environ.get("GITHUB_TOKEN"), os.environ.get("GITHUB_REPOSITORY")
    if not (token and repo):
        typer.echo("(sin GITHUB_TOKEN/GITHUB_REPOSITORY: no se publica el issue)")
        return
    typer.echo(
        f"Issue '{prefix}': "
        f"{upsert_issue(prefix, title, body, repo=repo, token=token, close=close)}"
    )


@mensual_app.command("estimar")
def mensual_estimar(
    issue: bool = typer.Option(False, "--issue", help="Publicar la estimación como issue."),
    env: str = typer.Option("prod", help="dev o prod."),
) -> None:
    """Estima la corrida del mes de los mercados activos. No gasta nada."""
    from visible_ia.motor.mensual import ESTIMATE_PREFIX, estimate_issue

    target = _resolve_env(env)
    settings = get_settings()
    with _connect_or_exit(target) as conn:
        plan = _month_plan(conn, settings)
    title, body = estimate_issue(plan)
    typer.echo(f"{title}\n\n{body}")
    if issue:
        _post_issue(f"{ESTIMATE_PREFIX} ", title, body)


@mensual_app.command("correr")
def mensual_correr(
    issue: bool = typer.Option(False, "--issue", help="Publicar el resultado como issue."),
    env: str = typer.Option("prod", help="dev o prod."),
) -> None:
    """Corre (o retoma) el mes de los mercados activos y extrae. Pensado para el workflow:
    lanzarlo a mano ES la aprobación del Director; nunca supera el presupuesto."""
    import openai

    from visible_ia.extractor import llm
    from visible_ia.motor.mensual import (
        ESTIMATE_PREFIX,
        REVIEW_PREFIX,
        SURFACES,
        estimate_issue,
        review_issue,
        run_month,
    )

    target = _resolve_env(env)
    settings = get_settings()
    with _connect_or_exit(target, autocommit=True) as conn:
        plan = _month_plan(conn, settings)
        if not plan.fits:
            title, body = estimate_issue(plan)
            typer.echo(f"No se corre: supera el presupuesto o la cuota.\n\n{body}")
            if issue:
                _post_issue(f"{ESTIMATE_PREFIX} ", title, body)
            raise typer.Exit(code=1)
        clients = _engine_clients(settings, SURFACES)
        oa = openai.OpenAI(
            api_key=_openai_key(settings), max_retries=0, timeout=llm.TIMEOUT_SECONDS
        )
        prompt = llm.load_prompt()

        def extractor(text, links):
            return llm.extract(text, link_texts=links, client=oa, prompt=prompt)

        typer.echo(f"Corriendo {len(plan.markets)} mercados (≈ US${plan.estimated_usd:.2f})…")
        results = run_month(conn, plan, clients, extractor)
    title, body = review_issue(plan.month, results)
    typer.echo(f"{title}\n\n{body}")
    if issue:
        _post_issue(f"{REVIEW_PREFIX} ", title, body)
        _post_issue(f"{ESTIMATE_PREFIX} ", None, "Aprobada y ejecutada: ver " + title, close=True)
    if any(r.failures for r in results):
        raise typer.Exit(code=1)


# --- checklist (C8-T03) --------------------------------------------------------------------

checklist_app = typer.Typer(help="Checklist priorizado de cada sede.", no_args_is_help=True)
app.add_typer(checklist_app, name="checklist")


@checklist_app.command("generar")
def checklist_generar(
    sede: int = typer.Argument(None, help="Id de la sede (sin id: todas las sedes activas)."),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Crea o actualiza el checklist priorizado (las tareas hechas se mantienen)."""
    from visible_ia.checklist import generate

    target = _resolve_env(env)
    _confirm_prod(target)
    with _connect_or_exit(target, autocommit=True) as conn:
        if sede is None:
            with conn.cursor() as cur:
                cur.execute("select id from public.sites where active_to is null order by id")
                sites = [r[0] for r in cur.fetchall()]
        else:
            sites = [sede]
        for site_id in sites:
            tasks = generate(conn, site_id)
            typer.echo(f"Sede {site_id}: " + " → ".join(t.code for t in tasks))
    if not sites:
        typer.echo("No hay sedes activas.")


@sede_app.command("schema")
def sede_schema(
    sede: int = typer.Argument(..., help="Id de la sede."),
    telefono: str = typer.Option(None, help="Con código de país, p. ej. +51 1 234 5678."),
    horario: list[str] = typer.Option(
        None, help="Repetible, formato schema.org: 'Mo-Fr 09:00-19:00', 'Sa 09:00-13:00'."
    ),
    otra_url: list[str] = typer.Option(None, help="Otros perfiles (Doctoralia, Facebook…)."),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Genera el schema JSON-LD de la sede, listo para pegar en su web (HU-18)."""
    from visible_ia.jsonld import build, script_tag, validate

    with _connect_or_exit(_resolve_env(env)) as conn, conn.cursor() as cur:
        cur.execute(
            "select c.name, m.category_code, m.district, c.address, c.website, c.instagram, "
            "c.maps_url from public.sites s join public.clinics c on c.id = s.clinic_id "
            "join public.markets m on m.id = s.market_id where s.id = %s",
            (sede,),
        )
        row = cur.fetchone()
    if row is None:
        typer.echo(f"No existe la sede {sede}")
        raise typer.Exit(code=1)
    name, category, district, address, website, instagram, maps_url = row
    data = build(
        name=name, category=category, district=district, address=address, website=website,
        instagram=instagram, maps_url=maps_url, phone=telefono, opening_hours=horario or None,
        extra_same_as=otra_url or None,
    )  # fmt: skip
    errors = validate(data)
    if errors:
        typer.echo("El schema tiene problemas:\n- " + "\n- ".join(errors))
        raise typer.Exit(code=1)
    typer.echo(script_tag(data))


@informe_app.command("mensual")
def informe_mensual(
    sede: int = typer.Option(..., help="Id de la sede."),
    mes: str = typer.Option(..., help="AAAA-MM."),
    subir: bool = typer.Option(
        True, "--subir/--sin-subir", help="Subir el PDF a Supabase Storage y registrarlo."
    ),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Genera el reporte mensual de una sede en PDF (HU-15)."""
    from visible_ia.informes.contexto import load_brand
    from visible_ia.informes.mensual import build_monthly_context, load_monthly_data
    from visible_ia.informes.pdf import OUTPUT_DIR, PdfError, html_to_pdf, slug, upload
    from visible_ia.informes.render import render_monthly

    target = _resolve_env(env)
    month = _parse_month(mes)
    settings = get_settings()
    with _connect_or_exit(target, autocommit=True) as conn:
        try:
            data = load_monthly_data(conn, sede, month)
            html = render_monthly(build_monthly_context(data, load_brand()))
        except ValueError as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from None
        path = OUTPUT_DIR / f"mensual-{slug(data.clinic_name)}-{month:%Y-%m}.pdf"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.with_suffix(".html").write_text(html, encoding="utf-8")
        try:
            html_to_pdf(html, path)
        except PdfError as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from None
        typer.echo(f"PDF: {path} ({path.stat().st_size / 1024:.0f} KB)")
        if subir:
            _confirm_prod(target)
            stored = upload(
                path,
                f"mensual/{path.name}",
                supabase_url=settings.value(f"SUPABASE_URL_{target.upper()}"),
                service_role_key=settings.value(
                    f"SUPABASE_SERVICE_ROLE_KEY_{target.upper()}"
                ).get_secret_value(),
            )
            with conn.transaction(), conn.cursor() as cur:
                cur.execute(
                    "insert into public.reports (kind, site_id, month, pdf_path) "
                    "values ('monthly', %s, %s, %s) returning id",
                    (sede, month, stored),
                )
                typer.echo(f"Subido ({stored}) y registrado como informe {cur.fetchone()[0]}.")


# --- manual payments (C9-T01) --------------------------------------------------------------

pago_app = typer.Typer(help="Registro de pagos manuales.", no_args_is_help=True)
app.add_typer(pago_app, name="pago")
pagos_app = typer.Typer(help="Estado de pagos de los clientes.", no_args_is_help=True)
app.add_typer(pagos_app, name="pagos")


def _parse_day(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        typer.echo(f"Fecha no válida: {value} (usa AAAA-MM-DD)")
        raise typer.Exit(code=2) from None


@pago_app.command("registrar")
def pago_registrar(
    cliente: int = typer.Argument(..., help="Id del cliente (visible-ia cliente listar)."),
    monto: str = typer.Option(..., help="Monto cobrado en soles, p. ej. 349."),
    medio: str = typer.Option(..., help="link, yape o transferencia."),
    periodo: str = typer.Option(..., help="Mes que paga, AAAA-MM."),
    ref: str = typer.Option(None, help="N.º de operación o referencia."),
    fecha: str = typer.Option(None, help="Fecha del pago, AAAA-MM-DD (por defecto, hoy)."),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Registra un pago manual (link de pago, Yape o transferencia)."""
    from visible_ia.pagos import (
        PaymentError,
        month_name,
        parse_amount,
        register_payment,
        today_lima,
    )

    target = _resolve_env(env)
    period = _parse_month(periodo)
    paid_on = _parse_day(fecha) or today_lima()
    try:
        amount = parse_amount(monto)
    except PaymentError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=2) from None
    _confirm_prod(target)
    with _connect_or_exit(target, autocommit=True) as conn:
        try:
            payment_id, repeated = register_payment(
                conn, cliente, amount, medio.lower(), period, paid_on=paid_on, reference=ref
            )
        except PaymentError as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from None
    typer.echo(
        f"Pago {payment_id} registrado: cliente {cliente}, S/ {amount:.2f} por "
        f"{month_name(period)} ({medio.lower()}, {paid_on:%d/%m/%Y})."
    )
    if repeated:
        typer.echo(f"Ojo: {month_name(period)} ya tenía otro pago de este cliente.")


@pagos_app.command("estado")
def pagos_estado(
    fecha: str = typer.Option(None, help="Calcular a esta fecha, AAAA-MM-DD (por defecto, hoy)."),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Muestra qué clientes están al día, cuáles vencen pronto y cuáles están atrasados."""
    from rich.console import Console
    from rich.table import Table

    from visible_ia.pagos import client_statuses, month_name, month_total, net_of_igv, today_lima

    target = _resolve_env(env)
    settings = get_settings()
    today = _parse_day(fecha) or today_lima()
    with _connect_or_exit(target) as conn:
        statuses = client_statuses(
            conn, today, grace_days=settings.pago_dias_gracia, notice_days=settings.pago_aviso_dias
        )
        total = month_total(conn, today.replace(day=1))
    if not statuses:
        typer.echo("No hay clientes activos que paguen directamente.")
    else:
        table = Table(title=f"Pagos al {today:%d/%m/%Y} ({target})")
        for column in ("id", "cliente", "estado", "detalle"):
            table.add_column(column)
        colors = {"al día": "green", "vence pronto": "yellow", "atrasado": "red"}
        for s in statuses:
            table.add_row(str(s.client_id), s.name, f"[{colors[s.status]}]{s.status}[/]", s.detail)
        Console().print(table)
    net = net_of_igv(total, includes_igv=settings.pagos_incluyen_igv)
    igv_note = "sin IGV" if settings.pagos_incluyen_igv else "los montos se toman sin IGV"
    typer.echo(
        f"Cobrado en {month_name(today.replace(day=1))}: S/ {total:.2f} · neto S/ {net:.2f} "
        f"({igv_note}; ajusta PAGOS_INCLUYEN_IGV cuando el contador defina el régimen)"
    )


@pagos_app.command("aviso")
def pagos_aviso(env: str = typer.Option("prod", help="dev o prod.")) -> None:
    """Abre, actualiza o cierra el issue "Pagos atrasados (n)" (para el job diario)."""
    from visible_ia.pagos import ISSUE_PREFIX, client_statuses, overdue_issue, today_lima

    target = _resolve_env(env)
    settings = get_settings()
    with _connect_or_exit(target) as conn:
        statuses = client_statuses(
            conn,
            today_lima(),
            grace_days=settings.pago_dias_gracia,
            notice_days=settings.pago_aviso_dias,
        )
    notice = overdue_issue(statuses)
    late = sum(s.status == "atrasado" for s in statuses)
    typer.echo(f"Clientes con pago atrasado ({target}): {late}")
    if notice is None:
        _post_issue(f"{ISSUE_PREFIX} ", None, "Ya no hay pagos atrasados.", close=True)
    else:
        _post_issue(f"{ISSUE_PREFIX} ", *notice)


# --- attribution kit (C9-T02) --------------------------------------------------------------

atribucion_app = typer.Typer(help="Pacientes que llegan por la IA (kit de atribución).",
                             no_args_is_help=True)  # fmt: skip
app.add_typer(atribucion_app, name="atribucion")


@atribucion_app.command("registrar")
def atribucion_registrar(
    sede: int = typer.Argument(..., help="Id de la sede."),
    mes: str = typer.Option(..., help="AAAA-MM."),
    pacientes: int = typer.Option(..., min=0, help="Pacientes que llegaron por la IA ese mes."),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Guarda el conteo del mes cuando la clínica lo envía por WhatsApp (en vez del panel)."""
    from visible_ia.atribucion import save_count

    target = _resolve_env(env)
    month = _parse_month(mes)
    _confirm_prod(target)
    with _connect_or_exit(target, autocommit=True) as conn:
        try:
            save_count(conn, sede, month, pacientes)
        except ValueError as exc:
            typer.echo(str(exc))
            raise typer.Exit(code=1) from None
    typer.echo(f"Sede {sede}: {pacientes} pacientes por IA en {mes}.")


@informe_app.command("kit")
def informe_kit(
    sede: int = typer.Option(..., help="Id de la sede."),
    env: str = typer.Option(None, help="dev o prod."),
) -> None:
    """Genera el kit de atribución de una sede en PDF, para enviarlo por WhatsApp (HU-25)."""
    from visible_ia.atribucion import kit_context
    from visible_ia.clientes import PANEL_PATH
    from visible_ia.informes.contexto import load_brand
    from visible_ia.informes.pdf import OUTPUT_DIR, PdfError, html_to_pdf, slug
    from visible_ia.informes.render import render_kit

    target = _resolve_env(env)
    settings = get_settings()
    with _connect_or_exit(target) as conn, conn.cursor() as cur:
        cur.execute(
            "select c.name, c.website from public.sites s "
            "join public.clinics c on c.id = s.clinic_id where s.id = %s",
            (sede,),
        )
        row = cur.fetchone()
    if row is None:
        typer.echo(f"No existe la sede {sede}")
        raise typer.Exit(code=1)
    name, website = row
    panel = settings.site_url.rstrip("/") + PANEL_PATH
    html = render_kit(kit_context(name, website, load_brand(), panel))
    path = OUTPUT_DIR / f"kit-atribucion-{slug(name)}.pdf"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.with_suffix(".html").write_text(html, encoding="utf-8")
    try:
        html_to_pdf(html, path)
    except PdfError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from None
    typer.echo(f"PDF: {path} ({path.stat().st_size / 1024:.0f} KB)")
