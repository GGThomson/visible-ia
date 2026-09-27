# 📍 ESTADO DEL PROYECTO
<!-- Máximo ~60 líneas. Lo actualiza /cerrar-sesion. El detalle va a la bitácora. -->

**Proyecto:** visible-ia: visibilidad de clínicas locales en asistentes de IA  
**Tipo:** A (SaaS) + J (datos / IA)  
**Última actualización:** 2026-09-26  

## Dónde estamos
- **Fase actual:** 5 · Construcción. Fase 4 aprobada el 26/09: arquitectura + plan (tags `fase-4-completa`, `plan-aprobado`)
- **Tarea actual:** **C3 ✅ (tareas)**: corrida 1 real en prod (IMP · Miraflores, 60/60, **US$0.97**; SerpApi 219/250) y muestra de la fase 1 importada en dev (31). Falta la demo de C3 del Director. Siguiente: **C4** (extractor). Landing: https://visible-ia.pages.dev
- **Rama de trabajo:** cada tarea en `feat/C<n>-T<nn>-...` desde `main` (las fases 1–4 ya están en `main`)
- **Avance general:** ██████░░░░ 56 % (construcción: C1–C3 de C1–C12)
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
1. **Director:** aprobar la migración 0003 en prod (superficie `google_ai_mode_manual`) y hacer la demo de C3 (`visible-ia corrida ver 1 --env prod`, cargar una muestra de la app de Gemini con `muestra cargar`)
2. `/siguiente` → C4-T01 (extractor con gpt-5-nano). Ojo: en Google los nombres de las fichas solo vienen en `snippet_links` (nota en C4). **Director:** demo de C2 con un CSV real y revisar la landing en el celular
3. En paralelo: lista de 40 clínicas (y preguntar por el plan Gestionado, H9), trámites de WhatsApp y pasarela, tareas legales. ~04/10: confirmar que Supabase dev no se pausó · jue 02/10: control del Plan B

## Bloqueos / esperando decisión
- ⏳ **RUC y régimen tributario** (contador) antes del primer cobro. Define si los S/ 349 incluyen IGV (neto ≈ S/ 296) → revisar la meta de la semana 6
- ⏳ Confirmar a los 8 días que el job diario mantiene activo Supabase dev (C1-T05)
- 🔽 Prueba API Gemini (informativa, baja prioridad): config. B, 1 de 10 hecha (rama `chore/prueba-api-gemini`)

## Decisiones recientes (últimas 5)
- 2026-09-26 · C-005: superficie `google_ai_mode_manual` (migración 0003) y muestra de la fase 1 importada en **dev** (31 filas, 8 mercados inactivos; las de "Lima" fuera de la calibración). Corrida 1 real en prod aprobada y hecha (US$0.97)
- 2026-09-26 · Motor: OpenAI aprobado con **tope de US$5** (prepago, sin recarga automática; `MONTHLY_BUDGET_USD` por defecto = 5). SerpApi Free (250 búsquedas/mes). Cada corrida real necesita el OK del Director con la estimación del motor
- 2026-09-26 · C-004: plan Gestionado como hipótesis H9 (S/ 990 de puesta a punto + S/ 790/mes, tentativos, para preguntar en las llamadas); sin código
- 2026-09-26 · Construcción: Claude Code fusiona cada PR con la CI en verde; se detiene solo si toca producción, cuesta dinero o requiere decisión. Migraciones con `visible-ia db migrate`; web publicada desde Actions
- 2026-09-26 · Plan de construcción aprobado (C1–C12, 46 tareas): Plan B de la v1.0 (C6-T05); la prueba manual de 270 consultas se reemplaza por las corridas reales + calibración; seguimiento solo por ESTADO

## Bandeja de pendientes
- Ver `memoria/cambios-pendientes.md` (0 sin clasificar)
