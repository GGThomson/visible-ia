# ADR-001 · Excluir Perplexity de la prueba completa y del MVP

- **Fecha:** 2026-09-26
- **Estado:** Aceptada
- **Decide:** Director
- **Consultados:** Claude Code (análisis de la muestra de la prueba de fuentes)

## Contexto
El brief y el protocolo de la prueba de fuentes contaban con 3 IAs (ChatGPT, Gemini y Perplexity), más Google (Modo IA / AI Overviews), que se añadió el 25/09. En la muestra del 26/09 el Director solo alcanzó a consultar Perplexity en Q01 y la descartó por dos motivos:
- **No localiza bien Lima sin sesión:** mezcla resultados de España.
- **Tiene poca adopción en Perú:** pocos pacientes la usarían para elegir clínica.

Las otras 3 superficies (ChatGPT, Gemini y Google Modo IA) respondieron las 10 preguntas y nombraron clínicas en 30 de 30 respuestas. Hay que decidir si Perplexity entra en la prueba completa y en el producto.

## Opciones consideradas
| Opción | Ventajas | Desventajas | Costo / esfuerzo |
|---|---|---|---|
| A. Mantener Perplexity (app sin sesión) | Cobertura más amplia; se vende como "todas las IAs" | Resultados contaminados por la ubicación (España). Mide un canal que casi no usan los pacientes de Lima | +90 consultas manuales (~3 h) en la prueba completa y más trabajo en cada informe |
| B. Mantener Perplexity con cuenta configurada en Lima | Arregla en parte la ubicación | Sigue con poca adopción. Una cuenta con historial sesga las respuestas y rompe el protocolo "sin sesión" | Igual que A, más la gestión de la cuenta |
| **C. Excluirla del MVP y reevaluarla en la v2 con la API Sonar y ubicación** | Enfoca el esfuerzo en las superficies que usan los pacientes de Lima (ChatGPT, Gemini y Google). La prueba completa baja a 270 consultas | El producto no cubre Perplexity en la v1. Si su adopción crece en Perú, llegamos tarde | Ninguno ahora. En la v2, la API Sonar es de pago y requiere la aprobación del Director |

## Decisión
Elegimos **C**: Perplexity queda **fuera de la prueba completa y del MVP**. Los motivos son su **baja adopción en Perú** y que **sin sesión no localiza bien Lima**. Se **reevalúa en la v2** con su **API Sonar**, pasándole la ubicación (Lima) en la consulta.

## Consecuencias
- **Positivas:**
  - La prueba completa queda en **3 superficies** (ChatGPT, Gemini y Google Modo IA): 30 × 3 × 3 = **270 consultas** (~9–10 h).
  - El producto y los informes se concentran en las IAs que más ven los pacientes de Lima.
- **Negativas / lo que aceptamos:**
  - No medimos Perplexity en la v1. En la venta no se promete "todas las IAs", sino "ChatGPT, Gemini y Google".
- **Qué habría que hacer si cambiamos de opinión:**
  - Probar la API Sonar con ubicación en las 10 preguntas de la muestra, después de estimar su costo y con la aprobación del Director.
  - Añadir `perplexity` como superficie en el extractor.
  - Actualizar el brief, el PRD y el informe.
- **Documentos actualizados:**
  - `docs/00-inicio/brief.md`
  - `docs/01-descubrimiento/investigacion.md` (protocolo)
  - `memoria/ESTADO.md`
