# 📍 ESTADO DEL PROYECTO
<!-- Máximo ~60 líneas. Lo actualiza /cerrar-sesion. El detalle va a la bitácora. -->

**Proyecto:** visible-ia: visibilidad de clínicas locales en asistentes de IA  
**Tipo:** A (SaaS) + J (datos / IA)  
**Última actualización:** 2026-09-26  

## Dónde estamos
- **Fase actual:** 4 · Arquitectura y plan. Fase 3 aprobada el 26/09: PRD v1 congelado (tag `fase-3-completa`)
- **Tarea actual:** `/fase 4`: stack con planes gratuitos, ADR-003 (repeticiones y regla de cambio del índice, PRD §5.5) → `/planificar`
- **Rama de trabajo:** `docs/F4-arquitectura` (las fases 1–3 ya están en `main`)
- **Avance general:** ████░░░░░░ 35 %
- **Calendario:** fases 1–4 del 25 al 27/09 · construcción del 28/09 al 08/11 · ventas desde el 05/10

## Ruta de fases
| # | Fase | Prof. | Estado |
|---|---|---|---|
| 0 | Inicio | — | ✅ |
| 1 | Descubrimiento | ●● | ✅ |
| 2 | Estrategia | ● | ✅ |
| 3 | Especificación | ●● | ✅ |
| 4 | Arquitectura y plan | ●● | 🟡 en curso |
| 5 | Construcción | ●●● | ⚪ |
| 6 | Lanzamiento | ●● | ⚪ |
| 7 | Cierre / mantenimiento | ● | ⚪ |
<!-- ⚪ pendiente · 🟡 en curso · ✅ completa · ⏭️ omitida (explicar por qué en el brief) -->

## Próximos 3 pasos
1. `/fase 4` (arquitectura, ADR-003) y `/planificar`. En paralelo, las tareas legales de `estrategia.md` (términos de OpenAI para web search, créditos de SerpApi en Modo IA, consulta por la Ley 29733)
2. Crear las cuentas gratis (SerpApi) y pedir la aprobación del gasto de OpenAI (≈ US$4/mes con 5 mercados) antes de activar la facturación
3. Iniciar los trámites **sin costo** de WhatsApp Business API y de la pasarela de pagos. Prueba completa (270 consultas) en la semana 1

## Bloqueos / esperando decisión
- ⏳ ADR-003: repeticiones por mes y regla de cambio del índice (con 3 repeticiones casi nunca se detecta una subida; recomendación: opción D). Se decide en la fase 4
- ⏳ **RUC y régimen tributario** (contador) antes del primer cobro. Define si los S/ 349 incluyen IGV (neto ≈ S/ 296) → revisar la meta de la semana 6
- 🔽 Prueba API Gemini (informativa, baja prioridad): config. B, 1 de 10 hecha (rama `chore/prueba-api-gemini`)

## Decisiones recientes (últimas 5)
- 2026-09-26 · PRD v1 congelado: 3 entregas (Vender / Servir / Escalar), 10 plantillas por rubro, índice = % de respuestas con margen de variación
- 2026-09-26 · Fase 2 aprobada: métrica norte = sedes activas pagando con reporte entregado; cobro inicial con link de pago manual; IGV pendiente del régimen
- 2026-09-26 · [ADR-002](../docs/decisiones/ADR-002-motor-de-medicion.md): motor = API de OpenAI + Google Modo IA vía SerpApi (gratis al inicio) + muestra manual de Gemini. Marca blanca para agencias aceptada
- 2026-09-26 · Puerta F1 aprobada: seguir (30/30 respuestas nombran clínicas). H2 reformulada: la fuente principal es la ficha de Google Maps
- 2026-09-26 · [ADR-001](../docs/decisiones/ADR-001-excluir-perplexity.md): Perplexity fuera de la prueba completa y del MVP; reevaluar en la v2 con la API Sonar

## Bandeja de pendientes
- Ver `memoria/cambios-pendientes.md` (0 sin clasificar)
