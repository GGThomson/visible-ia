# 💵 Costo mensual de medir con API (insumo para la fase 4)
<!-- Pedido por el Director el 26/09/2026. Precios consultados ese día en las páginas oficiales (fuentes al final). Revisar antes de decidir: cambian a menudo. -->

## Supuestos
- **Mercado** = rubro + distrito (p. ej., implantología en Miraflores). Por mercado y por mes: **10 preguntas × 3 repeticiones = 30 llamadas por superficie**.
- **Llamadas al mes por superficie:**
  | Escenario | Mercados | Llamadas |
  |---|---|---|
  | Chico | 5 | **150** |
  | Mediano | 12 | **360** |
  | Grande | 30 | **900** |
- **Tokens por llamada**, medidos en nuestra prueba (19 llamadas a Gemini 2.5 Flash con Search):
  - Entrada: ~16 de pregunta + ~180 de herramienta.
  - Salida: ~560 de respuesta + ~510 de razonamiento.
  - Para el cálculo se usa un margen: **300 de entrada y 1,600 de salida**.
- **Búsquedas por llamada:** Gemini hizo en promedio **3.3 búsquedas en Google** por pregunta (entre 2 y 5). Para Maps se asume 1 consulta por llamada.
- **OpenAI** (no medido): se asumen **2 búsquedas por llamada**, más ~5,000 tokens de contenido de búsqueda cobrados como entrada. Un caso alto con 3 búsquedas aparece aparte.
- Tipo de cambio de referencia: US$1 ≈ S/ 3.75.

## Precios oficiales usados
| Superficie | Modelo / plan | Precio | Fuente |
|---|---|---|---|
| **Gemini (API)** | Gemini 3.8 Flash, nivel de pago | Entrada US$0.75 / 1M tokens y salida US$3.75 / 1M **hasta el 31/12/2026**. **Desde el 01/01/2027: US$1.50 y US$7.50** | [Precios Gemini API](https://ai.google.dev/gemini-api/docs/pricing) |
| | Search (grounding) con 3.x | **5,000 búsquedas gratis al mes** (compartidas entre modelos 3.x), luego **US$14 / 1,000 búsquedas**. *"You will be charged for each individual search query performed."* | ídem |
| | Maps (grounding) con 3.x | **5,000 al mes gratis**, luego US$14 / 1,000 | ídem |
| | Gemini 2.5 Flash, nivel de pago (alternativa) | Entrada US$0.30 y salida US$2.50 / 1M. Search: 1,500 consultas al día gratis, luego US$35 / 1,000. Maps: 1,500 al día gratis, luego US$25 / 1,000 | ídem |
| **ChatGPT (API)** | gpt-5-mini | Entrada US$0.25 y salida US$2.00 / 1M tokens | [Precios OpenAI API](https://developers.openai.com/api/docs/pricing) |
| | Herramienta *Web search* | **US$10 / 1,000 búsquedas + tokens de contenido de búsqueda a la tarifa del modelo** (en modelos sin razonamiento: US$25 / 1,000, con esos tokens gratis) | ídem |
| **Google Modo IA** | SerpApi, [Google AI Mode API](https://serpapi.com/google-ai-mode-api) | Gratis: 250 búsquedas al mes · Starter: US$25/mes por 1,000 · Developer: US$75 por 5,000 · Production: US$150 por 15,000 | [Precios SerpApi](https://serpapi.com/pricing) |
| | DataForSEO, [AI Mode SERP API](https://dataforseo.com/apis/serp-api/google-ai-mode-serp-api) | **US$0.0012 por consulta** (cola estándar) · US$0.0024 (prioritaria) · US$0.004 (en vivo). **Pago mínimo de US$50** | [Precios DataForSEO](https://dataforseo.com/pricing) |

## Costo por llamada
| Superficie | Cálculo | Por llamada |
|---|---|---|
| Gemini 3.8 Flash + Search + Maps | Tokens: 300 × 0.75/1M + 1,600 × 3.75/1M = US$0.0062. Búsquedas: gratis mientras no se pasen las 5,000 al mes | **US$0.0062** (desde 2027: US$0.0124) |
| Gemini 2.5 Flash + Search + Maps | 300 × 0.30/1M + 1,600 × 2.50/1M. Búsquedas gratis bajo 1,500 al día | **US$0.0041** |
| OpenAI gpt-5-mini + web search | 2 × US$0.01 + 5,300 × 0.25/1M + 1,500 × 2.00/1M | **US$0.0243** (alto, con 3 búsquedas: US$0.0343) |
| Google Modo IA (DataForSEO, cola estándar) | 1 consulta | **US$0.0012** |
| Google Modo IA (SerpApi) | 1 crédito (⚠️ no confirmado que el Modo IA gaste un solo crédito) | Según el plan |

## Costo mensual por escenario (US$)
| Superficie | 5 mercados (150) | 12 mercados (360) | 30 mercados (900) |
|---|---|---|---|
| Gemini 3.8 Flash (2026) | 0.93 | 2.24 | 5.60 |
| Gemini 3.8 Flash (desde 2027) | 1.87 | 4.48 | 11.21 |
| Búsquedas de Gemini: ¿entran en las 5,000 gratis? | Sí (≈ 500 + 150 de Maps) | Sí (≈ 1,190 + 360) | Sí (≈ 2,970 + 900) |
| OpenAI gpt-5-mini + web search | 3.65 (alto: 5.15) | 8.76 (alto: 12.36) | 21.89 (alto: 30.89) |
| Google Modo IA · DataForSEO | 0.18 | 0.43 | 1.08 |
| Google Modo IA · SerpApi | 0 (plan gratis de 250) | 25 (Starter) | 25 (Starter) |
| **Total con DataForSEO** (2026) | **≈ 4.76** | **≈ 11.43** | **≈ 28.57** |
| **Total con SerpApi** (2026) | **≈ 4.58** | **≈ 36.00** | **≈ 52.49** |
| Total con DataForSEO, en soles | ≈ S/ 18 | ≈ S/ 43 | ≈ S/ 107 |

**Lectura:**
- **El costo no es el problema.** Medir un mercado cuesta ~US$1 al mes, y una sola clínica paga S/ 349 (≈ US$93).
- **El costo lo domina OpenAI**, sobre todo por las búsquedas a US$10 / 1,000.
- **Hay un desembolso inicial:** DataForSEO pide un pago mínimo de **US$50**, más que el tope de US$20 de la validación. Con 5 mercados, el plan gratis de SerpApi cubre Google sin pagar nada.
- **En 2027 sube Gemini:** el precio de los tokens de Gemini 3.8 Flash se duplica, pero el total apenas cambia (≈ +US$5.6 en el escenario grande).

## Hasta dónde alcanza el nivel gratuito de Gemini
- **Gemini 3.x:** en el nivel gratuito, Search y Maps figuran como **"Not available"**. Lo comprobamos: la llamada devuelve el error 429.
- **Gemini 2.5 Flash:**
  - La página de precios dice que el grounding del nivel gratuito es *"Free of charge, up to 500 RPD"*.
  - Pero el límite real del modelo fue **20 llamadas al día**. Así lo dice el error: *"limit: 20 requests per day on Free Tier"*.
  - Corriendo todos los días, eso da **~600 llamadas al mes**. En teoría cubre 5 mercados (150) y 12 mercados (360), pero no 30 (900).
  - En la práctica es frágil: sin margen para reintentos, sin control de cuándo se reinicia la cuota, y una sola superficie por modelo.
- **Privacidad:** en el nivel gratuito, Google usa lo enviado para mejorar sus productos, y **personas pueden leer y anotar** las entradas y salidas. Los términos dicen: *"Do not submit sensitive, confidential, or personal information to the Unpaid Services."* Las preguntas de paciente son públicas, pero **no** se deben enviar datos de clientes.
- **Conclusión:** el nivel gratuito sirve para **pruebas internas**, no para el producto.

## Qué dicen los términos de Gemini sobre uso comercial ([Gemini API Additional Terms](https://ai.google.dev/gemini-api/terms))
1. **Uso profesional:** la API es *"for developers building with Google AI models for professional or business purposes, not for consumer use"*. El uso comercial está permitido; es para lo que está pensada.
2. **Región:** *"You may use only Paid Services when making API Clients available to users in the European Economic Area, Switzerland, or the United Kingdom."* No aplica a Perú, pero sí si algún día hay clientes allí. Además, hay que ser mayor de 18 años.
3. **⚠️ Grounding con Search, el punto crítico.** Los términos dicen que no se puede *"cache, frame, syndicate, resell, **analyze**, train on, or otherwise learn from Grounded Results or Search Suggestions"*.
   - Solo se permite guardar el texto hasta **2 años** para casos concretos: evaluar la calidad de cómo se muestra, conservar el historial de chat del usuario, o reenviar el resultado para refinarlo.
   - También exigen **mostrar las "Search Suggestions"** junto al resultado.
   - Nuestro producto **guarda y analiza** esas respuestas (extrae clínicas, cuenta menciones, compara en el tiempo). Eso **choca, en principio, con esta restricción**.
4. **⚠️ Grounding con Maps:**
   - Se puede guardar un máximo de **90 días** (para optimización) o **6 meses** (para historial de chat).
   - Prohíbe *"scrape or export any Google Maps Data"* y entrenar con esos datos.
   - Hay que atribuir a "Google Maps" en cada fuente que se muestre.
5. **Implicación:** usar Gemini con grounding como motor de medición del producto tiene un **riesgo de términos de uso alto**. Hay que revisarlo en la **fase 2 (legal)** antes de diseñar la arquitectura. Registrado como pendiente C-001.
   - Alternativas a evaluar: medir solo la app de Gemini a mano como calibración; usar Gemini **sin** grounding (no representa la app); o consultar a Google.
   - OpenAI y los proveedores de SERP tienen sus propios términos, que también hay que revisar. El scraping de Google vía SerpApi o DataForSEO tiene su propio riesgo: SerpApi ofrece un "U.S. Legal Shield" solo desde el plan Production, de US$150 al mes.

## Advertencias
- **La API no es la app.** En nuestra prueba, la API de Gemini con solo Search compartió clínicas con la app en 5 de 7 preguntas, pero usó otras fuentes. Falta la configuración con Maps. Cualquier costo de aquí asume que la API es una medida válida, y eso todavía no está demostrado.
- **Supuestos sin medir:** las búsquedas y los tokens de OpenAI, y si el Modo IA gasta un solo crédito en SerpApi. Se miden con 10 llamadas de prueba antes de decidir (costo < US$1, requiere aprobación).
- **Precios del 26/09/2026.** Revisar las fuentes el día de la decisión.

## Fuentes (consultadas el 26/09/2026)
- Precios Gemini API: https://ai.google.dev/gemini-api/docs/pricing
- Términos adicionales de Gemini API: https://ai.google.dev/gemini-api/terms
- Grounding with Google Maps: https://ai.google.dev/gemini-api/docs/maps-grounding
- Precios OpenAI API: https://developers.openai.com/api/docs/pricing
- Web search de OpenAI (ubicación aproximada con `user_location`): https://developers.openai.com/api/docs/guides/tools-web-search
- Precios SerpApi: https://serpapi.com/pricing · Google AI Mode API: https://serpapi.com/google-ai-mode-api
- DataForSEO AI Mode SERP API: https://dataforseo.com/apis/serp-api/google-ai-mode-serp-api · Precios: https://dataforseo.com/pricing
- Datos de tokens y búsquedas: `docs/01-descubrimiento/prueba-fuentes/registro-api-crudo.jsonl` (rama `chore/prueba-api-gemini`)
