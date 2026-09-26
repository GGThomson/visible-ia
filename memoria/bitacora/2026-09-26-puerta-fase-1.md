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
