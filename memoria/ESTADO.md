# 📍 ESTADO DEL PROYECTO
<!-- Máximo ~60 líneas. Lo actualiza /cerrar-sesion. El detalle va a la bitácora. -->

**Proyecto:** visible-ia: visibilidad de clínicas locales en asistentes de IA  
**Tipo:** A (SaaS) + J (datos / IA)  
**Última actualización:** 2026-09-26  

## Dónde estamos
- **Fase actual:** 5 · Construcción. Fase 4 aprobada el 26/09: arquitectura + plan (tags `fase-4-completa`, `plan-aprobado`)
- **Tarea actual:** **C1-T05** en PR, esperando que prod tenga el esquema (C1-T01 a C1-T04 ✅). Siguiente: C1-T06
- **Rama de trabajo:** cada tarea en `feat/C<n>-T<nn>-...` desde `main` (las fases 1–4 ya están en `main`)
- **Avance general:** █████░░░░░ 45 %
- **Calendario:** construcción del 28/09 al 08/11 · **v1.0 "Vender" el 04/10** · ventas desde el 05/10 · control del Plan B el **jue 02/10** (C6-T05)

## Ruta de fases
| # | Fase | Prof. | Estado |
|---|---|---|---|
| 0 | Inicio | — | ✅ |
| 1 | Descubrimiento | ●● | ✅ |
| 2 | Estrategia | ● | ✅ |
| 3 | Especificación | ●● | ✅ |
| 4 | Arquitectura y plan | ●● | ✅ |
| 5 | Construcción (C1–C12) | ●●● | 🟡 en curso |
| 6 | Lanzamiento | ●● | ⚪ |
| 7 | Cierre / mantenimiento | ● | ⚪ |
<!-- ⚪ pendiente · 🟡 en curso · ✅ completa · ⏭️ omitida (explicar por qué en el brief) -->

## Próximos 3 pasos
1. **Director:** aplicar el esquema en prod (`uv run visible-ia db migrate --env prod`) y autorizar la fusión del PR de C1-T05 (job diario que escribe en prod)
2. `/siguiente` → C1-T05 (job diario) y C1-T06 (landing + README). Luego C2 (mercados)
3. **Director (29/09):** cuenta de SerpApi y **aprobar la facturación de OpenAI** (≈ US$4/mes, tope US$10) antes de C3. En paralelo: lista de 40 clínicas, trámites de WhatsApp y pasarela, tareas legales

## Bloqueos / esperando decisión
- ⏳ **RUC y régimen tributario** (contador) antes del primer cobro. Define si los S/ 349 incluyen IGV (neto ≈ S/ 296) → revisar la meta de la semana 6
- ⏳ Confirmar a los 8 días que el job diario mantiene activo Supabase dev (C1-T05)
- 🔽 Prueba API Gemini (informativa, baja prioridad): config. B, 1 de 10 hecha (rama `chore/prueba-api-gemini`)

## Decisiones recientes (últimas 5)
- 2026-09-26 · Plan de construcción aprobado (C1–C12, 46 tareas): Plan B de la v1.0 (C6-T05); la prueba manual de 270 consultas se reemplaza por las corridas reales + calibración; seguimiento solo por ESTADO
- 2026-09-26 · Arquitectura aprobada: [ADR-003](../docs/decisiones/ADR-003-repeticiones-y-regla-de-cambio.md) (3 rep. + prueba de 2 proporciones + ventana de 3 meses) y [ADR-004](../docs/decisiones/ADR-004-stack-sin-servidor-python.md) (Python sin servidor: Supabase + GitHub Actions + Cloudflare Pages; job diario; webhooks en Edge Functions)
- 2026-09-26 · PRD v1 congelado: 3 entregas (Vender / Servir / Escalar), 10 plantillas por rubro, índice = % de respuestas con margen de variación
- 2026-09-26 · Fase 2 aprobada: métrica norte = sedes activas pagando con reporte entregado; cobro inicial con link de pago manual; IGV pendiente del régimen
- 2026-09-26 · [ADR-002](../docs/decisiones/ADR-002-motor-de-medicion.md): motor = API de OpenAI + Google Modo IA vía SerpApi (gratis al inicio) + muestra manual de Gemini. Marca blanca aceptada

## Bandeja de pendientes
- Ver `memoria/cambios-pendientes.md` (0 sin clasificar)
