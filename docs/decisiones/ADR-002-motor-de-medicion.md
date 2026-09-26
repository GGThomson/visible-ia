# ADR-002 · Motor de medición del MVP: API de OpenAI + Google Modo IA vía SERP + muestra manual de Gemini

- **Fecha:** 2026-09-26
- **Estado:** Aceptada
- **Decide:** Director
- **Consultados:** Claude Code (análisis `docs/02-estrategia/riesgo-legal-motor.md`) · Claude en claude.ai (acta `memoria/actas/2026-09-26-riesgo-legal-motor.md`). Gemini no respondió antes de la decisión.

## Contexto
El producto necesita consultar a las IAs de forma repetida (10 preguntas × 3 repeticiones por mercado y mes), **guardar las respuestas y analizarlas**. El riesgo C-001 surgió de dos hechos:
- Los términos de la API de Gemini prohíben *"analyze"* y guardar los resultados obtenidos con grounding (Search), y limitan el caché de Maps a 90 días.
- Los términos de consumidor de OpenAI prohíben extraer datos de la app de forma automática.

Los competidores (Otterly, Peec AI, Profound) miden automatizando la interfaz web. Nosotros lo descartamos en el brief.

## Opciones consideradas
Detalle, citas y costos en `docs/02-estrategia/riesgo-legal-motor.md` (§3).

| Opción | Ventajas | Desventajas | Costo/mes (12 mercados) |
|---|---|---|---|
| A. Automatizar la interfaz (como la competencia) | Mide exactamente lo que ve el paciente | Viola los términos de consumidor; lo prohíbe el brief | Bajo en dinero, alto en infraestructura |
| B. Solo APIs, incluida Gemini con grounding | Todo automático | Choca con el "analyze" de los términos de Gemini | ≈ US$11 |
| **C. API de OpenAI + Google Modo IA vía SERP + muestra manual de Gemini** | Solo vías que permiten guardar y analizar (OpenAI), o donde el proveedor asume la recolección (SERP). Cubre la IA que más ven los pacientes (Google) | Gemini no se mide de forma automática. Riesgo residual en el proveedor SERP | ≈ US$9 |
| D. Solo la API de OpenAI | Es lo más seguro | Deja fuera a Google | ≈ US$9 |
| E. Pedir una vía a Google (Vertex AI u otra) | Podría habilitar Gemini | Lento e incierto | Desconocido |

## Decisión
Elegimos **C**:
- **ChatGPT:** API de OpenAI (gpt-5-mini + web search, `user_location` = Lima). Somos dueños del Output, así que podemos guardarlo y analizarlo. Se calibra cada mes con una muestra manual de la app.
- **Google Modo IA:** a través de un proveedor SERP. Se **empieza con el plan gratis de SerpApi** (250 búsquedas al mes ≈ 5 mercados × 30 llamadas + margen). Con el **primer ingreso** se pasa a **DataForSEO** (≈ US$1 al mes y un depósito mínimo de US$50) **o a SerpApi de pago**; se decide en ese momento.
- **Gemini:** sin motor automático. Una **muestra manual mensual** en la app, que se informa como "calibración Gemini", no como índice.
- **Datos y retención:**
  - Texto completo de las respuestas: **12 meses**.
  - Métricas derivadas (clínica, posición, menciones, fuentes, fecha, superficie): mientras el cliente esté activo **más 12 meses**.
  - Nombres de profesionales: solo cuando aparecen como nombre del establecimiento.
  - **Ningún dato de pacientes.**
  - Las respuestas de la API de Gemini con grounding **no se usan en el producto**.
- **Discurso de venta:** el índice mide "ChatGPT y Google (Modo IA)", más una muestra de Gemini.

**Motivos:** es la opción que cubre las IAs más usadas por los pacientes en Lima sin violar términos conocidos. Además, cabe en el presupuesto de validación.

## Consecuencias
- **Positivas:**
  - El motor es automatizable desde la semana 1 con costo ≈ US$0 en Google (plan gratis de SerpApi).
  - Guardar y analizar las respuestas de OpenAI está permitido: el cliente es dueño del Output.
- **Negativas / lo que aceptamos:**
  - **Gemini** solo se mide con una muestra manual.
  - **La API no es la app**, así que hay que calibrar e informar la brecha.
  - **Plan gratis de SerpApi:** no incluye el **Legal Shield** (solo desde US$150/mes) y SerpApi no responde por el uso de los datos.
  - **Google contra SerpApi:** la demanda sigue abierta (Google puede presentar una versión corregida).
  - **DataForSEO, §7.1:** prohíbe usar los datos *"to compete with or adversely affect the business interests of the search engine providers"*, y el cliente lo indemniza. Queda como **riesgo registrado** para cuando se migre.
  - **OpenAI no es gratis:** ≈ US$3.65 al mes con 5 mercados. **Activar la facturación de OpenAI requiere la aprobación explícita del Director**, dentro del tope de US$20 de la validación.
- **Pendientes de verificación:**
  1. Que los términos de la API de OpenAI no restrinjan guardar y analizar los resultados de *web search*.
  2. Que en SerpApi el Modo IA gaste 1 crédito y admita Lima y español.
  3. La Ley 29733: consulta breve con un abogado.
- **Qué habría que hacer si cambiamos de opinión:**
  - Si Google habilita una vía permitida (opción E), añadir Gemini al motor.
  - Si el riesgo SERP se materializa, pasar a la opción D (solo OpenAI) mientras se busca una alternativa.
- **Documentos actualizados:**
  - `docs/02-estrategia/riesgo-legal-motor.md`
  - `docs/02-estrategia/estrategia.md`
  - `docs/00-inicio/brief.md`
  - `memoria/ESTADO.md`
  - `memoria/cambios-pendientes.md`
  - `memoria/contexto-rapido.md`
