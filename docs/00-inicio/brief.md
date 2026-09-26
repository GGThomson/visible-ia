# 🪪 Brief del proyecto (Fase 0)
<!-- Lo llena /iniciar entrevistándote. Es la "cédula de identidad" del proyecto. -->
<!-- Fuente principal: memoria/actas/2026-09-25-evaluacion-idea-visible-ia.md -->

## Identidad
- **Nombre:** visible-ia
- **Tipo(s):** **A. SaaS / producto propio** + **J. Producto de datos / IA** (el núcleo es medir qué responden las IAs)
- **Fecha de inicio:** 2026-09-25
- **Director:** Gianpol Rosazza Bravo
- **Repositorio:** https://github.com/GGThomson/visible-ia

## Propósito
- **Problema que resuelve (en una frase):** un negocio local no sabe si ChatGPT, Gemini o Google (Modo IA) lo recomiendan a él o a su competencia, ni qué hacer para aparecer.
- **Para quién:**
  - **Clínicas (venta directa, laboratorio de producto):** salud electiva de ticket alto en Lima Top (Miraflores, San Isidro, Surco): implantología y estética dental, clínicas estéticas y dermatológicas.
  - **Agencias de marketing (canal de escala):** marca blanca para sus clientes.
- **Por qué ahora:** en EE. UU. el uso de IA para buscar negocios locales pasó de 6 % a 45 % en un año (BrightLocal 2026). En Latam aún no hay competidores enfocados en negocios **locales** (CreceRank apunta a marcas). En Latam la adopción es una **hipótesis a validar**.
- **Qué pasa si no se hace:** las clínicas siguen invisibles para la IA sin saberlo, y un competidor (CreceRank, BrightLocal) ocupa el segmento local latino.
- **Diferenciación:** medición + arreglos concretos (Bing Places, Doctoralia, schema JSON-LD), reporte por WhatsApp y ranking gratis por rubro y distrito como gancho. Sin promesas de "puesto #1": índice de presencia con muestreo repetido y variabilidad transparente.

## Éxito
- **Se considera exitoso si…** (medible):
  1. **Prueba de fuentes** completada: ~30 preguntas × 3 superficies (ChatGPT, Gemini y Google Modo IA) × 3 repeticiones (~270 consultas). Perplexity queda fuera del MVP ([ADR-001](../decisiones/ADR-001-excluir-perplexity.md)), con clínicas mencionadas y fuentes citadas registradas.
  2. **Interés:** > 25 % de respuesta a los informes gratis (40 enviados → 10 interesados).
  3. **Pago:** 3 clínicas (setup + primer mes) o 2 agencias con piloto pagado. **Meta: S/ 2,500 en preventas o pilotos.**
- **Criterio de replanteo:** si tras contactar 50 clínicas y 10 agencias con el informe nadie paga por adelantado → se reevalúa (rubro, canal o descarte).
- **Fecha objetivo:** sistema completo en ~6 semanas. Semana 1 = 28/09/2026 → fin de la semana 6 = 08/11/2026. Ventas desde la semana 2 (05/10).
- **Presupuesto:** **máximo US$20 en total durante la validación.** Ningún gasto sin aprobación previa del Director.
- **Horas disponibles:** tiempo completo (40+ h/semana), repartidas entre construcción y ventas.

## Precios de validación (Perú)
| Concepto | Clínica directa | Agencia (marca blanca) |
|---|---|---|
| Mensual | S/ 349 por sede | S/ 690 (hasta 5 sedes) + S/ 99 por sede extra |
| Setup | S/ 490 (auditoría + schema + perfiles) | S/ 0 |

## Restricciones conocidas
- **Técnicas:**
  - Solo **planes gratuitos** (hosting, base de datos, niveles gratis de APIs).
  - Donde una API de IA cueste, las consultas se hacen **a mano en las apps gratuitas** y un **script analiza las respuestas** (pegadas o exportadas). No se automatizan las apps de consumo porque violaría sus términos de uso.
  - Medición: índice de presencia con repeticiones. Calibrar API contra app (solo coinciden ~24 % según Surfer).
  - Nada de infraestructura cara (proxies, scraping masivo).
- **De negocio:**
  - WhatsApp Business API, pasarela de pagos y dominio **se pagan solo con el dinero del primer cliente**. Los trámites (verificación) sí se inician en la semana 1.
  - Contacto 100 % en frío, mensajes personalizados uno por uno, sin envíos masivos.
  - Desde el 01/10/2026 Meta cobra ~US$0.02 por respuesta de servicio en Perú: incluirlo en el precio.
  - Legal: Ley 29733 (datos personales, Perú) y términos de uso de cada proveedor de IA.
- **Personales:** tiempo completo. Experiencia en bots de WhatsApp/Telegram, facturación automatizada y juegos didácticos para empresas. Sin red de contactos inicial en el nicho.

## Ruta de fases elegida
| Fase | Profundidad | Motivo |
|---|---|---|
| 1 Descubrimiento | ●● | El acta ya cubre problema, competencia y mercado. Falta la **prueba de fuentes** (evidencia J) y registrar las respuestas de las clínicas como entrevistas |
| 2 Estrategia | ● | Nicho, canal y precios ya decididos (acta §5–7). Solo falta: legal (Ley 29733, términos de las IAs), métrica norte y costos con presupuesto ~0 |
| 3 Especificación | ●● | PRD de los 8 módulos. La v1 se congela en lo necesario para vender en la semana 2. Incluye cómo se evalúa el índice de presencia (J) |
| 4 Arquitectura y plan | ●● | Stack solo con planes gratuitos, ADR y roadmap de 6 semanas |
| 5 Construcción | ●●● | Plan de la §8 del acta: 8 módulos en 6 semanas |
| 6 Lanzamiento | ●● | La venta empieza en la semana 2, en paralelo. El lanzamiento formal llega con los primeros pagos |
| 7 Cierre | ● | Coincide con el punto de replanteo (50 clínicas + 10 agencias sin pago) |

**Calendario:** fases 1–4 ligeras del 25 al 27/09 · construcción del 28/09 al 08/11.

## Pendientes del acta
- ✅ Marca blanca para agencias: **aceptada** por el Director el 26/09/2026 (acta `memoria/actas/2026-09-26-riesgo-legal-motor.md`).

## Puertas de aprobación
<!-- Momentos en los que el Director debe decir "sí, avanzamos". -->
- [x] Brief aprobado (2026-09-25)
- [x] Descubrimiento → ¿vale la pena seguir? Sí (2026-09-26, muestra: 30/30 respuestas nombran clínicas)
- [ ] Especificación aprobada → se congela el alcance de la v1
- [ ] Plan aprobado → empieza la construcción
- [ ] Listo para lanzar
