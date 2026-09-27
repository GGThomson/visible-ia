# Fase C1 · Proyecto base

**Objetivo:** que el esqueleto funcione de punta a punta antes de escribir lógica.
- Paquete Python instalable, con una CLI que responde.
- Pruebas y CI en verde.
- Supabase dev/prod con el esquema inicial y RLS activado.
- Job diario que mantiene activos los dos proyectos.
- Landing vacía publicada en Cloudflare Pages.

**Historias que cubre:** — (infraestructura). Habilita todo el PRD.
**Estado:** 🟡 en curso
**Depende de (Director):** proyectos de Supabase dev/prod creados, claves en `.env` y en GitHub Secrets, cuenta de Cloudflare Pages conectada.

## Tareas

### C1-T01 · Paquete Python, herramientas y CLI "hola"
- **Estado:** ✅ (26/09, PR de `feat/C1-T01-python-package`)
- **Qué:** crear el paquete `visible_ia` en `src/`, gestionado con `uv`.
  - `pyproject.toml` con Python ≥ 3.12.
  - Dependencias base: `typer`, `pydantic`, `pydantic-settings`, `httpx`, `psycopg[binary]`.
  - Dependencias de desarrollo: `pytest`, `ruff`.
  - Script de consola `visible-ia`, con un comando `visible-ia version`.
- **Archivos probables:** `pyproject.toml`, `uv.lock`, `src/visible_ia/__init__.py`, `src/visible_ia/cli.py`, `tests/unit/test_cli.py`, `.python-version`
- **Criterios de aceptación:**
  - [ ] `uv sync` instala todo desde cero.
  - [ ] `uv run visible-ia version` imprime la versión (`0.1.0`).
  - [ ] `uv run ruff check .` y `uv run pytest` pasan.
- **Pruebas:** con `typer.testing.CliRunner`, que `version` salga con código 0 e imprima la versión.
- **Depende de:** —
- **Rama:** `feat/C1-T01-python-package`
- **Notas para Claude Code:**
  - Los scripts existentes de `scripts/` (prueba de la API de Gemini) **no** se tocan ni se importan desde el paquete.
  - Configurar `ruff` con `line-length = 100` y las reglas `E,F,I,UP,B`.
  - Nada de Poetry ni pip-tools: solo `uv`.

### C1-T02 · Configuración y `.env.example`
- **Estado:** ✅ (26/09, PR de `feat/C1-T02-config`)
- **Qué:** crear `config.py` con `pydantic-settings`.
  - Variables que lee (**ajustado el 26/09 a pedido del Director: un juego por entorno**): `VISIBLE_IA_ENV` (`dev`/`prod`); `SUPABASE_URL_*`, `SUPABASE_ANON_KEY_*`, `SUPABASE_SERVICE_ROLE_KEY_*` y `SUPABASE_DB_URL_*` para `DEV` y `PROD`; `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`; `OPENAI_API_KEY`, `SERPAPI_API_KEY`; `MONTHLY_BUDGET_USD` (10) y `SERPAPI_MONTHLY_QUOTA` (250).
  - Obligatorias para `config check`: las 3 de Supabase del entorno activo. Las demás se listan como "pendiente", con la tarea que las necesita.
  - `.env.example` con todas, sin valores.
  - Comando `visible-ia config check`: dice cuáles faltan **sin mostrar ningún valor**.
- **Archivos probables:** `src/visible_ia/config.py`, `.env.example`, `tests/unit/test_config.py`
- **Criterios de aceptación:**
  - [ ] Falta una variable obligatoria → `config check` la nombra y sale con código ≠ 0.
  - [ ] Ningún comando imprime claves. Hay una prueba que lo verifica con valores falsos.
  - [ ] `.env` sigue en `.gitignore`. `.env.example` se versiona.
- **Pruebas:** `monkeypatch` de variables de entorno; comprobar la salida de `config check`.
- **Depende de:** C1-T01
- **Rama:** `feat/C1-T02-config`
- **Notas para Claude Code:**
  - Claude Code **no puede leer ni escribir `.env`** (regla de permisos del proyecto). Pedir al Director que complete su `.env` a partir de `.env.example`.
  - Las claves se tipan como `SecretStr`.

### C1-T03 · Migración inicial del esquema + RLS activado
- **Estado:** ✅ (26/09, aplicada en **dev**; prod pendiente de confirmación del Director)
- **Cambio de método (26/09):** en lugar de `supabase db push` (requiere instalar la CLI de Supabase), las migraciones se aplican con `visible-ia db migrate [--env dev|prod] [--dry-run]`, que registra las versiones en `ops.schema_migrations` y en prod exige escribir "SI". La semilla de rubros va dentro de `0001_initial.sql`.
- **Qué:** crear `supabase/migrations/0001_initial.sql` con las tablas del modelo de datos de la arquitectura:
  - `rubro`, `plantilla`, `mercado`, `pregunta`, `clinica`, `clinica_mercado`, `alias`, `corrida`, `respuesta`, `mencion`, `fuente`, `puntaje_mensual`
  - `cliente`, `sede`, `usuario`, `tarea`, `informe`, `prospecto`, `pago`, `latido`
  - Con claves, restricciones, índices básicos y **RLS activado en todas las tablas** (sin políticas públicas, salvo el insert de `prospecto` que se hace en C6).
  - Semilla de los 4 rubros.
- **Archivos probables:** `supabase/config.toml`, `supabase/migrations/0001_initial.sql`, `supabase/seed.sql`, `tests/integration/test_schema.py`
- **Criterios de aceptación:**
  - [ ] `supabase db push` aplica la migración en **dev** sin errores. Lo ejecuta el Director o un workflow manual.
  - [ ] Todas las tablas tienen RLS activado. Una prueba consulta `pg_tables`/`pg_class` y falla si alguna no lo tiene.
  - [ ] `respuesta` tiene `purge_after` (fecha), que por defecto es la fecha de creación + 12 meses.
- **Pruebas:** integración contra Supabase dev (se marca `@pytest.mark.integration` y se salta si no hay `SUPABASE_DB_URL`).
- **Depende de:** C1-T02
- **Rama:** `feat/C1-T03-initial-schema`
- **Notas para Claude Code:**
  - Nombres de tablas y columnas en **inglés** en el SQL (convención del código), con un comentario que diga su nombre del documento (p. ej., `-- respuesta`). Por ejemplo: `markets`, `questions`, `clinics`, `runs`, `responses`, `mentions`, `sources`, `monthly_scores`, `clients`, `sites`, `app_users`, `tasks`, `reports`, `prospects`, `payments`, `heartbeats`.
  - La tabla `evento_webhook` **no** va aquí (es de la v1.2).

### C1-T04 · CI en GitHub Actions
- **Estado:** ✅ (26/09)
- **Qué:** workflow `ci.yml` que, en cada push y PR, instala con `uv`, corre `ruff check`, `ruff format --check` y `pytest` (sin las pruebas de integración).
- **Archivos probables:** `.github/workflows/ci.yml`
- **Criterios de aceptación:**
  - [ ] La CI pasa en `main` y en una rama de prueba.
  - [ ] Tarda < 3 minutos, con caché de `uv`.
- **Pruebas:** la propia ejecución del workflow.
- **Depende de:** C1-T01
- **Rama:** `feat/C1-T04-ci`
- **Notas para Claude Code:**
  - Usar `astral-sh/setup-uv`.
  - Solo runners Linux: los de Windows y macOS consumen más minutos.

### C1-T05 · Job diario: mantener activos Supabase dev y prod
- **Estado:** 🟡 código listo y probado en dev (26/09); el PR espera que el Director migre prod, porque el job escribe en producción. Falta la verificación a 8 días
- **Qué:** comando `visible-ia heartbeat` y workflow `diario.yml` (cron 1 vez al día + ejecución manual).
  - Por **cada** proyecto (dev y prod) hace 3 operaciones reales en la base de datos por la **API REST de Supabase**:
    1. `select` en `markets`.
    2. `insert` en `heartbeats`.
    3. `delete` de los latidos de más de 30 días.
  - Si algo falla, el workflow abre un issue.
- **Archivos probables:** `src/visible_ia/heartbeat.py`, `.github/workflows/diario.yml`, `tests/unit/test_heartbeat.py`
- **Criterios de aceptación:**
  - [ ] El workflow corre en ambos proyectos y deja una fila nueva en `heartbeats` en cada uno.
  - [ ] Si falla (p. ej., una clave incorrecta), aparece un issue "Heartbeat falló (dev|prod)".
  - [ ] **Verificación a 8 días:** el proyecto dev sigue activo sin otro uso. El Director lo anota en la bitácora (arquitectura: "Por confirmar en la semana 1").
- **Pruebas:** unitarias con `httpx.MockTransport`: se hacen las 3 llamadas y se manejan los errores.
- **Depende de:** C1-T03
- **Rama:** `feat/C1-T05-daily-heartbeat`
- **Notas para Claude Code:**
  - Usar la API REST (PostgREST) con la clave `service_role` desde los Secrets. Un `SELECT 1` por la conexión directa podría no contar como "user database activity".
  - Secrets por entorno: `SUPABASE_URL_DEV`/`_PROD`, `SUPABASE_SERVICE_ROLE_KEY_DEV`/`_PROD`.

### C1-T06 · Landing vacía publicada + README técnico
- **Estado:** 🟡 (26/09) publicación desde GitHub Actions (`web.yml`, wrangler) en lugar de la integración Git de Cloudflare: usa el token de Pages del Director
- **Qué:**
  - `web/index.html` con Pico CSS: nombre, una frase de valor y "Pronto: pide tu informe gratis".
  - Publicarla en Cloudflare Pages desde `main`, con vistas previas por rama.
  - Escribir el README técnico: cómo instalar, configurar `.env`, correr pruebas, aplicar migraciones y desplegar.
- **Archivos probables:** `web/index.html`, `README.md` (sección técnica), `docs/04-arquitectura/arquitectura.md` (URL de producción en "Entornos")
- **Criterios de aceptación:**
  - [ ] La landing se ve en `https://<proyecto>.pages.dev` y en el celular.
  - [ ] Un push a una rama genera una URL de vista previa.
  - [ ] Siguiendo solo el README, alguien puede instalar y correr las pruebas.
- **Pruebas:** revisión manual (el Director abre la URL en su celular).
- **Depende de:** C1-T01
- **Rama:** `feat/C1-T06-landing-readme`
- **Notas para Claude Code:**
  - Sin framework ni build: Cloudflare Pages sirve la carpeta `web/` tal cual.
  - Textos en español de Perú.
  - No prometer "puesto #1".

## Demo de la fase
- El Director ejecuta `uv run visible-ia version` y `uv run visible-ia config check` en su PC.
- Ve la CI en verde en GitHub.
- Ve las filas de `heartbeats` en Supabase dev y prod.
- Abre la landing en su celular.
