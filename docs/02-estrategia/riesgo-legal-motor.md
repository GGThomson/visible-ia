# ⚖️ C-001 · Riesgo legal del motor de medición (Fase 2, prioridad n.º 1)
<!-- Pedido por el Director el 26/09/2026. Estado: ANÁLISIS Y OPCIONES. No es asesoría legal: antes de vender, conviene una consulta breve con un abogado de TI/datos. -->

## La pregunta
El producto necesita **consultar a las IAs de forma repetida, guardar las respuestas y analizarlas**: extraer las clínicas mencionadas, contar menciones, anotar fuentes y comparar en el tiempo. La pregunta es qué forma de hacerlo respeta los términos de cada proveedor, qué datos podemos guardar y por cuánto tiempo.

## 1. Cómo miden los competidores
| Competidor | Método declarado | Fuente |
|---|---|---|
| **Otterly.AI** | Envía los prompts a las **interfaces públicas** de las IAs "para reflejar lo que ve el usuario". Guarda cada respuesta y extrae menciones, posición, sentimiento y dominios citados. Usa API solo para Claude | [Trakkr: exactitud de datos de Otterly](https://trakkr.ai/reviews/otterly-review/data-accuracy) · [Otterly: funciones](https://otterly.ai/features) |
| **Peec AI** | **Scraping de la interfaz y automatización de navegador** ("query AI search engines exactly as a real user would"). Usa API solo en modelos opcionales (Claude) | [Discovered Labs: reseña de Peec AI](https://discoveredlabs.com/blog/peec-ai-review-best-for-ai-visibility-monitoring-use-cases-limits-alternatives) · [Peec AI](https://peec.ai/product/ai-visibility) |
| **Profound** | Captura las respuestas **"front-end"**, de los sitios reales y no de las APIs. Además usa paneles de conversaciones reales de usuarios, con opt-in | [Profound: Answer Engine Insights](https://www.tryprofound.com/features/answer-engine-insights) · [Reseña de N. Lafferty](https://nicklafferty.com/reviews/profound-best-aeo-geo-platform-for-ai-search/) |
| **CreceRank** | "Simula los prompts" a diario en ChatGPT, Gemini, Perplexity y AI Overviews. Lanza cada prompt **≥ 3 veces en sesiones separadas** y da un % de aparición. No publica si usa API o interfaz | [CreceRank: clínicas dentales](https://crecerank.com/como-medir-visibilidad-ia-clinicas/) · [CreceRank](https://crecerank.com/) |

**Lectura:**
- **Los líderes miden automatizando la interfaz de consumo.** Así obtienen lo que ve el usuario, pero es justo lo que prohíben los términos de consumidor (ver la sección 2). Asumen ese riesgo porque tienen escala, abogados y capital.
- **Nosotros ya descartamos esa vía:** el brief prohíbe automatizar las apps de consumo.
- **CreceRank usa nuestro mismo método estadístico:** ≥ 3 repeticiones y un porcentaje de aparición. Eso valida el método del índice.

## 2. Qué dicen los términos
| Proveedor / vía | ¿Se puede guardar y analizar? | Cita clave | Fuente |
|---|---|---|---|
| **App de ChatGPT** (consumidor), automatizada | ❌ **No.** Prohíbe la extracción automática | *"automatically or programmatically extract data or Output"* (conducta prohibida) | [OpenAI Terms of Use](https://openai.com/policies/row-terms-of-use/) |
| **API de OpenAI** (Responses + *web search*) | ✅ **Sí, en principio.** El cliente es dueño del Output | *"you … own the Output"*; OpenAI *"assign[s] to you all our right, title, and interest … in and to Output"*. ⚠️ No encontré restricciones específicas sobre los resultados de *web search*. Hay que verificarlo en los *Service Terms*: la página bloqueó la descarga automática | [OpenAI Terms of Use](https://openai.com/policies/row-terms-of-use/) · [Services Agreement](https://openai.com/policies/services-agreement/) |
| **API de Gemini con Search** | ❌ **No.** Prohíbe analizar y almacenar | *"cache, frame, syndicate, resell, **analyze**, train on, or otherwise learn from Grounded Results"*. Solo se puede guardar el texto ≤ 2 años para evaluar cómo se muestra, conservar el historial del usuario o reenviarlo para refinar. Hay que **mostrar las Search Suggestions** | [Gemini API Additional Terms](https://ai.google.dev/gemini-api/terms) |
| **API de Gemini con Maps** | ⚠️ **Muy limitado** | Caché ≤ **90 días** (optimización) o ≤ 6 meses (historial). Prohíbe *"scrape or export any Google Maps Data"* | ídem |
| **App de Gemini** (consumidor), automatizada | ❌ No hacerlo: el brief ya lo prohíbe | — | — |
| **SerpApi** (Google Modo IA / AI Overviews) | ⚠️ **Sí, bajo nuestra responsabilidad** | *"SerpApi assumes liability for the lawful collection of public search data … but not for how that data is ultimately used."* El **Legal Shield** (hasta US$2M) solo está en los planes **Production o superiores** (desde US$150/mes), *"provided your use … is not illegal"*. SerpApi borra las búsquedas a los 31 días; con *ZeroTrace* no guarda nada | [SerpApi Legal](https://serpapi.com/legal) · [Precios](https://serpapi.com/pricing) |
| **DataForSEO** (Google Modo IA) | ⚠️ **Sí, con indemnidad a cargo del cliente** | §7.1: los datos SERP *"shall not be used to compete with or adversely affect the business interests of the search engine providers"*. §7.2: el cliente **indemniza** a DataForSEO si viola la §7.1. No regula cuánto tiempo guardar | [DataForSEO Terms of Service](https://dataforseo.com/terms-of-service) |
| **Contexto: Google contra SerpApi** | ⚠️ Riesgo abierto | Google demandó el 19/12/2025. El **20/07/2026** la jueza desestimó las demandas DMCA sobre resultados sin contenido protegido; Google puede presentar una demanda corregida más acotada | [Search Engine Roundtable](https://www.seroundtable.com/google-lawsuit-serpapi-dismissed-41731.html) · [Android Headlines](https://www.androidheadlines.com/2026/07/google-amends-lawsuit-serpapi-ai-scraping-search-results.html) · [Search Engine Land](https://searchengineland.com/google-sues-serpapi-466541) |

**Ley peruana (Ley 29733):**
- Las respuestas incluyen **nombres de médicos** (por ejemplo, "Dra. …"). Son datos personales de profesionales, aunque sean públicos.
- **Minimización:** guardar el nombre del establecimiento y, del profesional, solo lo que aparece como nombre comercial. Nada de pacientes.
- Hay que revisar con un abogado si se requiere inscribir un banco de datos ante la ANPD.

## 3. Opciones
| Opción | ChatGPT | Gemini | Google Modo IA | Riesgo legal | Parecido a lo que ve el paciente | Costo/mes (12 mercados) |
|---|---|---|---|---|---|---|
| **A. Interfaz automatizada** (como Otterly, Peec y Profound) | Scraping de la app | Scraping de la app | Scraping o SERP | 🔴 Alto: viola los términos de consumidor; lo prohíbe el brief | 🟢 Alto | Bajo en dinero, alto en infraestructura (proxies, navegadores) |
| **B. Solo APIs oficiales, incluida Gemini con grounding** | API OpenAI + web search | API Gemini + Search/Maps | SERP API | 🔴 Alto en Gemini: prohíbe "analyze" | 🟡 Medio | ≈ US$11 |
| **C. APIs donde los términos lo permiten + SERP para Google (recomendada)** | **API OpenAI + web search** (`user_location` = Lima) | **Sin API.** Muestra **manual** mensual en la app, como calibración (lo hace una persona) | **DataForSEO** (o SerpApi) | 🟡 Medio: depende del proveedor SERP y de un uso no competitivo | 🟡 Medio en ChatGPT, 🟢 alto en Google, 🟡 muestra en Gemini | ≈ US$9 más US$50 de depósito inicial en DataForSEO |
| **D. Solo lo más seguro** | API OpenAI + web search | No se mide | No se mide | 🟢 Bajo | 🔴 Bajo: Google, que es la IA que más ven los pacientes en Lima, queda fuera | ≈ US$9 |
| **E. Pedir permiso o una vía enterprise a Google** | — | Consultar a Google o las condiciones de Vertex AI | — | 🟢 si Google lo permite | 🟡 | Desconocido; lento |

### Recomendación: **C**, y abrir **E** en paralelo sin bloquear
- **ChatGPT por API:**
  - Somos dueños del Output, así que podemos guardarlo y analizarlo.
  - Se calibra cada mes contra la app con una muestra manual pequeña, y se informa la brecha.
- **Google Modo IA por un proveedor SERP:**
  - Es la IA que más ven los pacientes, y en nuestra muestra comparte fuentes con la app de Gemini (fichas de Maps).
  - **DataForSEO** es más barato, pero traslada el riesgo al cliente.
  - **SerpApi Production** (US$150/mes) incluye el Legal Shield. Solo vale la pena cuando haya ingresos.
- **Gemini, sin motor automático en la v1:**
  - Una muestra manual mensual en la app (p. ej., 1 repetición por pregunta y mercado) se informa como "calibración Gemini", no como índice.
  - Se puede ofrecer como parte del informe mensual del setup.
- **Cambio en el discurso de venta:** el índice mide "ChatGPT y Google (Modo IA)", más una muestra de Gemini.

### Qué datos guardar y por cuánto tiempo (propuesta para la opción C)
| Dato | ChatGPT (API) | Google Modo IA (SERP) | Gemini (muestra manual) | Plazo |
|---|---|---|---|---|
| Texto completo de la respuesta | ✅ Sí (somos dueños) | ✅ Sí, solo para auditoría | ✅ Sí (copia manual) | **12 meses**; luego se borra el texto y quedan las métricas |
| Métricas derivadas: clínica, posición, n.º de menciones, fuentes citadas, fecha, superficie | ✅ | ✅ | ✅ | Mientras el cliente esté activo, más 12 meses |
| Enlaces y dominios de las fuentes | ✅ | ✅ | ✅ | Igual que las métricas |
| Nombres de profesionales | Solo si aparecen como nombre del establecimiento | Igual | Igual | Igual que las métricas |
| Respuestas de Gemini API con grounding | ❌ No se usa | — | — | — |
| Datos de pacientes | ❌ Nunca | ❌ | ❌ | — |

## 4. Qué falta confirmar (antes de la fase 4)
1. **OpenAI:** revisar los *Service Terms* y la política de *web search*, y confirmar que guardar y analizar los resultados de la herramienta no tiene restricciones adicionales.
2. **DataForSEO:** confirmar que nuestro uso (informes de visibilidad para clínicas) no se considera "compete with or adversely affect" a Google. Confirmar también que admite ubicación Lima y español en AI Mode.
3. **SerpApi:** confirmar que el Modo IA consume 1 crédito y seguir la demanda corregida de Google.
4. **Google (opción E):** preguntar si existe una vía (Vertex AI u otra) que permita analizar respuestas con grounding para medir la visibilidad.
5. **Ley 29733:** hacer una consulta corta con un abogado de datos.
6. **Segunda opinión:** llevar esto a Gemini con `/contexto "riesgo legal del motor de medición"`.

## Decisión
_(Pendiente del Director. Cuando decida, se registra como ADR-002.)_
