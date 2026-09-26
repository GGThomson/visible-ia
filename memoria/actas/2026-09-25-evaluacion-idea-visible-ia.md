# Acta 2026-09-25 · Evaluación y decisión de la idea "visible-ia"

- **Participantes:** Director (Gianpol Rosazza Bravo), Claude (planificador), Gemini (revisor crítico, 2 rondas)
- **Tema:** Elegir y validar una idea de SaaS rentable y escalable
- **Resultado:** Idea aprobada con ajustes. Se construye el sistema completo en paralelo con la venta.

---

## 1. Cómo se llegó a la idea
1. **Perfil del Director:** bots de WhatsApp y Telegram, juegos didácticos para empresas y sistemas automatizados de facturación. Experiencia previa en dropshipping y trading. Busca un SaaS con pago mensual, escalable y en cualquier país.
2. **Ideas descartadas o en reserva:**
   - Asistente SIRE para contadores y confirmación de pedidos contraentrega: validadas, pero con competencia clara.
   - Auditor de costos de WhatsApp: en reserva. Es un problema invisible, con urgencia por el cambio de precios de Meta del 1 de octubre de 2026.
   - Antifraude interno y clientes ignorados en WhatsApp: en reserva.
3. **Elegida:** visibilidad de negocios locales en asistentes de IA (ChatGPT, Gemini, Perplexity).

## 2. El problema
Cada vez más gente pregunta a la IA "¿cuál es la mejor clínica dental en Miraflores?" en vez de buscar en Google. El negocio no sabe si la IA lo recomienda o recomienda a su competencia. Puede estar primero en Google Maps y no existir para ChatGPT.

## 3. Hallazgos de la investigación (sept. 2026)
- **Adopción (EE. UU.):** el uso de IA para buscar negocios locales pasó de 6 % a 45 % en un año, y el 88 % verifica después lo que la IA dijo. Fuente: BrightLocal Local Consumer Review Survey 2026, con 1,002 adultos de EE. UU.
- **Latam:** no hay datos verificados de uso transaccional local. Es una **hipótesis a validar**. Gemini intuye que en Lima la IA se usa más para decisiones de ticket alto o de riesgo (salud, estética, abogados, colegios).
- **Fuentes de ChatGPT:** según Local Falcon, no usa directamente Google Business Profile. Se apoya en Bing Places, directorios y reseñas (Yelp, TripAdvisor, Foursquare), webs y Facebook. Gemini advierte que también rastrea la web abierta y plataformas verticales. **Se resuelve con la prueba de fuentes.**
- **Doctoralia:** posible fuente dominante que citan las IAs en salud en Perú. Podría ser una palanca clave, pero sin depender solo de ella.
- **Medición:** un estudio de Surfer con 1,000 prompts encontró que las respuestas por API coinciden solo un 24 % en marcas con lo que ve un usuario en la app. Se debe medir un **índice de presencia** con muestreo repetido y calibrar contra las apps reales.
- **WhatsApp:** desde el 1 de octubre de 2026, Meta cobra también las respuestas de servicio, alrededor de US$0.02 por mensaje en Perú. Hay que incluirlo en el precio.

## 4. Competencia
| Competidor | Enfoque | Precio de entrada |
|---|---|---|
| CreceRank | Marcas en Latam (incluye Perú) | US$29/mes (10 prompts), US$79 |
| BrightLocal | Negocios locales en EE. UU. | US$39/mes por local |
| Local AI Audit | Auditoría única en EE. UU. | US$297 |
| Otterly, Peec AI, Semrush, Profound, Yext, AthenaHQ | Marcas grandes y agencias | US$29–99+/mes o enterprise |
| Doctoralia / TopDoctors | Indirecto: dominan la presencia en salud | — |

**Diferenciación:** negocios locales latinos de ticket alto, **medición + arreglos concretos**, reporte por WhatsApp y ranking gratis por rubro y distrito como gancho.

## 5. Consenso entre Claude y Gemini
1. No prometer "puesto #1". Medir el índice de presencia con muestreo repetido y transparentar la variabilidad.
2. **Nicho inicial:** salud electiva de ticket alto en Lima Top (Miraflores, San Isidro, Surco). Implantología y estética dental, clínicas estéticas y dermatológicas.
3. **Separar** el SaaS (monitoreo, reportes, guías, schema generado) del servicio (setup cobrado aparte).
4. **Atribución** para reducir cancelaciones: pregunta de intake "¿Cómo nos conociste? → IA", UTMs y cupones exclusivos.
5. **Canal dual:** venta directa a clínicas como laboratorio de producto, y agencias como canal de escala. Gemini corrigió su postura inicial de "solo agencias".
6. Nada de infraestructura cara (proxies, scraping masivo) al inicio: APIs con búsqueda web más calibración manual.

## 6. Precios de validación (Perú)
| Concepto | Clínica directa | Agencia (marca blanca) |
|---|---|---|
| Mensual | S/ 349 por sede | S/ 690 (hasta 5 sedes) + S/ 99 por sede extra |
| Setup | S/ 490 (auditoría + schema + perfiles) | S/ 0 (la agencia ejecuta los checklists) |
| Entregables | Reporte por WhatsApp, alertas, soporte | Reportes PDF con el logo de la agencia |

## 7. Decisiones del Director
- ✅ **Construir el sistema completo**, en paralelo con la venta.
- ✅ **Contacto 100 % en frío** (sin red inicial), mensajes personalizados uno por uno, sin envíos masivos.
- ✅ Nicho, canal dual y precios según las secciones 5 y 6.
- ⏳ Pendiente: confirmar la aceptación de la marca blanca para agencias (propuesta: sí).

## 8. Plan (~6 semanas)
| Semana | Construcción | Ventas |
|---|---|---|
| 1 | Base + motor de consultas + extractor + puntaje + informe PDF. **Iniciar trámites** de WhatsApp Business API y pasarela de pagos | Lista de 40 clínicas y 10 agencias |
| 2 | Landing page + panel de demostración | Primeros contactos con informes reales |
| 3–4 | Panel web real + cuentas | Llamadas, demos, pilotos |
| 5–6 | WhatsApp automático, recomendaciones, pagos, marca blanca | Cierres y aprendizaje |

### Módulos del sistema
1. Motor de consultas (ChatGPT, Gemini, Perplexity, con repeticiones)
2. Extractor (clínicas mencionadas + fuentes citadas)
3. Puntaje de presencia (por clínica, rubro y distrito, contra competidores)
4. Informes (PDF de diagnóstico + reporte mensual)
5. Panel web (evolución, competidores, tareas)
6. Recomendaciones (Bing Places, Doctoralia, schema JSON-LD generado)
7. WhatsApp (reportes y alertas)
8. Cuentas y pagos (planes clínica y agencia, marca blanca)

## 9. Criterios de éxito y de replanteo
- **Prueba de fuentes:** ~30 preguntas × 3 IAs × 3 repeticiones (unas 270 consultas). Registrar las clínicas mencionadas y las fuentes citadas.
- **Interés:** más del 25 % de respuesta a los informes gratis (40 enviados → 10 interesados).
- **Pago:** 3 clínicas (setup + primer mes) o 2 agencias con piloto pagado. Meta total: **S/ 2,500 en preventas o pilotos**.
- **Replanteo:** si tras contactar 50 clínicas y 10 agencias con el informe nadie paga por adelantado, se reevalúa la idea (rubro, canal o descarte).

## 10. Riesgos a vigilar
- Precisión de la medición (API vs app) y volatilidad de las respuestas.
- Cancelaciones por falta de atribución visible.
- Dependencia de plataformas: Meta/WhatsApp, Doctoralia, cambios en las IAs.
- Términos de uso de cada proveedor de IA al consultar de forma automatizada.
- Que CreceRank u otro competidor baje al segmento local.

## 11. Tareas inmediatas
1. Iniciar los trámites de WhatsApp Business API y de la pasarela de pagos.
2. Definir las 30 preguntas de la prueba de fuentes.
3. Construir motor + extractor + puntaje + informe PDF.
4. Lista de 40 clínicas (Miraflores, San Isidro, Surco) y 10 agencias.
5. Plantillas de mensajes en frío para clínicas (WhatsApp/Instagram) y agencias (LinkedIn).

## Fuentes principales
- BrightLocal 2026 vía Bill Hartzer: https://www.billhartzer.com/local-search/ai-local-business-recommendations-45-percent/
- Local Falcon (fuentes de ChatGPT): https://www.localfalcon.com/blog/chatgpt-local-search-data-sources-where-does-business-info-come-from
- Surfer (API vs app): https://surferseo.com/blog/llm-scraped-ai-answers-vs-api-results
- CreceRank: https://crecerank.com/seo-para-chatgpt/
- Precios de herramientas de visibilidad IA: https://searcherries.com/ai-visibility-tool-pricing
- Precios de WhatsApp 2026: https://www.patagon.ai/blog-posts/whatsapp-business-api-pricing
