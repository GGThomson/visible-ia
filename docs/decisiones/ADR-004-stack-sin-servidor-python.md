# ADR-004 · Stack: Python + arquitectura sin servidor (Supabase, GitHub Actions, Cloudflare Pages)

- **Fecha:** 2026-09-26
- **Estado:** Aceptada
- **Decide:** Director
- **Consultados:** Claude Code (propuesta en `docs/04-arquitectura/arquitectura.md`)

## Contexto
La v1 debe construirse en 6 semanas y costar US$0 fijo al mes (brief: planes gratuitos; tope de US$20 en la validación).
- **El trabajo pesado es por lotes:** una corrida mensual por mercado (60 llamadas a API, extracción, puntaje y PDF).
- **La web es liviana:** una landing con formulario y un panel de lectura para pocos clientes.
- **El Director mantiene el código:** prefiere Python.

## Opciones consideradas
| Opción | Ventajas | Desventajas | Costo fijo |
|---|---|---|---|
| **A. Sin servidor:** Python en CLI + GitHub Actions, Supabase (Postgres, Auth, Storage, RLS) y web estática en Cloudflare Pages | Nada que mantener encendido. Los permisos se aplican en la base de datos (RLS). Encaja con el trabajo por lotes | Hace falta JavaScript mínimo en el navegador. Supabase gratis pausa tras 1 semana sin actividad. Las corridas dependen de Actions | US$0 |
| B. Servidor Python (FastAPI) en Render gratis + Postgres | Un solo lugar para la lógica y todo en Python | Se duerme tras inactividad (primer acceso lento). Los jobs largos pueden cortarse. Hay que programar los permisos a mano | US$0 (con limitaciones) |
| C. Next.js en Vercel + Supabase | Ecosistema moderno | Todo en TypeScript, que no prefiere el Director. **El plan Hobby de Vercel prohíbe el uso comercial** | US$20/mes (Pro) |

## Decisión
Elegimos **A**:
- **Datos:** Python 3.12+ (uv, ruff, pytest, pydantic, typer, httpx, SDK de OpenAI, rapidfuzz, jinja2 y Playwright para los PDF).
- **Base de datos:** Supabase (proyectos dev y prod) con migraciones SQL versionadas y RLS probado.
- **Tareas:** GitHub Actions para la corrida mensual, el job semanal y la CI.
- **Web:** Cloudflare Pages para la landing y el panel estáticos (HTML + Pico CSS + `supabase-js`, sin framework).
- **Extractor:** gpt-5-nano con salida estructurada, más coincidencia por alias y rapidfuzz.

## Consecuencias
- **Positivas:**
  - US$0 fijo.
  - La herramienta de v1.0 es una CLI y funciona en la semana 1, sin esperar al panel.
  - La seguridad por cliente vive en la base de datos.
- **Negativas / lo que aceptamos:**
  - Un poco de JavaScript en el panel.
  - Los webhooks de v1.2 (WhatsApp y pagos) necesitarán una función pequeña (Supabase Edge Function, en TypeScript) o una alternativa que se decide al planificar la v1.2.
  - Hay que vigilar los límites de los planes gratis (sección de costos de la arquitectura).
- **Qué habría que hacer si cambiamos de opinión:**
  - La lógica está en el paquete Python `visible_ia`, así que se podría envolver en un servidor FastAPI (opción B) sin reescribirla.
  - La base de datos es Postgres estándar y se puede mover.
