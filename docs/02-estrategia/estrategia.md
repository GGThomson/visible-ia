# 🎯 Estrategia (Fase 2) · profundidad ●
<!-- Cómo va a ganar este proyecto. Base: acta 2026-09-25 (§5–8), fase 1 (investigacion.md), ADR-001 y ADR-002. Lo ya decidido no se reabre; esta fase lo junta y cierra lo que faltaba. -->

## Propuesta de valor
**Para** dueños y gerentes de clínicas de salud electiva de ticket alto en Lima Top **que** no saben si ChatGPT o Google (Modo IA) los recomiendan a ellos o a su competencia, **visible-ia** es un servicio de medición mensual **que** les dice en qué respuestas aparecen, frente a quién y qué arreglar para aparecer más. **A diferencia de** CreceRank, Otterly o Peec (pensados para marcas y en inglés) y del SEO local clásico (que no mide la IA), **nosotros** medimos por rubro y distrito, con datos locales de Lima, y entregamos arreglos concretos: ficha de Google, Doctoralia, web y redes.

**Qué sabemos de la fase 1 (muestra de 31 consultas):**
- En 30 de 30 respuestas la IA nombra clínicas concretas.
- La fuente principal es la ficha de Google Maps; le siguen Doctoralia, la web propia y las redes.
- Las respuestas varían mucho entre IAs.
- Por eso el producto se apoya en dos cosas: **medir con repeticiones** y **optimizar esas fuentes para la IA**.

## Lean Canvas
| Problema | Solución | Propuesta única | Ventaja injusta | Segmentos |
|---|---|---|---|---|
| 1. La clínica no sabe si la IA la recomienda. 2. No sabe qué hacer para aparecer. 3. Su agencia no tiene un producto de "IA" que vender | Índice de presencia mensual (ChatGPT + Google Modo IA + muestra de Gemini), competidores del mismo rubro y distrito, checklist de arreglos y reporte por WhatsApp | "Te decimos si la IA te recomienda en tu distrito y qué hacer para que lo haga", en español y con datos de Lima | Datos locales acumulados por rubro y distrito (histórico que nadie más tiene en Lima); método validado con la prueba de fuentes; primero en el nicho | Clínicas de implantología, estética dental, medicina estética y dermatología en Miraflores, San Isidro y Surco. Agencias de marketing que atienden a esas clínicas (marca blanca) |
| **Métricas clave** | **Canales** | **Estructura de costos** | **Fuentes de ingreso** | |
| Métrica norte (ver abajo). Informes gratis enviados → respuestas → demos → pagos. Índice de presencia de cada cliente | Contacto en frío uno por uno (Instagram DM y correo; WhatsApp cuando la clínica responde). Agencias por LinkedIn. Ranking gratis por rubro y distrito como gancho | API de OpenAI (≈ US$0.73 por mercado al mes), SerpApi (gratis al inicio), WhatsApp (≈ US$0.02 por respuesta), pasarela (≈ 4 % + IGV), dominio. Tiempo del Director: muestra manual de Gemini (≈ 20 min por mercado al mes) y setups | Clínica: S/ 349/mes por sede + S/ 490 de setup. Agencia: S/ 690/mes (hasta 5 sedes) + S/ 99 por sede extra | |

## Modelo de precios
**Planes** (decididos el 25/09; no se reabren):

| Concepto | Clínica directa | Agencia (marca blanca, aceptada el 26/09) |
|---|---|---|
| Mensual | **S/ 349 por sede** | **S/ 690** (hasta 5 sedes) + S/ 99 por sede extra |
| Setup | **S/ 490** (auditoría + schema + perfiles) | S/ 0 (la agencia ejecuta los checklists) |
| Entregables | Reporte por WhatsApp, alertas y soporte | Reportes PDF con el logo de la agencia |

> ✅ **Planes que se ofrecen en las llamadas desde el 05/10** (acta 2026-09-28, marca Eminia, ADR-005). Los precios siguen siendo **tentativos** (Director, 26/09) y se muestran **sin IGV** mientras el contador no defina el régimen.
>
> | Plan | Precio | Incluye |
> |---|---|---|
> | **Diagnóstico gratis** | S/ 0 | El informe de 7 páginas (resumen con semáforo y plan de acción; con «Por qué la IA eligió a tu competencia», «En qué preguntas apareces» y «Dónde te falta estar», C-008) |
> | **Plan Medir** | **S/ 349/mes** por sede + **S/ 490** de puesta a punto | Medición mensual en ChatGPT y Google Modo IA; panel; comparación con **3 competidores** en el reporte y el ranking completo en el panel; checklist; JSON-LD listo para la web; kit «¿Cómo nos conociste?» |
> | **Plan Gestionado** (**servicio principal**, «te ayudamos a que la IA te recomiende»; Director, 28/09) | **S/ 790/mes** + **S/ 990** de puesta a punto | Todo lo de Medir y, además, **nosotros** hacemos 3 mejoras al mes (ficha de Google, Doctoralia, web, pedido de reseñas) y una llamada de 15 min al mes. Es servicio manual: no se construye nada (C-004, H9) |
>
> Las agencias (S/ 690) **no van en la landing de clínicas**: tendrán su propia página en C10.
>
> **Ganchos aprobados por el Director (28/09):**
> - **Sin permanencia:** cancelas cuando quieras.
> - **Precio fundador** para las 5 primeras clínicas: la puesta a punto va a mitad de precio (S/ 245 en Medir, S/ 495 en Gestionado) y la mensualidad queda congelada 12 meses.
> - **Garantía de entrega:** se devuelve la puesta a punto si el checklist y los arreglos no se entregan en 10 días hábiles. **No** se garantiza subir en la IA.
>
> Si H9 se valida con el Gestionado, `/decision` para fijar el precio y revisar el PRD §7, que hoy excluye editar los perfiles del cliente dentro del producto (el servicio seguiría siendo manual).

**Costo variable por cliente al mes** (estimado; precios del 26/09/2026). La pasarela aplica solo a pagos con tarjeta; con Yape o transferencia el costo baja a ≈ S/ 4 por clínica:

| Concepto | Clínica (1 sede, 1 mercado) | Agencia (5 sedes, hasta 5 mercados) | Fuente |
|---|---|---|---|
| Medición con API (OpenAI + Google Modo IA): 30 llamadas por mercado | ≈ S/ 2.90 (US$0.77) | ≈ S/ 14.50 | [costos-medicion-api.md](../04-arquitectura/costos-medicion-api.md) |
| WhatsApp (reportes y alertas, ≈ 10 respuestas) | ≈ S/ 0.75 | — (PDF) | Acta del 25/09 (§3) |
| Pasarela de pago (Culqi online: 3.44 % + US$0.20 + IGV) | ≈ S/ 15.00 | ≈ S/ 29.00 | [Culqi: precios](https://culqi.com/precios/) · [Riqra: pasarelas en Perú 2026](https://blog.riqra.com/posts/pasarelas-pago-online-peru) |
| **Total variable** | **≈ S/ 19** | **≈ S/ 44** | |
| **Margen bruto sobre el precio** | **≈ 95 %** (≈ 94 % si el precio incluye IGV) | **≈ 94 %** | |

**Costos que no son de API:**
- **Tiempo:** la muestra manual de Gemini toma ≈ 20 min por mercado al mes. El setup (auditoría, schema y perfiles) toma ≈ 3–4 h por clínica, y se cobra S/ 490.
- **Costos fijos al inicio:**
  - Hosting: plan gratuito.
  - SerpApi: plan gratis de 250 búsquedas al mes, que cubre hasta ~8 mercados (30 búsquedas por mercado), o 5 con margen para reintentos y el informe gratis.
  - OpenAI: ≈ US$4/mes con 5 mercados. **Requiere tu aprobación antes de activar la facturación.**
  - WhatsApp API y dominio: se pagan con el primer cliente.
- **Punto de equilibrio:** **1 cliente** cubre todos los costos fijos del inicio.

> ⚠️ **Sin definir: ¿los S/ 349 incluyen IGV?** (anotado por el Director el 26/09). Si lo incluyen, el **ingreso real por clínica es ≈ S/ 296** (349 / 1.18), y lo mismo pasa con el setup (S/ 490 → ≈ S/ 415) y con el plan de agencia (S/ 690 → ≈ S/ 585). En ese caso hay que **revisar la meta de la semana 6**. Se confirma cuando el contador defina el régimen tributario.

**Precio frente a la competencia:** CreceRank cobra US$29/mes por 10 prompts (≈ S/ 109) y BrightLocal US$39/mes por local. S/ 349 se justifica porque incluye el análisis local por distrito, los competidores, el checklist y el reporte por WhatsApp. **Se valida con la venta** (H6).

## Salida al mercado (go-to-market)
- **Primeros 10 clientes:**
  - **Lista de 40 clínicas** (4 rubros × 3 distritos), armada desde Google Maps en la semana 1.
  - A cada una se le envía un **informe gratis personalizado**: "así te ve la IA frente a tus 3 competidores", uno por uno, por Instagram DM o correo. Se pasa a WhatsApp solo cuando la clínica responde.
  - En paralelo, se contacta a **10 agencias** por LinkedIn.
  - **Meta:** > 25 % de respuesta (H5) y S/ 2,500 en preventas o pilotos (H6).
- **Primeros 100:**
  - **Agencias con marca blanca**, como canal de escala: cada una trae 5–20 clínicas.
  - **Ranking gratis por rubro y distrito**, publicado en la landing como gancho.
  - **Referidos** de las primeras clínicas.
- **Canales:** Instagram DM y correo para el primer contacto; WhatsApp para dar seguimiento; LinkedIn para agencias. Sin envíos masivos (riesgo de bloqueo de WhatsApp).
- **Atribución, para reducir cancelaciones:** pregunta de intake "¿Cómo nos conociste? → IA", UTMs y cupones exclusivos en las recomendaciones (acta §5).

## Métrica norte
- ✅ **Sedes activas pagando con su reporte mensual entregado** (elegida por el Director el 26/09). Refleja a la vez el ingreso (sedes que pagan) y el valor entregado (el reporte llegó).
- **Métricas de entrada que la mueven:**
  - Informes gratis enviados por semana.
  - % de respuesta.
  - Demos.
  - % de conversión a pago.
  - % de clientes cuyo índice de presencia mejora en 90 días (la retención).
- **Metas a la semana 6 (08/11):** ≥ 3 sedes pagando o 2 agencias con piloto pagado (S/ 2,500).
  - ⚠️ **A revisar cuando se sepa si el precio incluye IGV.** Si lo incluye, 3 clínicas (setup + primer mes = 3 × S/ 839 = S/ 2,517 cobrados) dejan **≈ S/ 2,133 netos**, por debajo de la meta de S/ 2,500. Habría que subir a 4 clínicas o definir la meta como monto cobrado con IGV.

## Alcance del MVP / v1
**Dentro (semanas 1–6):**
1. **Motor de consultas** (ADR-002): API de OpenAI para ChatGPT, con `user_location` = Lima, y Google Modo IA vía SerpApi, con 3 repeticiones por pregunta. La muestra manual de Gemini se carga desde un formulario simple.
2. **Extractor:** clínicas mencionadas, posición y fuentes citadas.
3. **Puntaje de presencia:** índice por clínica, rubro y distrito, frente a los competidores, con la variabilidad a la vista.
4. **Informes:** PDF de diagnóstico (el informe gratis) y reporte mensual. Marca blanca: el PDF lleva el logo de la agencia.
5. **Recomendaciones:** checklist priorizado según la fase 1:
   1. Ficha de Google Business Profile.
   2. Doctoralia.
   3. Web con schema JSON-LD generado.
   4. Instagram y Facebook.
   5. Bing Places.
6. **Panel web:** evolución, competidores y tareas.
7. **WhatsApp:** reportes y alertas.
8. **Cuentas y pagos:** planes para clínica y agencia. **Al inicio se cobra con un link de pago manual** (Culqi o Mercado Pago, o Yape/transferencia), decidido el 26/09. La suscripción automática con pasarela integrada va en las semanas 5–6.

**Fuera (para después):**
- Perplexity (ADR-001; en la v2 con la API Sonar).
- Gemini automático (ADR-002; depende de una vía permitida por Google).
- Otras ciudades y rubros.
- Automatizar las apps de consumo (nunca).
- App móvil.
- API para agencias.
- Gestión automática de la ficha de Google (la hace la clínica o la agencia con el checklist).

## Aspectos legales
- **Motor de medición (C-001):** ✅ decidido → [ADR-002](../decisiones/ADR-002-motor-de-medicion.md).
  - **Qué se mide:** API de OpenAI para ChatGPT, Google Modo IA vía SerpApi (plan gratis al inicio) y una muestra manual mensual de Gemini.
  - **Retención:** texto 12 meses; métricas mientras el cliente esté activo más 12 meses; nada de pacientes.
  - **Análisis completo:** [riesgo-legal-motor.md](riesgo-legal-motor.md).
- **Tareas legales pendientes:**
  - [ ] Verificar que los términos de la API de OpenAI no restrinjan guardar y analizar los resultados de *web search*.
  - [ ] Confirmar que en SerpApi el Modo IA gaste 1 crédito y admita Lima y español.
  - [ ] Ley 29733: consulta breve con un abogado (nombres de médicos en las respuestas; ¿hay que inscribir un banco de datos?).
  - [ ] Riesgo registrado: la §7.1 de DataForSEO. Revisarla antes de migrar.
- **Datos de contacto de dueños y gerentes (venta en frío):**
  - Usar solo datos públicos del negocio (web, Instagram, ficha de Google).
  - Registrar de dónde salió cada contacto.
  - Ofrecer una opción de "no volver a contactar" y respetarla.
- **Documentos propios antes del primer cobro:**
  - Términos del servicio: qué medimos, que no prometemos "puesto #1" y cómo se cancela.
  - Política de privacidad.
  - Para agencias, un acuerdo simple de marca blanca.
- **Tributario:** el Director **aún no tiene RUC** (26/09).
  - [ ] **Sacar el RUC y elegir régimen antes del primer cobro**, con un contador.
  - Las clínicas son empresas y suelen pedir **factura** para deducir el gasto. El Nuevo RUS solo emite boletas, así que probablemente convenga el RER o el Régimen MYPE Tributario, que cobran IGV.
  - Con el régimen definido se decide si los precios **incluyen IGV** (neto S/ 295.8 por sede, margen ≈ 94 %) o se cobran **+ IGV** (la clínica paga S/ 411.8).
  - ⚠️ Es orientación general, no asesoría tributaria: confirmar con un contador.

## ✅ Puerta de aprobación
- **Aprobado por el Director el:** 2026-09-26
- **Queda abierto:** si los precios incluyen IGV (depende del régimen que defina el contador) y, con eso, revisar la meta de la semana 6.
