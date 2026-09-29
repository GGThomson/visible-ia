# 📍 ESTADO DEL PROYECTO
<!-- Máximo ~60 líneas. Lo actualiza /cerrar-sesion. El detalle va a la bitácora. -->

**Proyecto:** visible-ia: visibilidad de clínicas locales en asistentes de IA  
**Tipo:** A (SaaS) + J (datos / IA)  
**Última actualización:** 2026-09-28  

## Dónde estamos
- **Fase actual:** 5 · Construcción. Fase 4 aprobada el 26/09: arquitectura + plan (tags `fase-4-completa`, `plan-aprobado`)
- **Tarea actual:** **C9b · Marca y oferta** lista en el **PR #67** (sin fusionar ni publicar): landing Eminia con foto, RUC y Libro de Reclamaciones; **diagnóstico de 7 páginas coherente** (semáforo frente al líder, plan por impacto); migraciones 0009 y 0010 en prod. Falta el **OK escrito del Director** para publicar. Luego C10. Vista previa: https://feat-c9b-marca-y-oferta.visible-ia.pages.dev
- **Rama de trabajo:** `feat/C9b-marca-y-oferta` (PR #67). Cada tarea en `feat/C<n>-...` desde `main`
- **Avance general:** █████████░ 91 % (construcción: C1–C9 de C1–C12 completas; v1.0 y v1.1 listas)
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
1. **Director:** revisar la vista previa del PR #67 y dar el **OK escrito para publicar**; ofrecer el diagnóstico gratis a NEODENTIS, Clínica Virtual Dent, Clínica Dental Cano y The Dental Clinic & GT Concept (bitácora 28/09)
2. **Al publicar:** migración que hace obligatoria `consent_version` → fusionar el PR #67. El **1/10**, aprobar la corrida de octubre (issue) lanzando *Corrida mensual* en modo `correr`
3. Ventas desde el 05/10 con el guion y los planes; luego **C10** (agencias) y planificar **C-009** (ADR-006, 120 respuestas en pagados)

## Bloqueos / esperando decisión
- ⏳ **Al publicar la landing (C9b):** migración que haga obligatoria `prospects.consent_version` (0009 la dejó opcional)
- ⏳ **Director:** revisar INDECOPI (clases 35 y 42) y eminia.pe antes de comprar o registrar (si no están libres → Prominia). Libro de Reclamaciones publicado sin domicilio del proveedor, correlativo ni copia por correo (revisión legal)
- ⏳ **RUC y régimen tributario** (contador) antes del primer cobro. Define si los S/ 349 incluyen IGV (neto ≈ S/ 296) → revisar la meta de la semana 6
- ⏳ Confirmar a los 8 días que el job diario mantiene activo Supabase dev (C1-T05)
- 🔽 Prueba API Gemini (informativa, baja prioridad): config. B, 1 de 10 hecha (rama `chore/prueba-api-gemini`)

## Decisiones recientes (últimas 5)
- 2026-09-28 · **Semáforo del diagnóstico frente al líder**: tu cifra ÷ la del líder; Bien ≥ 80 %, Regular 40–80 %, Bajo < 40 %, «Sin datos» si el líder está en 0 (Maps: reseñas). Plan de acción: siempre las 3 acciones de mayor impacto (respuestas de diferencia con el líder). RUC 10707993435 en el pie
- 2026-09-28 · **Diagnóstico rediseñado (C-008)**: resumen con semáforo de 4 áreas (criterio Eminia), frases literales de la competencia (gpt-5-nano solo elige, costo en el presupuesto vía 0010), dónde te falta estar, plan de acción; 7 páginas. Landing: ilustraciones propias, 6 cifras verificadas, tabla de planes, pedido por WhatsApp; efectos inspirados en trendos.com
- 2026-09-28 · **ADR-006**: los planes pagados medirán **120 respuestas/mes** por mercado (20 preguntas × 3 × ChatGPT y Google), el diagnóstico gratis sigue en 60; presupuesto +US$2.50 por mercado de cliente que pagó; Gemini manual; investigar Vertex AI. Sin construir (C-009). PRD HU-14: diagnóstico ≤ 8 páginas
- 2026-09-28 · **Marca Eminia** (ADR-005) y oferta para las llamadas: planes Diagnóstico gratis / Medir (S/ 349 + 490) / Gestionado (S/ 790 + 990), sin permanencia, precio fundador (5 primeras) y garantía de entrega en 10 días; fase C9b antes de C10 (acta 2026-09-28)
- 2026-09-27 · **C9 cerrada, v1.1 lista** (tag `v1.1`): pagos manuales con las reglas de «al día» aprobadas (5 días de gracia, aviso 7 días antes, IGV configurable), kit de atribución y conteo «por IA» en el reporte; migración 0008 en prod

## Bandeja de pendientes
- Ver `memoria/cambios-pendientes.md` (0 sin clasificar)
