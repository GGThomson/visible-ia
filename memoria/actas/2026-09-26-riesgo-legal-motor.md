# Acta 2026-09-26 · Riesgo legal del motor de medición (C-001)
<!-- Nombre: AAAA-MM-DD-tema.md. Se crea con /acta pegando las respuestas de Gemini y/o Claude web. -->

- **Participantes:** Director, Claude (proyecto en claude.ai, con lectura del repositorio). **Gemini: todavía sin respuesta.**
- **Tema:** C-001, el riesgo legal del motor de medición, y el siguiente paso de la fase 2.
- **Contexto usado:** `memoria/contexto-rapido.md`, versión 2026-09-26, más `docs/02-estrategia/riesgo-legal-motor.md` (Claude lo leyó en el repositorio).

## Propuestas recibidas
| De | Propuesta | A favor | En contra |
|---|---|---|---|
| Claude (claude.ai) | **Opción C como motor del MVP:** API de OpenAI (gpt-5-mini + web search, `user_location` = Lima) para ChatGPT; Google Modo IA vía un proveedor SERP; Gemini solo como muestra manual mensual de calibración | Usa solo vías cuyos términos permiten guardar y analizar (API de OpenAI), o que asumen la recolección (SERP). Coincide con la recomendación de Claude Code | Gemini no se mide de forma automática. El proveedor SERP deja un riesgo residual (demanda de Google contra SerpApi, §7.1 de DataForSEO) |
| Claude (claude.ai) | Empezar Google Modo IA con el **plan gratis de SerpApi** (250 búsquedas al mes, alcanza para 5 mercados). Pasar a DataForSEO o a SerpApi de pago con el primer ingreso | Cabe en el tope de US$20. DataForSEO pide un mínimo de US$50 | El plan gratis no incluye el Legal Shield (solo desde US$150/mes). Falta confirmar que el Modo IA gaste 1 crédito |
| Claude (claude.ai) | **Retención:** texto completo 12 meses; métricas derivadas mientras el cliente esté activo más 12 meses; ningún dato de pacientes | Igual que la propuesta de Claude Code | Falta la revisión legal de la Ley 29733 (nombres de médicos) |
| Claude (claude.ai) | La prueba de la API de Gemini (`chore/prueba-api-gemini`) queda como informativa y no bloquea la fase 2 | Coincide con lo que ya decidió el Director | — |

**Coincidencias:** la propuesta de Claude (claude.ai) coincide con la opción C que recomendó Claude Code en `riesgo-legal-motor.md`. Agrega una precisión: empezar con el plan gratis de SerpApi por el tope de presupuesto.
**Desacuerdos:** ninguno por ahora. **Gemini todavía no ha dado su opinión**, así que esta acta refleja una sola voz de los planificadores.

## Decisión del Director
- **Se decidió (26/09):**
  1. **Opción C** como motor del MVP.
  2. **Plan gratis de SerpApi** para Google Modo IA; con el primer ingreso se pasa a DataForSEO o a SerpApi de pago.
  3. **Se acepta la marca blanca para agencias.**
- **Porque:** es la vía que cubre ChatGPT y Google sin violar términos conocidos y cabe en el tope de US$20. La marca blanca era un pendiente desde el 25/09 y se necesitaba antes de la semana 5.
- **ADR generado:** `docs/decisiones/ADR-002-motor-de-medicion.md`
- **Nota:** se decidió sin la opinión de Gemini.

## Tareas que salen de aquí
- [ ] Verificar en los términos de la API de OpenAI que no haya restricciones para guardar y analizar los resultados de *web search*.
- [x] Registrar como riesgo la §7.1 de DataForSEO (en ADR-002 y `riesgo-legal-motor.md`): prohíbe usar los datos *"to compete with or adversely affect"* a los buscadores.
- [x] Crear el ADR-002 con la decisión del motor.
- [ ] Completar `docs/02-estrategia/estrategia.md` (propuesta de valor, precios con margen, métrica norte, alcance del MVP, legal / Ley 29733).
- [ ] Al cerrar la fase 2: actualizar ESTADO y fusionar `docs/F2-estrategia` a `main`. Además, con la regla nueva, `memoria/` y `docs/` se fusionan en cada cierre de sesión.

## Preguntas que quedan abiertas
- ~~Opción C, plan gratis de SerpApi y marca blanca~~ → decididas el 26/09.
- Si Gemini responde después, se integra su acta. Solo se reabre el ADR-002 si trae un motivo nuevo.
