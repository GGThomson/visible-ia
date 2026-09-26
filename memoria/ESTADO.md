# 📍 ESTADO DEL PROYECTO
<!-- Máximo ~60 líneas. Lo actualiza /cerrar-sesion. El detalle va a la bitácora. -->

**Proyecto:** visible-ia: visibilidad de clínicas locales en asistentes de IA  
**Tipo:** A (SaaS) + J (datos / IA)  
**Última actualización:** 2026-09-26  

## Dónde estamos
- **Fase actual:** 2 · Estrategia (ligera). Fase 1 aprobada el 26/09 (tag `fase-1-completa`)
- **Tarea actual:** `/fase 2`, más la prueba con la API de Gemini (propuesta, pendiente de aprobación)
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
1. **Director:** revisar la [propuesta de la API de Gemini](../docs/01-descubrimiento/prueba-fuentes/propuesta-api-gemini.md). Si la aprueba, crear la clave en AI Studio **sin facturación** y guardarla en `.env`
2. `/fase 2` (estrategia ligera: legal, métrica norte y costos)
3. Iniciar los trámites **sin costo** de WhatsApp Business API y de la pasarela de pagos. Prueba completa (270 consultas) en la semana 1

## Bloqueos / esperando decisión
- 🔽 Prueba con la API de Gemini (informativa, baja prioridad por C-001): solo config. B, 1 de 10 hecha. `python scripts/prueba_api_gemini.py --configs B --reps 1` (rama `chore/prueba-api-gemini`)
- ⏳ Marca blanca para agencias: ¿se acepta? (propuesta: sí; se necesita antes de la semana 5)

## Decisiones recientes (últimas 5)
- 2026-09-26 · Puerta F1 aprobada: seguir (30/30 respuestas nombran clínicas). H2 reformulada: la fuente principal es la ficha de Google Maps
- 2026-09-26 · [ADR-001](../docs/decisiones/ADR-001-excluir-perplexity.md): Perplexity fuera de la prueba completa y del MVP; reevaluar en la v2 con la API Sonar
- 2026-09-25 · Google (Modo IA / AI Overviews) como 4.ª superficie; muestra de 40 consultas; prueba completa en la semana 1; consultas sin sesión; 30 preguntas aprobadas
- 2026-09-25 · Tipo A + J, tiempo completo, ruta de fases aprobada
- 2026-09-25 · Presupuesto máximo de US$20 en la validación; solo planes gratuitos; ningún gasto sin aprobación

## Bandeja de pendientes
- Ver `memoria/cambios-pendientes.md` (0 sin clasificar)
