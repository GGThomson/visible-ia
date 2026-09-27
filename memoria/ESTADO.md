# 📍 ESTADO DEL PROYECTO
<!-- Máximo ~60 líneas. Lo actualiza /cerrar-sesion. El detalle va a la bitácora. -->

**Proyecto:** visible-ia: visibilidad de clínicas locales en asistentes de IA  
**Tipo:** A (SaaS) + J (datos / IA)  
**Última actualización:** 2026-09-26  

## Dónde estamos
- **Fase actual:** 5 · Construcción. Fase 4 aprobada el 26/09: arquitectura + plan (tags `fase-4-completa`, `plan-aprobado`)
- **Tarea actual:** **C3**, motor: T01–T04 ✅ (clientes verificados con 1 llamada real c/u: ChatGPT US$0.028, SerpApi 1 crédito). Falta la **primera corrida real** (espera el OK del Director con la estimación del motor) y C3-T05. Landing: https://visible-ia.pages.dev
- **Rama de trabajo:** cada tarea en `feat/C<n>-T<nn>-...` desde `main` (las fases 1–4 ya están en `main`)
- **Avance general:** █████░░░░░ 52 % (construcción: C1–C2 de C1–C12)
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
1. **Director:** poner `MONTHLY_BUDGET_USD=5` en `.env` (hoy dice 10) y aprobar la primera corrida real "Implantología · Miraflores" (60 llamadas, ≈ US$0.89 estimados por el motor; 30 créditos de SerpApi) y en qué entorno (recomendado: prod, con la migración 0002)
2. `/siguiente` → C3-T05 (muestras manuales) y la demo de C3. **Director:** demo de C2 con un CSV real y revisar la landing en el celular
3. En paralelo: lista de 40 clínicas (y preguntar por el plan Gestionado, H9), trámites de WhatsApp y pasarela, tareas legales. ~04/10: confirmar que Supabase dev no se pausó · jue 02/10: control del Plan B

## Bloqueos / esperando decisión
- ⏳ **RUC y régimen tributario** (contador) antes del primer cobro. Define si los S/ 349 incluyen IGV (neto ≈ S/ 296) → revisar la meta de la semana 6
- ⏳ Confirmar a los 8 días que el job diario mantiene activo Supabase dev (C1-T05)
- 🔽 Prueba API Gemini (informativa, baja prioridad): config. B, 1 de 10 hecha (rama `chore/prueba-api-gemini`)

## Decisiones recientes (últimas 5)
- 2026-09-26 · Motor: OpenAI aprobado con **tope de US$5** (prepago, sin recarga automática; `MONTHLY_BUDGET_USD` por defecto = 5). SerpApi Free (250 búsquedas/mes). Cada corrida real necesita el OK del Director con la estimación del motor
- 2026-09-26 · C-004: plan Gestionado como hipótesis H9 (S/ 990 de puesta a punto + S/ 790/mes, tentativos, para preguntar en las llamadas); sin código
- 2026-09-26 · Construcción: Claude Code fusiona cada PR con la CI en verde; se detiene solo si toca producción, cuesta dinero o requiere decisión. Migraciones con `visible-ia db migrate`; web publicada desde Actions
- 2026-09-26 · Plan de construcción aprobado (C1–C12, 46 tareas): Plan B de la v1.0 (C6-T05); la prueba manual de 270 consultas se reemplaza por las corridas reales + calibración; seguimiento solo por ESTADO
- 2026-09-26 · Arquitectura aprobada: [ADR-003](../docs/decisiones/ADR-003-repeticiones-y-regla-de-cambio.md) (3 rep. + prueba de 2 proporciones + ventana de 3 meses) y [ADR-004](../docs/decisiones/ADR-004-stack-sin-servidor-python.md) (Python sin servidor: Supabase + GitHub Actions + Cloudflare Pages; job diario; webhooks en Edge Functions)

## Bandeja de pendientes
- Ver `memoria/cambios-pendientes.md` (0 sin clasificar)
