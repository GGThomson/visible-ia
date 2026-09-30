# 📍 ESTADO DEL PROYECTO
<!-- Máximo ~60 líneas. Lo actualiza /cerrar-sesion. El detalle va a la bitácora. -->

**Proyecto:** visible-ia: visibilidad de clínicas locales en asistentes de IA  
**Tipo:** A (SaaS) + J (datos / IA)  
**Última actualización:** 2026-09-29  

## Dónde estamos
- **Fase actual:** 5 · Construcción. Fase 4 aprobada el 26/09: arquitectura + plan (tags `fase-4-completa`, `plan-aprobado`)
- **Tarea actual:** **C9b publicada** (29/09, OK del Director): PR #67 fusionado, landing Eminia en https://visible-ia.pages.dev (foto, RUC, Libro de Reclamaciones), diagnóstico coherente de ≤ 8 páginas; migraciones 0009–0011 en prod. **C-010** hecho: `visible-ia diagnostico lote` (PDF + mensaje de WhatsApp por clínica). Sigue **C10** (agencias)
- **Rama de trabajo:** ninguna abierta. Cada tarea en `feat/C<n>-...` desde `main`
- **Avance general:** █████████░ 92 % (construcción: C1–C9 y C9b de C1–C12 completas; v1.0 y v1.1 listas)
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
1. **Director:** el **1/10**, aprobar la corrida de octubre (issue) lanzando *Corrida mensual* en modo `correr`, y **revisarla**
2. **Claude Code:** después de esa revisión, **pasos 1–3 de la reorganización del repo** (un PR cada uno, sin prod ni base de datos; fusionar fuera de 06:00–08:00 de Lima) y parar con un resumen antes del paso 4 (acta `2026-09-29-mapa-del-sistema.md`)
3. **Motor GEO (ADR-007):** diseño del sistema (3 capas, 7 módulos) → producto con panel → clientes. **Ventas postergadas.** Decidir si los 4 diagnósticos de `salida/diagnosticos/2026-09/` se envían o esperan

## Bloqueos / esperando decisión
- ⏳ **Director:** revisar INDECOPI (clases 35 y 42) y eminia.pe antes de comprar o registrar (si no están libres → Prominia). Libro de Reclamaciones publicado sin domicilio del proveedor, correlativo ni copia por correo (revisión legal)
- ⏳ **Régimen tributario** (contador; RUC 10707993435 ya existe) antes del primer cobro. Define si los S/ 349 incluyen IGV (neto ≈ S/ 296) → revisar la meta de la semana 6
- ⏳ Confirmar a los 8 días que el job diario mantiene activo Supabase dev (C1-T05)
- 🔽 Prueba API Gemini (informativa, baja prioridad): config. B, 1 de 10 hecha (rama `chore/prueba-api-gemini`)

## Decisiones recientes (últimas 5)
- 2026-09-29 · **El motor GEO es la empresa; Eminia es su primera vertical** (ADR-007): opción 4 (interno, diseñado para abrirse); todas las entidades, global y multi-idioma; diseño → producto con panel → clientes. Mapa en 3 capas y 7 módulos; reorganización de `src/` aprobada
- 2026-09-29 · **Diagnósticos en lote (C-010)**: comando con PDF + primer mensaje de WhatsApp; vocabulario del nicho en `nicho.toml`; diagnóstico ≤ 8 páginas (2 frases por competidor, versión compacta automática); el plan no repite acciones con la misma medida
- 2026-09-29 · **C9b publicada** con el OK escrito del Director: PR #67 fusionado y migración 0011 (`consent_version` obligatoria) aplicada en prod por el Director tras publicar la landing
- 2026-09-28 · **Semáforo del diagnóstico frente al líder**: tu cifra ÷ la del líder; Bien ≥ 80 %, Regular 40–80 %, Bajo < 40 %, «Sin datos» si el líder está en 0 (Maps: reseñas). Plan de acción: siempre las 3 acciones de mayor impacto (respuestas de diferencia con el líder). RUC 10707993435 en el pie
- 2026-09-28 · **ADR-006**: los planes pagados medirán **120 respuestas/mes** por mercado (20 preguntas × 3 × ChatGPT y Google), el diagnóstico gratis sigue en 60; presupuesto +US$2.50 por mercado de cliente que pagó; Gemini manual; investigar Vertex AI. Sin construir (C-009). PRD HU-14: diagnóstico ≤ 8 páginas

## Bandeja de pendientes
- Ver `memoria/cambios-pendientes.md` (0 sin clasificar)
