# 🔎 Descubrimiento (Fase 1) · profundidad ●●
<!-- Objetivo: entender el problema ANTES de pensar en la solución. Tipo A (SaaS) + J (datos / IA). -->
<!-- Base: memoria/actas/2026-09-25-evaluacion-idea-visible-ia.md (investigación y 2 rondas con Gemini). -->

## Hipótesis iniciales
| # | Creemos que… | Lo sabremos cuando… | Estado |
|---|---|---|---|
| H1 | Las IAs nombran **clínicas concretas** de Lima Top al preguntarles por un rubro y un distrito, en vez de dar respuestas genéricas | En la prueba de fuentes, ≥ 60 % de las respuestas nombra al menos 1 clínica | ✅ muestra: 30/30 (100 %) |
| H2 | Las IAs se apoyan en **fuentes distintas de Google Maps** (Doctoralia, directorios, webs, reseñas) y esas fuentes se pueden trabajar | Las fuentes citadas se concentran en ≤ 10 dominios, y al menos 3 son accionables (perfil editable) | 🟡 accionables sí (≥ 4); pero la fuente n.º 1 **es** Google Maps → reformular |
| H3 | Las respuestas **varían** entre repeticiones y entre IAs, lo que justifica un índice con muestreo repetido | Menos del 70 % de las clínicas mencionadas se repite en las 3 repeticiones de una misma pregunta | 🟡 indicio: alta variación entre IAs; repeticiones → prueba completa |
| H4 | Hay **brecha Maps vs IA**: clínicas fuertes en Google Maps no aparecen en la IA (ese es el gancho de venta) | ≥ 5 de las 40 clínicas de la lista tienen ≥ 4.5★ y ≥ 100 reseñas en Maps, pero presencia IA ≈ 0 | ⚪ |
| H5 | Los dueños o gerentes de clínica **responden** a un informe gratis personalizado | > 25 % de respuesta (40 enviados → 10 interesados) | ⚪ |
| H6 | Las clínicas o agencias **pagan por adelantado** | S/ 2,500 en preventas o pilotos (3 clínicas o 2 agencias) | ⚪ |
| H7 | Las agencias ven valor en revender con **marca blanca** | ≥ 2 de 10 agencias piden piloto o precio | ⚪ |
| H8 | Los pacientes de ticket alto en Lima **ya usan IA** para elegir clínica | Proxy: ≥ 3 clínicas dicen en las llamadas que algún paciente mencionó ChatGPT/Gemini, o el intake "¿Cómo nos conociste? → IA" registra casos | ⚪ (hipótesis más débil; sin datos Latam) |

H1–H4 se prueban con la **prueba de fuentes** (sin clientes). H5–H8 se prueban con la **venta** (semanas 2–6).

## Usuarios / actores
| Actor | Qué necesita | Qué le duele hoy | Cómo lo resuelve hoy |
|---|---|---|---|
| **Dueño o gerente de clínica** (implantología, estética dental, medicina estética, dermatología) | Pacientes nuevos de ticket alto | No sabe si la IA lo recomienda ni qué hacer para aparecer. Invierte en Google/Instagram sin ver este canal | No lo resuelve ("no hacer nada") o su agencia hace SEO clásico |
| **Encargado de marketing** de la clínica (interno o freelance) | Mostrar resultados medibles al dueño | No tiene cómo medir la IA ni un checklist de acciones | Pregunta a ChatGPT a mano, sin método |
| **Agencia de marketing** (canal) | Un servicio nuevo que vender a su cartera | Los clientes preguntan por "IA" y la agencia no tiene producto ni reporte | Herramientas en inglés para marcas (Otterly, Peec, Semrush) que no sirven para lo local |
| **Paciente** (usuario final, no paga) | Elegir una clínica confiable | Muchas opciones, precios opacos, miedo a un mal resultado | Google Maps, Instagram, recomendaciones, Doctoralia y, cada vez más, IA (H8) |

## Prueba de fuentes (núcleo J)
**Objetivo:** probar H1–H4 y obtener datos reales para el primer informe PDF y para calibrar el extractor y el puntaje.

### Protocolo
- **Superficies (4):** ChatGPT, Gemini y Perplexity en sus **apps web gratuitas**, más **Google (Modo IA / AI Overviews)**, que es la IA que más pacientes ven en Lima (añadida por el Director el 25/09). Por la restricción de presupuesto no se usan APIs de pago (ver brief).
- **Cómo consultar Google:** hacer la búsqueda normal en google.com.pe. Si aparece un AI Overview, registrar ese texto con `modo` = `google-ai-overview`. Si no aparece, repetir la pregunta en **Modo IA** y registrarla con `modo` = `google-modo-ia`. Cuando no hay AI Overview, anotar en `notas` "sin AI Overview": ese dato también sirve.
- **Repeticiones:** 3 por pregunta y por IA, cada una en un **chat nuevo**.
- **Sesión:** sin iniciar sesión o en ventana de incógnito cuando la IA lo permita. Si exige cuenta, usar una cuenta **sin memoria ni historial** (desactivar "memoria" y "personalización"). Registrar en el campo `modo` cómo se hizo.
- **Ubicación:** desde Lima, sin VPN.
- **Registro:** copiar la respuesta **completa** y las fuentes citadas en [prueba-fuentes/registro.csv](prueba-fuentes/registro.csv): una fila por consulta.
  - `ia`: `chatgpt`, `gemini`, `perplexity` o `google`.
  - `busco_web`: `si` si la IA muestra que buscó en internet (indicador de búsqueda, enlaces o fuentes); `no` si respondió solo con lo que sabe.
  - `fuentes_citadas`: dominios separados por `;`. Si no muestra ninguna, escribir exactamente `sin fuentes visibles`.
- **Volumen de la prueba completa:** 30 preguntas × 4 superficies × 3 repeticiones = **360 consultas**, unas **12 h** de trabajo manual (~2 min por consulta). ⏳ Si Google se mantiene en la prueba completa o solo en la muestra se decide con los resultados de la muestra (con Google fuera: 270 consultas, ~9–10 h).
- **Análisis:** un script (módulo "extractor" de la semana 1) lee el CSV y saca las clínicas mencionadas, las fuentes y la frecuencia. Mientras tanto, conteo manual en una hoja.

### Muestra rápida (26/09) → puerta de la fase 1
Decisión del Director (25/09): la puerta se decide con una **muestra**, y la prueba completa se hace en la **semana 1**, en paralelo con la construcción.
- **Preguntas:** Q01, Q05, Q10, Q11, Q16, Q19, Q22, Q24, Q29 y Q30 (cubren los 4 rubros, los 3 distritos y Lima).
- **Volumen:** 10 preguntas × 4 superficies × 1 repetición = **40 consultas** (~1 h 20 min), sin sesión o en incógnito.
- **Regla de decisión:**
  - ✅ **Seguir** si ≥ 60 % de las respuestas (≥ 24 de 40) nombra al menos 1 clínica concreta (H1).
  - 🔁 **Pivotear** si < 40 % (< 16 de 40): las IAs no recomiendan clínicas en Lima. Probar otro rubro (abogados, colegios) o ciudad antes de construir.
  - ⚠️ Entre 40 % y 60 % (16 a 23 de 40): se sigue con cautela y se revisa en la prueba completa.

### Resultados de la muestra (26/09)
Datos en [prueba-fuentes/registro.csv](prueba-fuentes/registro.csv). Conteo manual. El extractor lo automatizará en la semana 1.

**Qué se hizo:** ChatGPT, Gemini y Google (Modo IA), completas: 10 preguntas cada una, más una 2.ª repetición de ChatGPT en Q22. Son 31 respuestas en total. **Perplexity** solo se hizo en Q01: el Director la descartó para la muestra porque sin sesión mezcla resultados de España y tiene poca adopción en Perú. Todas las consultas se hicieron en incógnito y en todas la IA buscó en la web.

**H1 (regla de la puerta):** **30 de 30** respuestas de las 3 superficies completas nombran ≥ 1 clínica concreta (100 %). Contando las 40 previstas y tomando como fallo las 9 de Perplexity que no se hicieron, quedan 31 de 40 (77.5 %). **Ambas cuentas superan el umbral de 24/40.** Casi todas las respuestas dan de 3 a 5 clínicas con nombre, dirección y ★. Las respuestas del tipo "no hay un único mejor" también terminan nombrando clínicas.

**H2 (fuentes):**
| Superficie | Fuente principal | Otras fuentes |
|---|---|---|
| Gemini | **Fichas de Google Maps** (10 de 10: tarjetas con ★, horario y dirección) | Webs propias y Doctoralia, pocas veces |
| Google Modo IA | **Fichas de Google (Business Profile)** en 7 de 10, con unas 20 fichas por consulta | Webs propias; **Doctoralia** en 4 de 10; **Facebook/Instagram** en 6 de 10; blogs y rankings (dentum.com.pe, pielbella, blogs de cuidamedic y de Zegarra) |
| ChatGPT | Datos de mapa (primero pasa la ubicación; da ★ y n.º de reseñas) | **Doctoralia** en 5 de 11; webs propias; limadentalrating.com; 1 respuesta sin fuentes |

- **Hallazgo clave:** la fuente dominante **es** la ficha de Google Maps, al contrario de lo que suponía H2 ("fuentes distintas de Google Maps"). La segunda palanca es Doctoralia. Detrás vienen la web propia, Instagram/Facebook y los sitios de ranking.
- **Fuentes accionables:** hay ≥ 4 fuentes con perfil editable (ficha de Google, Doctoralia, web propia, Instagram/Facebook). Esa parte de H2 se cumple.
- **Señal de "GEO" local:** muchas fichas que aparecen tienen palabras clave en el nombre ("Implantes Dentales Miraflores", "…| Carillas | Diseño de sonrisa"). Es una práctica que las normas de Google Business Profile prohíben. Nosotros **no la recomendaremos**. Sí confirma que el contenido de la ficha pesa.

**H3 (variación), preliminar:**
- **Entre IAs:** en 7 de 10 preguntas hay **una clínica "líder" que nombran las 3 superficies**: Smiles Peru (Q01), Top Smile (Q10), Cuidamedic (Q16), Medi Esthetic (Q22), Clínica Lima Derma (Q24), Clínica de la Piel (Q29) y Cderma (Q30). Fuera de esa líder, la mayoría de las clínicas aparece en **una sola** superficie. En Q05 y Q19, ChatGPT no coincide con ninguna de las otras dos.
- **Entre repeticiones:** hay un solo dato (ChatGPT Q22): de 5 clínicas, solo 1 se repite. Eso apunta a mucha variación, pero la estabilidad se mide en la prueba completa.

**H4 (brecha Maps vs IA), indicio:** las IAs no ordenan solo por ★. Gemini puso primera en Q24 a una clínica con 3.4★ y en Q19 a otra con 3.8★. La lista de 40 clínicas (semana 1) medirá la brecha.

**Otros datos:**
- El **Modo IA de Google** respondió siempre. Si hubo AI Overview en la búsqueda normal no quedó registrado de forma sistemática.
- **Gemini y Google** usan casi los mismos datos (fichas de Maps). **ChatGPT** es la superficie más distinta.
- Perplexity (Q01) nombró clínicas: Dr. Teixeira y Odontologists.

### Las 30 preguntas
Aprobadas por el Director el 25/09/2026, sin cambios. Redactadas como lo haría un paciente. Mezclan 4 rubros, 3 distritos y 5 formas de preguntar: **M** = "mejor", **R** = pide recomendación, **C** = con criterio (precio, confianza, especialista), **P** = procedimiento concreto, **L** = Lima sin distrito.

| ID | Rubro | Distrito | Forma | Pregunta |
|---|---|---|---|---|
| Q01 | Implantología | Miraflores | M | ¿Cuál es la mejor clínica de implantes dentales en Miraflores? |
| Q02 | Implantología | San Isidro | R | Recomiéndame una clínica para hacerme implantes dentales en San Isidro |
| Q03 | Implantología | Surco | C | ¿Dónde me pongo implantes dentales en Surco a buen precio y con garantía? |
| Q04 | Implantología | Miraflores | P | Necesito un implante dental de un solo diente, ¿qué clínica en Miraflores me recomiendas? |
| Q05 | Implantología | Lima | L | ¿Cuáles son las clínicas dentales más confiables en Lima para implantes? |
| Q06 | Implantología | San Isidro | P | ¿Qué clínica hace all-on-4 o implantes de arcada completa en San Isidro? |
| Q07 | Implantología | Surco | C | ¿Qué implantólogo tiene buenas reseñas en Surco? |
| Q08 | Implantología | Lima | C | ¿Cuánto cuesta un implante dental en Lima y dónde lo hacen bien? |
| Q09 | Estética dental | Miraflores | M | ¿Cuál es la mejor clínica de estética dental en Miraflores? |
| Q10 | Estética dental | San Isidro | P | ¿Dónde me hago carillas dentales en San Isidro? |
| Q11 | Estética dental | Surco | P | Recomiéndame un lugar para ortodoncia invisible (Invisalign) en Surco |
| Q12 | Estética dental | Lima | C | ¿Qué clínica dental en Lima tiene los mejores resultados en diseño de sonrisa? |
| Q13 | Estética dental | Miraflores | R | Quiero blanquearme los dientes en Miraflores, ¿a qué clínica voy? |
| Q14 | Estética dental | San Isidro | C | ¿Cuál es la clínica de ortodoncia más recomendada en San Isidro? |
| Q15 | Estética dental | Surco | M | ¿Cuál es el mejor dentista estético en Surco? |
| Q16 | Medicina estética | Miraflores | M | ¿Cuál es la mejor clínica estética en Miraflores? |
| Q17 | Medicina estética | San Isidro | P | ¿Dónde me pongo bótox en San Isidro con un médico confiable? |
| Q18 | Medicina estética | Surco | P | Recomiéndame una clínica para ácido hialurónico o rellenos en Surco |
| Q19 | Medicina estética | Lima | C | ¿Qué clínicas de medicina estética en Lima son seguras y tienen buenas reseñas? |
| Q20 | Medicina estética | Miraflores | P | ¿Dónde hacen depilación láser de buena calidad en Miraflores? |
| Q21 | Medicina estética | San Isidro | R | Quiero un tratamiento facial antiedad en San Isidro, ¿qué clínica me recomiendas? |
| Q22 | Medicina estética | Surco | C | ¿Qué clínica estética en Surco tiene buenos precios? |
| Q23 | Medicina estética | Lima | P | ¿Dónde se hace una buena lipoescultura o lipo sin cirugía en Lima? |
| Q24 | Dermatología | Miraflores | M | ¿Cuál es el mejor dermatólogo en Miraflores? |
| Q25 | Dermatología | San Isidro | P | Recomiéndame una clínica dermatológica en San Isidro para tratar el acné |
| Q26 | Dermatología | Surco | P | ¿Dónde tratan manchas en la piel o melasma en Surco? |
| Q27 | Dermatología | Lima | C | ¿Qué dermatólogo en Lima es bueno y atiende particular? |
| Q28 | Dermatología | Miraflores | P | ¿Dónde me hago un peeling químico con dermatólogo en Miraflores? |
| Q29 | Dermatología | San Isidro | C | ¿Cuál es la clínica dermatológica mejor valorada en San Isidro? |
| Q30 | Dermatología | Surco | R | Necesito un dermatólogo para caída de cabello en Surco, ¿a quién voy? |

Reparto: 8 de implantología, 7 de estética dental, 8 de medicina estética y 7 de dermatología. Por distrito: 8 de Miraflores, 8 de San Isidro, 8 de Surco y 6 de Lima general.

### Qué se mide
| Métrica | Cómo | Para qué hipótesis |
|---|---|---|
| % de respuestas con ≥ 1 clínica nombrada | Conteo por respuesta | H1 |
| Top de dominios citados (Doctoralia, webs, directorios…) | Frecuencia de fuentes | H2 |
| Estabilidad: % de clínicas que se repiten en las 3 repeticiones | Intersección por pregunta e IA | H3 |
| Coincidencia entre IAs | Clínicas compartidas por 2, 3 o 4 superficies | H3 |
| % de respuestas con búsqueda web y % sin fuentes visibles | Columnas `busco_web` y `fuentes_citadas` | H2 |
| Frecuencia de AI Overview en Google para preguntas locales | Notas "sin AI Overview" | H2, H8 |
| Brecha Maps vs IA | Cruzar con la lista de 40 clínicas (★ y n.º de reseñas) | H4 |

## Competencia y alternativas
Detalle y fuentes en el acta (§4). Resumen:

| Alternativa | Qué hace bien | Qué hace mal (para nuestro nicho) | Precio | Nuestra diferencia |
|---|---|---|---|---|
| **CreceRank** | Visibilidad en IA para marcas, en español, con presencia en Perú | Se enfoca en marcas, no en negocios locales por distrito. Solo mide, no ejecuta arreglos locales | US$29/mes (10 prompts), US$79 | Local por rubro y distrito, con arreglos concretos (Bing Places, Doctoralia, schema) |
| **BrightLocal** | SEO local maduro, ya mide IA | Solo EE. UU. y en inglés | US$39/mes por local | Latam, en español, con reporte por WhatsApp |
| **Local AI Audit** | Auditoría única y clara | Pago único, sin monitoreo, EE. UU. | US$297 | Monitoreo mensual + setup |
| **Otterly, Peec AI, Semrush, Profound, Yext, AthenaHQ** | Potentes y con API | Pensadas para marcas grandes y agencias en inglés, caras para una clínica | US$29–99+/mes o enterprise | Precio y lenguaje de clínica local |
| **Doctoralia / TopDoctors** | Probable fuente dominante que citan las IAs en salud | No miden la IA ni cubren el resto de fuentes | Suscripción de perfil | Doctoralia es una palanca que recomendamos, no un rival directo |
| **No hacer nada / agencia de SEO clásico** | Sin costo extra | No saben qué dice la IA | — | El informe gratis muestra la brecha con datos |

## Mercado (SaaS)
Estimaciones **a validar**. No hay censos confiables por rubro y distrito. La lista de 40 clínicas (semana 1) servirá para contar en Google Maps.

- **TAM (Latam):** negocios locales de ticket alto en ciudades grandes: salud electiva, estética, abogados, colegios. Decenas de miles. Solo sirve como visión.
- **SAM (Lima, 4 rubros de salud electiva):** supuesto de ~1,500–3,000 clínicas y consultorios con web o redes activas. **Validar** contando en Google Maps.
- **SOM (6 meses, Lima Top):** 20–30 clínicas directas + 3–5 agencias. Con 25 clínicas × S/ 349 ≈ **S/ 8,700/mes (≈ US$2,300)**, más setups.
- **Señales de demanda:** ninguna todavía. La primera señal real será la tasa de respuesta a los informes gratis (H5) y las preventas (H6).

## Riesgos detectados
| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Las IAs no nombran clínicas o dan respuestas genéricas en Lima (H1 falla) | Media | Alto | La prueba de fuentes lo detecta antes de construir más. Si falla: pivotear de rubro (abogados, colegios) o de ciudad |
| Medición imprecisa: la app difiere de la API, las respuestas son volátiles | Alta | Alto | Índice con muestreo repetido, variabilidad transparente y calibración manual contra las apps |
| Carga manual: 270 consultas ≈ 10 h y el monitoreo mensual no escala a mano | Alta | Medio | Plantilla + script de análisis. Pasar a API de pago solo cuando haya ingresos (con aprobación del Director) |
| Términos de uso de las IAs | Media | Alto | Consultas manuales, sin automatizar las apps de consumo. APIs oficiales cuando haya presupuesto |
| **Bloqueo de WhatsApp personal** por mensajes en frío | Media | Alto | Mensajes uno por uno y pocos por día. Priorizar Instagram DM y correo para el primer contacto; WhatsApp cuando la clínica responde |
| Cancelaciones por falta de atribución | Media | Alto | Intake "¿Cómo nos conociste? → IA", UTMs y cupones exclusivos (acta §5) |
| Dependencia de plataformas (Meta, Doctoralia, cambios en las IAs) | Media | Medio | No depender de una sola fuente. Medir las 3 IAs |
| CreceRank u otro baja al segmento local | Media | Medio | Velocidad, nicho de salud en Lima y relación directa con las clínicas |
| Datos personales (Ley 29733) | Baja | Medio | Solo datos públicos de negocios. Revisar en la fase 2 el tratamiento de los datos de contacto de dueños y pacientes |

## ✅ Conclusión y puerta de aprobación
- **¿Vale la pena seguir?** Propuesta: **✅ sí, seguir** _(pendiente de aprobación del Director)_
- **Porque:** H1 se cumple con holgura (30/30 en las 3 superficies completas, 31/40 aun contando Perplexity como fallo). Las fuentes son accionables (ficha de Google, Doctoralia, web, redes) y la variación entre IAs justifica medir con muestreo repetido.
- **Ajustes que salen de la muestra (a confirmar):**
  1. Reformular H2: la ficha de Google Maps es la fuente principal. La diferencia frente al SEO local clásico está en **medir qué dice cada IA** y en optimizar la ficha, Doctoralia y la web **para la IA**, no en evitar Google.
  2. Perplexity queda fuera de la prueba completa (3 superficies × 30 × 3 = **270 consultas**, ~9–10 h) y Google se mantiene.
  3. Registrar en la prueba completa si aparece AI Overview antes de pasar al Modo IA.
- **Aprobado por el Director el:** _(pendiente)_
