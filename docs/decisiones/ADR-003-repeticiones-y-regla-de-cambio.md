# ADR-003 · Repeticiones por mes y regla de cambio del índice

- **Fecha:** 2026-09-26
- **Estado:** Aceptada
- **Decide:** Director
- **Consultados:** Claude Code (análisis en el PRD §5.5)

## Contexto
El PRD v1 mide cada mercado con 10 preguntas × 3 repeticiones por superficie al mes, es decir, 30 respuestas.
- **El margen es ancho:** con 30 respuestas, una clínica con 30 % de presencia tiene un margen de 17–48 % (intervalo de Wilson al 95 %).
- **La regla original casi nunca detecta cambios.** Decía "se informa un cambio solo si los intervalos no se solapan", y eso exigiría una subida de ≈ 36 puntos en un mes. El reporte mensual diría casi siempre "sin cambio claro".
- **Además, las repeticiones de una misma pregunta no son independientes**, así que el margen real es todavía mayor.

## Opciones consideradas
| Opción | Subida detectable (desde 30 %) | Costo API por mercado al mes | Plan gratis de SerpApi |
|---|---|---|---|
| A. 3 repeticiones + prueba de 2 proporciones sobre el índice combinado (60 respuestas) | ≈ 16 puntos al mes | ≈ US$0.77 | ~8 mercados |
| B. 9 repeticiones al mes | ≈ 13 puntos al mes por superficie | ≈ US$2.30 | ~2 mercados |
| C. Ranking mensual + tendencia con ventana móvil de 3 meses | ≈ 13 puntos por trimestre | ≈ US$0.77 | ~8 mercados |
| **D. A + C** | ≈ 16 puntos al mes (combinado) y ≈ 9–10 por trimestre | ≈ US$0.77 | ~8 mercados |

## Decisión
Elegimos **D**:
- **Repeticiones:** 3 por pregunta y superficie al mes, en una corrida mensual. Son 60 respuestas por mercado.
- **Cambio mensual:** se compara el **índice combinado** (ChatGPT + Google) de un mes con el del anterior, con una **prueba de 2 proporciones** (α = 0.05, bilateral).
  - Si es significativa, se informa "sube" o "baja".
  - Si no, "sin cambio claro".
  - Reemplaza la regla de "intervalos sin solaparse" del PRD §5.2.
- **Tendencia:** índice de **ventana móvil de 3 meses** (180 respuestas combinadas). Es el que se usa para hablar de evolución en el reporte mensual.
- **Por superficie:** se muestra el índice de cada superficie con su intervalo de Wilson. Los cambios por superficie solo se informan con la ventana de 3 meses.
- **Transparencia:** cada informe dice qué diferencia es detectable con los datos del periodo.

**Motivo:** detecta cambios reales sin costo adicional y dentro del plan gratis de SerpApi.

## Consecuencias
- **Positivas:**
  - El reporte mensual puede mostrar cambios reales: ~16 puntos al mes o ~10 por trimestre.
  - El costo no cambia.
- **Negativas / lo que aceptamos:**
  - Los cambios pequeños tardan hasta 3 meses en verse.
  - El índice combinado mezcla dos IAs con el mismo peso.
  - La correlación entre repeticiones hace que la prueba sea algo optimista. Se mitiga exigiendo significancia también en la ventana antes de afirmar una tendencia.
- **Qué habría que hacer si cambiamos de opinión:**
  - Con ingresos para un proveedor SERP de pago, pasar a B (9 repeticiones) o a B + C.
  - El modelo de datos ya guarda cada respuesta, así que el cambio es de configuración.
- **Documentos actualizados:**
  - `docs/03-especificacion/prd.md` (§5.2, §5.5, §8)
  - `docs/04-arquitectura/arquitectura.md`
