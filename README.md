# visible-ia

Mide cada mes si **ChatGPT** y **Google (Modo IA)** recomiendan a una clínica de Lima cuando un paciente pregunta por su especialidad y distrito, frente a su competencia. Especificación: [PRD](docs/03-especificacion/prd.md) · arquitectura: [arquitectura.md](docs/04-arquitectura/arquitectura.md) · plan: [roadmap](docs/05-plan/roadmap.md) · estado: [ESTADO](memoria/ESTADO.md).

## Guía técnica

### Requisitos
- Python (cualquier versión reciente) y [`uv`](https://docs.astral.sh/uv/): `python -m pip install --user uv`. `uv` descarga solo Python 3.12 para el proyecto (`.python-version`).
- Opcional: [GitHub CLI](https://cli.github.com/) (`gh`) para PRs y Secrets.

### Instalar y configurar
```powershell
uv sync                              # instala dependencias (uv.lock)
Copy-Item .env.example .env          # luego pega los valores en .env (nunca se sube a Git)
uv run visible-ia config check       # dice qué variables faltan, sin mostrar valores
uv run visible-ia config check --env prod
uv run playwright install chromium   # una vez: navegador para generar los informes en PDF
```
Si `uv` no se reconoce en la terminal, usa `python -m uv`.

### Informe gratis de diagnóstico (PDF)
```powershell
uv run visible-ia informe crear-bucket --env prod     # una vez por entorno: bucket privado "informes"
uv run visible-ia informe diagnostico --clinica <id> --mercado <id> --env prod
```
Por defecto compara con los 3 mejores del ranking (`--competidores a,b,c` para elegir otros). El PDF queda en `salida/` (fuera de Git), se sube al bucket privado y se registra en `reports`. Con `--sin-subir` solo se genera el archivo local. La marca (nombre, colores, logo, contacto) está en `src/visible_ia/informes/marca.toml`.

### Pagos manuales
```powershell
uv run visible-ia pago registrar <cliente> --monto 349 --medio yape --periodo 2026-10 --ref <n.º op.> --env prod
uv run visible-ia pagos estado --env prod     # al día / vence pronto / atrasado
```
Cada pago cubre un mes (`--periodo`), por adelantado. Un mes vence el día 1 (o el día en que se creó el cliente) más `PAGO_DIAS_GRACIA` (5); "vence pronto" avisa `PAGO_AVISO_DIAS` (7) antes del mes siguiente. Las clínicas de una agencia no aparecen: se cobra a la agencia. Con `PAGOS_INCLUYEN_IGV=true`, el neto descuenta el 18 %.

### Kit de atribución (pacientes que llegan por la IA)
```powershell
uv run visible-ia informe kit --sede <id> --env prod                          # PDF en salida/ para enviar por WhatsApp
uv run visible-ia atribucion registrar <sede> --mes 2026-10 --pacientes 3 --env prod   # si la clínica lo manda por WhatsApp
```
La clínica también lo registra en su panel (sección «Pacientes que llegan por la IA»); el reporte mensual muestra el conteo del mes.

### Pruebas y estilo
```powershell
uv run ruff check .                  # estilo
uv run ruff format .                 # formato
uv run pytest                        # pruebas unitarias (las que usa la CI)
uv run pytest -m integration         # contra Supabase dev (necesita SUPABASE_DB_URL_DEV)
```
Las pruebas `live` llaman a APIs de pago y solo se corren a mano (`-m live`).

### Base de datos (Supabase)
```powershell
uv run visible-ia db status --env dev
uv run visible-ia db migrate --env dev          # aplica supabase/migrations/NNNN_*.sql en orden
uv run visible-ia db migrate --env prod         # pide escribir SI
```
Todas las tablas tienen RLS activado; las políticas se agregan en migraciones propias.

### Automatizaciones (GitHub Actions)
| Workflow | Cuándo | Qué hace |
|---|---|---|
| `ci.yml` | push a `main`, PRs | ruff + pytest |
| `diario.yml` | cada día 07:17 (Lima) y a mano | latido en Supabase dev y prod para que no se pausen (si falla, abre un issue); issues de prospectos nuevos y de **pagos atrasados** |
| `web.yml` | cambios en `web/` | publica `web/` en Cloudflare Pages: `main` → producción, PR → URL de vista previa |

**GitHub Secrets** que usan: `SUPABASE_URL_DEV/PROD`, `SUPABASE_SERVICE_ROLE_KEY_DEV/PROD`, `SUPABASE_DB_URL_DEV/PROD`, `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`. Para cargar uno desde tu `.env` sin copiarlo a mano:
```powershell
uv run python -c "from visible_ia.config import get_settings; print(get_settings().supabase_url_dev)" | gh secret set SUPABASE_URL_DEV
```

### Web
`web/` es un sitio estático (HTML + Pico CSS, sin build). Para verlo en local: `python -m http.server -d web 8000` y abrir http://localhost:8000.

---

# 🧭 Método de trabajo: plantilla de proyecto con equipo de IAs

Sistema reutilizable para llevar **cualquier proyecto de programación** desde la idea hasta el mantenimiento. El equipo de planificación está formado por **tú + Claude + Gemini**, y **Claude Code** es el ejecutor.

> **Regla de oro:** nada importante vive solo en un chat. Todo lo que se decide se escribe en este repositorio. Por eso la memoria es "infinita": está en archivos versionados con Git, no en la ventana de contexto de una IA.

---

## 1. ¿Cómo funciona? (en 30 segundos)

```
 IDEA ──► 0. Inicio ──► 1. Descubrimiento ──► 2. Estrategia ──► 3. Especificación
                                                                      │
 MANTENIMIENTO ◄── 7. Cierre ◄── 6. Lanzamiento ◄── 5. Construcción ◄── 4. Arquitectura y Plan
        │
        └──► (cambios nuevos vuelven a entrar por /cambio en cualquier momento)
```

- **Fases 0 a 4**: se planifica todo. Aquí conversan tú, Claude (chat) y Gemini. Claude Code redacta los documentos.
- **Fase 5**: Claude Code construye tarea por tarea, siguiendo el plan. Cada tarea usa una rama de Git y termina en un *commit*.
- **Fases 6 y 7**: lanzamiento, retrospectiva y archivo, para retomar el proyecto cuando quieras.

No todos los proyectos recorren todas las fases con la misma profundidad. El tipo de proyecto lo decide; ver `docs/00-inicio/tipos-de-proyecto.md`.

---

## 2. Mapa de la plantilla

| Carpeta / archivo | Para qué sirve | ¿Quién lo lee? |
|---|---|---|
| `memoria/ESTADO.md` | **Tablero**: dónde estamos, qué sigue y qué está bloqueado. | Tú, siempre. Todas las IAs, al empezar. |
| `memoria/contexto-rapido.md` | Resumen de 1 página para **pegar en cualquier chat** (Gemini, Claude web). | IAs de chat |
| `memoria/cambios-pendientes.md` | Bandeja de entrada: ideas, cambios y bugs que surgen en cualquier momento. | Tú + Claude Code |
| `memoria/bitacora/` | Diario de cada sesión de trabajo. | Bajo demanda |
| `memoria/actas/` | Actas de las reuniones de planificación con las IAs. | Bajo demanda |
| `docs/decisiones/` | ADRs: cada decisión importante con su porqué. | Bajo demanda |
| `docs/00-inicio … 07-cierre` | Los entregables de cada fase. | Según la fase |
| `docs/guias/` | Guías para aprender Git/GitHub, el flujo con IAs y MCP. | Tú |
| `AGENTS.md` | Reglas universales para **todas** las IAs. | Claude Code, Gemini/Antigravity, Cursor… |
| `CLAUDE.md` / `GEMINI.md` | Puntos de entrada de cada herramienta (apuntan a AGENTS.md). | Automático |
| `.claude/commands/` | Comandos `/` para Claude Code. | Tú los ejecutas |

---

## 3. Primeros pasos (una sola vez en tu computadora)

1. Instala **Git**: https://git-scm.com/downloads
2. Crea una cuenta en **GitHub** e instala **GitHub CLI** (`gh`): https://cli.github.com/, y luego ejecuta `gh auth login`.
3. Instala **Claude Code** siguiendo la documentación oficial: https://docs.claude.com/en/docs/claude-code/overview
4. (Opcional) Instala la CLI de Gemini. Ojo: Google retiró *Gemini CLI* para cuentas gratuitas/Pro/Ultra en junio de 2026; su sucesora es **Antigravity CLI (`agy`)**. Revisa `docs/guias/mcp-integraciones.md`.
5. Guarda esta plantilla en GitHub como **Template repository**: Settings → marca *Template repository*.

Lee `docs/guias/git-github-para-empezar.md`. Está escrito para aprender desde cero.

---

## 4. Empezar un proyecto nuevo

```bash
# Opción A: script incluido (crea carpeta, git y repo privado en GitHub)
bash scripts/nuevo-proyecto.sh mi-proyecto

# Opción B: desde GitHub → "Use this template" → clonar
```

Luego, dentro de la carpeta:

```bash
claude            # abre Claude Code
/iniciar          # entrevista inicial: tipo de proyecto, propósito, ruta de fases
```

---

## 5. Los comandos (tu control remoto)

| Comando | Cuándo usarlo | Qué hace |
|---|---|---|
| `/iniciar` | Al crear el proyecto | Te entrevista, clasifica el proyecto y arma la ruta de fases |
| `/fase` | Para avanzar la planificación | Trabaja el entregable de la fase actual contigo |
| `/planificar` | Al terminar la especificación | Genera roadmap, fases y tareas ejecutables |
| `/siguiente` | En construcción | Toma la próxima tarea, crea la rama, la implementa y la prueba |
| `/cambio <texto>` | En **cualquier** momento | Registra una modificación o idea y evalúa su impacto |
| `/decision <tema>` | Ante una elección importante | Crea un ADR con opciones y consecuencias |
| `/contexto` | Antes de hablar con Gemini/Claude web | Actualiza `contexto-rapido.md` para que lo pegues |
| `/acta` | Después de una reunión con las IAs | Integra lo acordado en la memoria |
| `/estado` | Cuando te sientas perdido | Te explica en simple dónde estás y qué sigue |
| `/cerrar-sesion` | **Siempre al terminar el día** | Actualiza ESTADO, bitácora y hace commit + push |
| `/archivar` | Al terminar el proyecto | Retrospectiva, versión final y guía para retomarlo |

---

## 6. El ciclo diario (lo que realmente harás)

```
1. claude              → Claude Code lee ESTADO.md automáticamente
2. /estado             → (opcional) recordatorio de dónde vas
3. /siguiente  o  /fase
4. ¿Surgió una idea?   → /cambio "..."   (no interrumpes lo que haces)
5. ¿Hay que decidir algo grande? → /contexto → llevas el tema a Gemini y a Claude web
   → decides → /acta
6. /cerrar-sesion      → todo queda guardado en GitHub
```

---

## 7. Cómo nunca perder el contexto (la memoria en capas)

| Capa | Archivo | Tamaño | Cuándo se carga |
|---|---|---|---|
| 1. Reglas | `AGENTS.md` | Pequeño, casi fijo | Siempre, automático |
| 2. Estado | `memoria/ESTADO.md` | ≤ 1 página | Siempre, automático (hook de inicio) |
| 3. Documentos de fase | `docs/0X-*` | Medio | Cuando se trabaja esa fase |
| 4. Historia | bitácora, actas, ADRs | Crece sin límite | Solo cuando se necesita |
| 5. (Opcional) Búsqueda | NotebookLM con los docs del repo | Ilimitado | Consultas a todo el historial |

El secreto está en que las capas 1 y 2 **siempre se mantienen cortas**. Así ninguna IA se satura. La historia crece sin límite, pero solo se lee por partes. Los detalles están en `docs/guias/flujo-equipo-ia.md`.
