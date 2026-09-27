# 📍 ESTADO DEL PROYECTO
<!-- Máximo ~60 líneas. Lo actualiza /cerrar-sesion. El detalle va a la bitácora. -->

**Proyecto:** visible-ia: visibilidad de clínicas locales en asistentes de IA  
**Tipo:** A (SaaS) + J (datos / IA)  
**Última actualización:** 2026-09-26  

## Dónde estamos
- **Fase actual:** 5 · Construcción. Fase 4 aprobada el 26/09: arquitectura + plan (tags `fase-4-completa`, `plan-aprobado`)
- **Tarea actual:** **C4-T05**: lista de IMP · Miraflores importada en prod (34 clínicas) y corrida 1 re-asociada (205/215 menciones asociadas). Falta que el Director revise la **muestra de 15 etiquetas** (`data/propuestas/etiquetas-muestra-15.xlsx`) y grabar las salidas del extractor (≈ US$0.007, pedir OK). Landing: https://visible-ia.pages.dev
- **Rama de trabajo:** cada tarea en `feat/C<n>-T<nn>-...` desde `main` (las fases 1–4 ya están en `main`)
- **Avance general:** ██████░░░░ 60 % (construcción: C1–C3 y C4 casi, de C1–C12)
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
1. **Director:** revisar las 15 etiquetas de la muestra y decidir si, con pocas correcciones, se dan por confirmadas las 63
2. Aplicar correcciones, grabar las salidas del extractor (≈ US$0.007, con OK) y cerrar C4 → **C5** (puntaje)
3. En paralelo: lista de 40 clínicas (y preguntar por el plan Gestionado, H9), trámites de WhatsApp y pasarela, tareas legales. ~04/10: confirmar que Supabase dev no se pausó · jue 02/10: control del Plan B

## Bloqueos / esperando decisión
- ⏳ **RUC y régimen tributario** (contador) antes del primer cobro. Define si los S/ 349 incluyen IGV (neto ≈ S/ 296) → revisar la meta de la semana 6
- ⏳ Confirmar a los 8 días que el job diario mantiene activo Supabase dev (C1-T05)
- 🔽 Prueba API Gemini (informativa, baja prioridad): config. B, 1 de 10 hecha (rama `chore/prueba-api-gemini`)

## Decisiones recientes (últimas 5)
- 2026-09-27 · C-006 → se declara en la nota de método (3 de 30 respuestas de Google con fichas sin nombre). Bug corregido: la CLI no confirmaba cada respuesta (se perdió 1 crédito); ahora `autocommit`. SerpApi: 37/250 usadas; OpenAI ≈ US$1.01/5
- 2026-09-26 · C4: extractor con gpt-5-nano y prompt v2 (la v1 descartaba todo con razonamiento mínimo); migraciones 0003 y 0004 en prod; `dentum.com.pe` = web de clínica. Gasto del mes ≈ US$1.01 de US$5
- 2026-09-26 · C-005: superficie `google_ai_mode_manual` (migración 0003) y muestra de la fase 1 importada en **dev** (31 filas, 8 mercados inactivos; las de "Lima" fuera de la calibración). Corrida 1 real en prod aprobada y hecha (US$0.97)
- 2026-09-26 · Motor: OpenAI aprobado con **tope de US$5** (prepago, sin recarga automática; `MONTHLY_BUDGET_USD` por defecto = 5). SerpApi Free (250 búsquedas/mes). Cada corrida real necesita el OK del Director con la estimación del motor
- 2026-09-26 · C-004: plan Gestionado como hipótesis H9 (S/ 990 de puesta a punto + S/ 790/mes, tentativos, para preguntar en las llamadas); sin código

## Bandeja de pendientes
- Ver `memoria/cambios-pendientes.md` (0 sin clasificar)
