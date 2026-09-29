# ADR-006 · 120 respuestas al mes para los planes pagados

- **Fecha:** 2026-09-28
- **Estado:** Aceptada. **Todavía no se construye:** se implementa en una tarea propia (cambio C-009).
- **Decide:** Director
- **Consultados:** Claude Code (cálculo del rango y del costo)
- **Relación:** amplía el ADR-003 (repeticiones y regla de cambio) solo para los clientes que pagan; el diagnóstico gratis sigue igual.

## Contexto
- Hoy cada mercado se mide con **60 respuestas al mes**: 10 preguntas × 3 veces × ChatGPT y Google (ADR-003, PRD §5).
- Con 60 respuestas el rango es ancho. Una clínica en 30 % tiene un rango de **20–43 %** (Wilson, 95 %), y un cambio real de un mes a otro casi nunca se distingue del azar.
- Además, las 3 repeticiones de una misma pregunta no son independientes: más **preguntas distintas** ayudan más que más repeticiones.
- Quien paga el Plan Medir o el Gestionado espera ver si sube. El diagnóstico gratis solo necesita una foto del mes.

## Opciones consideradas
| Opción | Ventajas | Desventajas | Costo / esfuerzo |
|---|---|---|---|
| A · Todo en 60 respuestas (hoy) | Simple; ya funciona | Rango ancho; el reporte mensual dice casi siempre «sin cambio claro» | 0 |
| **B · 120 para los mercados con cliente que paga; 60 para el diagnóstico** | Rango más estrecho donde importa; 20 preguntas reducen la dependencia entre repeticiones | Más costo por mercado pagado; bancos de 20 preguntas por rubro | ≈ US$2 más por mercado pagado al mes |
| C · 120 para todos los mercados | Un solo método | Duplica el costo de mercados sin cliente | El doble para todo |

## Decisión
Elegimos **B**:
- **Planes pagados:** **120 respuestas al mes por mercado**: **20 preguntas × 3 veces × ChatGPT y Google**. Con 120 respuestas, la clínica en 30 % pasa a un rango de **23–39 %**.
- **Diagnóstico gratis:** se queda en **60 respuestas** (10 preguntas × 3 × 2), como hoy.
- **Presupuesto:** el tope mensual de OpenAI sube **US$2.50 por cada mercado de un cliente que pagó** ese mes, sobre los US$5 actuales. Una llamada de ChatGPT cuesta en promedio ≈ US$0.032 (`data/tarifas.toml`): 60 llamadas más ≈ US$1.92, más la extracción; US$2.50 deja margen.
- **Gemini** sigue como **muestra manual** de calibración (PRD §5.4), no en la corrida automática.
- **Pendiente de investigar:** **Vertex AI** (Gemini con búsqueda por API y términos de uso empresariales), para ver si Gemini puede entrar en la corrida automática sin el riesgo legal del ADR-002.

## Consecuencias
- **Positivas:**
  - Rango más estrecho y cambios mensuales más fáciles de detectar para quien paga.
  - El diagnóstico gratis no sube de costo.
- **Negativas / lo que aceptamos:**
  - **Bancos de preguntas:** hacen falta **20 plantillas por rubro** (hoy hay 10). Son 10 nuevas por rubro, redactadas y aprobadas como las actuales.
  - **SerpApi (Google Modo IA):** cada mercado pagado usa 60 búsquedas al mes. Con la cuota gratis de 250, caben unos 3 o 4 mercados pagados (más los diagnósticos). Pasar ese punto exige un plan pagado de SerpApi o una alternativa: **decisión de dinero del Director** cuando llegue.
  - **Hay que actualizar la especificación al implementarlo:** PRD §5 (60 → 120 en pagados; HU-01 y HU-04) y la regla de cambio del ADR-003 con el nuevo tamaño de muestra.
  - **Comparabilidad:** el mes en que un mercado pasa de 60 a 120 respuestas, el reporte debe decirlo.
- **Si cambiamos de opinión:** volver a 60 es bajar el número de preguntas del mercado; los meses medidos con 120 siguen siendo válidos.
