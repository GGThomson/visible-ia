# Sesión 2026-09-26 · Muestra de la prueba de fuentes y puerta de la fase 1

- **Fase / tareas:** F1 (puerta de descubrimiento)
- **Rama(s):** `docs/F1-descubrimiento` (fusionada en `main`) · `docs/F2-estrategia` (creada para el cierre)
- **Commits:**
  - `37aa2b0` docs: sample results and gate proposal for source test (F1)
  - `9e104bb` docs: ADR-001 exclude Perplexity from full test and MVP (F1)
  - `8878bb9` docs: completa fase 1 - descubrimiento
  - `6b5e21f` Merge branch 'docs/F1-descubrimiento': fase 1 completa (tag `fase-1-completa`)

## Qué se hizo
- **Muestra:** el Director completó ChatGPT, Gemini y Google Modo IA (10 preguntas cada una, más una 2.ª repetición de ChatGPT en Q22). De Perplexity solo hizo Q01.
- **Registro corregido** (`registro.csv`):
  - En las filas 23–28, las fuentes venían en varias líneas y con las notas mezcladas. Quedaron en una línea y las notas pasaron a su columna.
  - Se recuperaron el nombre del archivo y los encabezados del protocolo.
  - Se borraron las filas vacías de Perplexity.
  - Se anotó "Modo IA" en Google Q22–Q30.
- **Análisis de la muestra** (en `investigacion.md`):
  - **H1:** 30/30 respuestas nombran clínicas (100 %).
  - **Fuentes:** la principal es la ficha de Google Maps, seguida de Doctoralia, la web propia y las redes.
  - **Variación:** en 7 de 10 preguntas hay una clínica "líder" que nombran las 3 IAs. Fuera de ella, la mayoría de las clínicas aparece en una sola IA.
- **Propuesta de prueba con la API de Gemini** (nivel gratuito, Search + Maps) antes de las 270 consultas manuales: `docs/01-descubrimiento/prueba-fuentes/propuesta-api-gemini.md`.
- **Fase 1 cerrada:** fusión con `main`, tag `fase-1-completa` y push.

## Qué se decidió (y dónde quedó registrado)
- **Puerta F1 aprobada: seguir.** Registrado en `investigacion.md` y en el brief.
- **H2 reformulada:** la fuente principal es la ficha de Google Maps. Registrado en `investigacion.md`.
- **Perplexity fuera de la prueba completa y del MVP;** se reevalúa en la v2 con la API Sonar. Registrado en `docs/decisiones/ADR-001-excluir-perplexity.md`.
- **Prueba completa:** 3 superficies × 30 × 3 = 270 consultas.

## Problemas y cómo se resolvieron
- **CSV con saltos de línea dentro de las fuentes:** se aplanó con un script, sin cambiar el contenido.
- **Error de Claude:** dijo que Q19 de Google tenía "Modo IA" anotado y no era así. Se dejó Q19 sin anotar porque el Director solo confirmó Q22–Q30.
- **Riesgo encontrado:** la herramienta de Google Maps de la API de Gemini "solo admite inglés" según la documentación oficial. La prueba propuesta lo mide (config. B y B-en).

## Para la próxima sesión
- **Director:** aprobar (o no) la propuesta de la API de Gemini. Si la aprueba, crear la clave en AI Studio **sin facturación** y guardarla en `.env`.
- `/fase 2` (estrategia ligera).
- Semana 1 (28/09): prueba completa, trámites sin costo de WhatsApp Business API y de la pasarela de pagos.
- **Pendiente menor:** ¿Google Q19 también fue en Modo IA?

---

# Sesión 2026-09-26 (2.ª parte) · Prueba API Gemini, costos y C-001

- **Fase / tareas:** F2 (estrategia) · prueba de la API de Gemini (informativa)
- **Rama(s):** `chore/prueba-api-gemini` · `docs/F2-estrategia` (ambas sincronizadas con `main` al cierre)
- **Commits:**
  - `ddaaea7` chore: Gemini API source test script; annotate Google Q19 as Modo IA
  - `520fc34` chore: partial Gemini API test results (19/60 calls, free tier daily cap)
  - `19cac0d` fix: parse search queries and source domains in Gemini API test; config B only
  - `191afae` docs: API measurement cost estimate for phase 4 and ToS risk C-001 (F2)
  - `ada89d7` docs: C-001 legal risk analysis of measurement engine (F2)
  - `5e6ce27` docs: actualiza contexto rápido (vacío: el contenido entró en `ada89d7`)

## Qué se hizo
- **Prueba de la API de Gemini:**
  - Gemini 3.x no tiene grounding en el nivel gratuito, así que se usó 2.5 Flash, con un tope de 20 llamadas al día.
  - Config. A: 19 llamadas. Comparte ≥ 1 clínica con la app en 5 de 7 preguntas, pero cita webs y no fichas de Maps.
  - Config. B: 1 de 10.
- **Costos de medir con API** (5, 12 y 30 mercados): ≈ US$5, 11 y 29 al mes → `docs/04-arquitectura/costos-medicion-api.md`.
- **C-001:**
  - Los términos de grounding de Gemini prohíben "analyze" y guardar las respuestas.
  - Investigación de competidores (miden automatizando la interfaz web) y de los términos de OpenAI, SerpApi y DataForSEO → `docs/02-estrategia/riesgo-legal-motor.md`.
  - Contexto regenerado para llevarlo a Gemini.
- **`/cerrar-sesion` modificado:** ahora fusiona `memoria/` y `docs/` a `main` en cada cierre.

## Qué se decidió (y dónde quedó registrado)
- **Prueba de la API:** solo la config. B, informativa y de baja prioridad (en la propuesta y el ESTADO).
- **C-001 es la prioridad n.º 1 de la fase 2** (en el ESTADO y en cambios pendientes).
- **Memoria y docs a `main` en cada cierre** (en `.claude/commands/cerrar-sesion.md`).

## Problemas y cómo se resolvieron
- **Dato equivocado de Claude:** la propuesta decía que el nivel gratuito incluía 5,000 búsquedas al mes; eran del nivel de pago. Se corrigió en el documento.
- **Clave en `.env`:** Claude no puede escribir `.env` por una regla de permisos, así que la creó el Director.
- **Parser del script:** no capturaba las búsquedas (`arguments.queries`) ni los dominios de las fuentes. Se corrigió y se rellenaron las filas ya registradas.

## Para la próxima sesión
- Llevar el contexto y `riesgo-legal-motor.md` a Gemini → `/acta` → decidir el motor (ADR-002).
- Opcional: las 9 llamadas que faltan de la config. B.
- Regenerar la clave de Gemini en AI Studio: quedó en el historial del chat.

---

# Sesión 2026-09-26 (3.ª parte) · Fases 2–4 aprobadas y construcción de C1–C2

- **Fase / tareas:** F2 estrategia · F3 PRD · F4 arquitectura y plan · construcción C1-T01…C1-T06 y C2-T01…C2-T04
- **Rama(s):** `docs/F2-estrategia`, `docs/F3-especificacion`, `docs/F4-arquitectura` (fusionadas, con tags) y una rama `feat/`/`fix/` por tarea, cada una fusionada por PR
- **Commits en `main` (primer padre, desde el cierre anterior):**
  - `c2026f6` fase 2 completa · `74eaf34` fase 3 completa · `2af50ea` fase 4 completa, plan aprobado
  - `af1c2d8` C1-T01 (#1) · `6bbc3b4` C1-T02 (#2) · `cae970e` C1-T03 (#3) · `bec66f3` C1-T04 (#4)
  - `57193ac` C1-T05 (#5) · `7dde1b8` fix URL (#8) · `747ac1f` fix diagnóstico (#9)
  - `fe4ed4f` C1-T06 (#10) · `5c34e07` docs C1 (#11)
  - `0c08e9a` C2-T01 (#12) · `77030ec` C2-T02 (#13) · `0fd02ea` C2-T03 (#14) · `c0e6d92` C2-T04 (#15)
  - Tags: `fase-2-completa`, `fase-3-completa`, `fase-4-completa`, `plan-aprobado`

## Qué se hizo
- **Acta C-001:** Claude (claude.ai) coincidió con la opción C. El Director aprobó el ADR-002, el plan gratis de SerpApi y la marca blanca.
- **Fase 2 (estrategia):** propuesta de valor, precios con margen (≈ 94–95 %), go-to-market y métrica norte. IGV pendiente del régimen.
- **Fase 3 (PRD v1 congelado):**
  - 27 historias en 3 entregas.
  - 40 plantillas.
  - Índice = % con margen de Wilson.
  - La §5.5 muestra que con 30 respuestas casi no se detectan cambios.
- **Fase 4 (arquitectura aprobada):**
  - ADR-003: 3 repeticiones + prueba de 2 proporciones + ventana de 3 meses.
  - ADR-004: Python sin servidor (Supabase + GitHub Actions + Cloudflare Pages).
  - Job diario (una vez por semana no basta, según la documentación de Supabase).
  - Webhooks en Edge Functions.
  - Plan C1–C12 (46 tareas) con Plan B para vender el 05/10 (C6-T05).
- **Construcción C1 (base):**
  - Paquete `uv` y CLI.
  - Config por entorno.
  - Esquema con RLS en 20 tablas (dev y prod).
  - CI.
  - Job diario OK en Actions.
  - Landing "Próximamente" en https://visible-ia.pages.dev.
- **Construcción C2 (mercados):**
  - 40 plantillas cargadas en dev.
  - `mercado crear/listar/preguntas/editar-pregunta` con banco versionado.
  - `clinicas importar/listar` (CSV con `,` o `;`, decimales con coma).
  - Alias automáticos no genéricos + manuales.
  - 60 pruebas unitarias y 13 de integración (con rollback).

## Qué se decidió (y dónde quedó registrado)
- Fases 2, 3 y 4 aprobadas (documentos de cada fase, ADR-002 a ADR-004, roadmap).
- **Fusión automática de PRs con la CI en verde; parar solo por producción, dinero o decisiones del Director** (memoria de Claude Code, 26/09).
- **Migraciones con `visible-ia db migrate`** en vez de `supabase db push` (C1-base.md).
- **Web publicada desde Actions (wrangler)** en vez de la integración Git de Cloudflare (C1-base.md).
- **Alias genéricos nunca automáticos**, aunque el ejemplo del plan dijera "Implantes Dental" (C2-mercados.md).

## Problemas y cómo se resolvieron
- **CI:** `setup-uv` no publica la etiqueta `v10`; se fijó `v10.2.0`.
- **Secrets de GitHub con valores distintos al `.env`:**
  - URL sin forma `https://<id>.supabase.co` → PR #8 (normaliza) y PR #9 (diagnostica sin mostrar el valor).
  - Claves `service_role` inválidas.
  - Solución: el Director recargó los Secrets desde el `.env`. Issues #6 y #7 cerrados.
- **Cloudflare:** el primer token no veía ninguna cuenta (403). El Director creó uno con *Cloudflare Pages: Edit*.
- **Certificado SSL** de `*.pages.dev`: tarda unos minutos en emitirse al crear el proyecto.
- **Claude no puede leer ni escribir `.env`** (regla de permisos). El Director lo crea con `Copy-Item .env.example .env`.

## Para la próxima sesión
- **Director:**
  - Demo de C2 en dev con un CSV real.
  - Revisar la landing en el celular.
  - Crear la cuenta de SerpApi y **decidir la facturación de OpenAI** (≈ US$4/mes, tope US$10).
- **Claude Code:** C3 (motor). Sin la facturación aprobada, avanzar con respuestas grabadas, sin llamadas reales.
- **Hacia el 04/10:** confirmar que Supabase dev no se pausó. **Jue 02/10:** control del Plan B.
