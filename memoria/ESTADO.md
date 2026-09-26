# 📍 ESTADO DEL PROYECTO
<!-- Máximo ~60 líneas. Lo actualiza /cerrar-sesion. El detalle va a la bitácora. -->

**Proyecto:** visible-ia: visibilidad de clínicas locales en asistentes de IA  
**Tipo:** A (SaaS) + J (datos / IA)  
**Última actualización:** 2026-09-26  

## Dónde estamos
- **Fase actual:** 2 · Estrategia (ligera). Fase 1 aprobada el 26/09 (tag `fase-1-completa`)
- **Tarea actual:** `/fase 2`: completar `estrategia.md` (propuesta de valor, precios con margen, métrica norte, alcance del MVP, legal). C-001 resuelto (ADR-002)
- **Rama de trabajo:** `docs/F2-estrategia` (la fase 1 ya está en `main`)
- **Avance general:** ██░░░░░░░░ 18 %
- **Calendario:** fases 1–4 del 25 al 27/09 · construcción del 28/09 al 08/11 · ventas desde el 05/10

## Ruta de fases
| # | Fase | Prof. | Estado |
|---|---|---|---|
| 0 | Inicio | — | ✅ |
| 1 | Descubrimiento | ●● | ✅ |
| 2 | Estrategia | ● | 🟡 en curso |
| 3 | Especificación | ●● | ⚪ |
| 4 | Arquitectura y plan | ●● | ⚪ |
| 5 | Construcción | ●●● | ⚪ |
| 6 | Lanzamiento | ●● | ⚪ |
| 7 | Cierre / mantenimiento | ● | ⚪ |
<!-- ⚪ pendiente · 🟡 en curso · ✅ completa · ⏭️ omitida (explicar por qué en el brief) -->

## Próximos 3 pasos
1. `/fase 2`: completar `estrategia.md` y las tareas legales (términos de OpenAI para web search, créditos de SerpApi en Modo IA, consulta por la Ley 29733)
2. Crear las cuentas gratis (SerpApi) y pedir la aprobación del gasto de OpenAI (≈ US$4/mes con 5 mercados) antes de activar la facturación
3. Iniciar los trámites **sin costo** de WhatsApp Business API y de la pasarela de pagos. Prueba completa (270 consultas) en la semana 1

## Bloqueos / esperando decisión
- 🔽 Prueba API Gemini (informativa, baja prioridad): config. B, 1 de 10 hecha (rama `chore/prueba-api-gemini`)

## Decisiones recientes (últimas 5)
- 2026-09-26 · [ADR-002](../docs/decisiones/ADR-002-motor-de-medicion.md): motor = API de OpenAI + Google Modo IA vía SerpApi (gratis al inicio) + muestra manual de Gemini. Marca blanca para agencias aceptada
- 2026-09-26 · Puerta F1 aprobada: seguir (30/30 respuestas nombran clínicas). H2 reformulada: la fuente principal es la ficha de Google Maps
- 2026-09-26 · [ADR-001](../docs/decisiones/ADR-001-excluir-perplexity.md): Perplexity fuera de la prueba completa y del MVP; reevaluar en la v2 con la API Sonar
- 2026-09-25 · Google (Modo IA / AI Overviews) como 4.ª superficie; muestra de 40 consultas; prueba completa en la semana 1; consultas sin sesión; 30 preguntas aprobadas
- 2026-09-25 · Presupuesto máximo de US$20 en la validación; solo planes gratuitos; ningún gasto sin aprobación

## Bandeja de pendientes
- Ver `memoria/cambios-pendientes.md` (0 sin clasificar)
