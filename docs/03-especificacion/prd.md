# 📋 Especificación del producto — PRD (Fase 3)
<!-- La fuente de verdad de QUÉ se construye. Claude Code construye desde aquí. Si algo no está aquí, no se construye (va a /cambio). -->
<!-- Base: brief, investigacion.md (fase 1), estrategia.md (fase 2), ADR-001 y ADR-002. El CÓMO (stack, modelos, base de datos) se decide en la fase 4. -->

**Versión:** v1 · **Estado:** borrador · **Fecha:** 2026-09-26

## 1. Resumen
- **Qué es:** visible-ia mide cada mes si **ChatGPT** y **Google (Modo IA)** recomiendan a una clínica cuando un paciente pregunta por su rubro y distrito en Lima. La compara con sus competidores y le da un checklist de arreglos. Gemini se mide con una muestra manual, como calibración (ADR-002).
- **Para quién:**
  - Clínicas de implantología, estética dental, medicina estética y dermatología en Miraflores, San Isidro y Surco.
  - Agencias de marketing, que lo revenden con su marca.
- **Unidad de medida: el mercado** = rubro + distrito (p. ej., "implantología · Miraflores"). Cada mercado tiene un **banco de 10 preguntas** y una **lista de clínicas** (el cliente y sus competidores).
- ✅ **Entregas escalonadas** (aprobadas por el Director el 26/09; el calendario sale de la estrategia):
  | Entrega | Semanas | Para qué | Módulos |
  |---|---|---|---|
  | **v1.0 "Vender"** | 1–2 | Generar el **informe gratis** que abre la venta desde el 05/10 | Mercados y clínicas, motor, extractor, puntaje, informe PDF de diagnóstico, landing |
  | **v1.1 "Servir"** | 3–4 | Atender a los primeros clientes cada mes | Cuentas, panel web, reporte mensual, recomendaciones |
  | **v1.2 "Escalar"** | 5–6 | Automatizar y abrir el canal de agencias | WhatsApp, pagos recurrentes, marca blanca completa |

## 2. Usuarios y roles
| Rol | Qué puede hacer |
|---|---|
| **Operador** (Director) | Todo: crear mercados, preguntas y clínicas; lanzar corridas; cargar la muestra manual de Gemini; revisar y corregir lo extraído; generar informes; gestionar clientes, agencias y cobros |
| **Clínica** (cliente) | Ver el panel de **sus** sedes: índice, evolución, competidores, fuentes y checklist. Marcar tareas como hechas. Recibir los reportes por WhatsApp o correo |
| **Agencia** (cliente, marca blanca) | Lo mismo que una clínica, pero para **todas las sedes de sus clientes**. Poner su logo y colores en los informes. No ve a los clientes de otras agencias |
| **Prospecto** (sin cuenta) | Recibe el informe gratis en PDF. Puede dejar sus datos en la landing |

## 3. Historias de usuario
<!-- Prioridad MoSCoW. "Entrega" indica en qué versión entra. -->
| ID | Historia | Prioridad | Entrega |
|---|---|---|---|
| **Mercados, preguntas y clínicas** | | | |
| HU-01 | Como operador quiero crear un **mercado** (rubro + distrito) con su banco de **10 preguntas** para medir siempre lo mismo cada mes | Must | v1.0 |
| HU-02 | Como operador quiero **cargar la lista de clínicas** de un mercado (nombre, dirección, ★, n.º de reseñas, web, Instagram, enlace de la ficha de Google) desde un CSV para tener a los competidores | Must | v1.0 |
| HU-03 | Como operador quiero registrar los **alias** de cada clínica (p. ej., "Perez Yance" = "Americadent") para que una clínica no se cuente como dos | Must | v1.0 |
| **Motor de consultas** | | | |
| HU-04 | Como operador quiero **lanzar una corrida** de un mercado (10 preguntas × 3 repeticiones × 2 superficies: ChatGPT por API y Google Modo IA por SerpApi) y guardar cada respuesta completa con sus fuentes | Must | v1.0 |
| HU-05 | Como operador quiero que el motor **se detenga y me avise** si una corrida superaría el presupuesto o la cuota gratuita, para no gastar sin aprobación | Must | v1.0 |
| HU-06 | Como operador quiero **cargar a mano la muestra de Gemini** (y de la app de ChatGPT) pegando la respuesta, para calibrar la API contra la app | Must | v1.0 |
| **Extractor** | | | |
| HU-07 | Como operador quiero que cada respuesta se convierta en la **lista ordenada de clínicas mencionadas** (asociadas a la lista del mercado cuando existan) y de los **dominios citados** | Must | v1.0 |
| HU-08 | Como operador quiero **revisar y corregir** lo extraído (unir, separar o descartar menciones) antes de publicar un informe | Must | v1.0 |
| HU-09 | Como operador quiero ver las **clínicas nuevas** (mencionadas pero fuera de la lista) para sumarlas al mercado | Should | v1.0 |
| **Puntaje de presencia** | | | |
| HU-10 | Como operador quiero el **índice de presencia** de cada clínica por superficie y combinado, con su **margen de variación**, según la §5 | Must | v1.0 |
| HU-11 | Como clínica quiero ver mi **posición frente a mis competidores** del mismo mercado (ranking por índice) | Must | v1.0 |
| HU-12 | Como clínica quiero saber **qué fuentes** usa la IA en mi mercado (Google, Doctoralia, webs, redes) para saber dónde trabajar | Must | v1.0 |
| HU-13 | Como clínica quiero ver la **brecha Maps vs IA** (mis ★ y reseñas frente a mi presencia en la IA) para entender el problema | Should | v1.0 |
| **Informes** | | | |
| HU-14 | Como operador quiero generar el **informe gratis de diagnóstico** en PDF para un prospecto ("así te ve la IA frente a tus 3 competidores") en ≤ 10 minutos de trabajo manual | Must | v1.0 |
| HU-15 | Como clínica quiero recibir un **reporte mensual** con la evolución de mi índice, los cambios frente a los competidores y las tareas sugeridas | Must | v1.1 |
| HU-16 | Como agencia quiero que los informes salgan **con mi logo y mis colores** y sin la marca visible-ia | Must | v1.2 (PDF con logo manual desde v1.0 si una agencia lo pide) |
| **Recomendaciones** | | | |
| HU-17 | Como clínica quiero un **checklist priorizado** (ficha de Google → Doctoralia → web con schema → redes → Bing Places) según lo que falta en mi caso | Must | v1.1 |
| HU-18 | Como clínica quiero que me **generen el schema JSON-LD** de mi clínica para pegarlo en mi web | Should | v1.1 |
| **Panel web y cuentas** | | | |
| HU-19 | Como clínica o agencia quiero **entrar a un panel** con correo y contraseña (o enlace mágico) y ver solo lo mío | Must | v1.1 |
| HU-20 | Como clínica quiero ver la **evolución** de mi índice mes a mes y marcar las tareas del checklist como hechas | Must | v1.1 |
| HU-21 | Como agencia quiero ver **todas las sedes de mis clientes** en una sola vista | Must | v1.2 |
| **WhatsApp** | | | |
| HU-22 | Como clínica quiero recibir el **reporte mensual y alertas** (p. ej., "un competidor te pasó en ChatGPT") por WhatsApp | Should | v1.2 |
| **Pagos y atribución** | | | |
| HU-23 | Como operador quiero **registrar los pagos manuales** (link de pago, Yape o transferencia) y ver qué clientes están al día | Must | v1.1 |
| HU-24 | Como clínica quiero pagar con una **suscripción automática** con tarjeta | Could | v1.2 |
| HU-25 | Como clínica quiero un **kit de atribución** (pregunta de intake "¿Cómo nos conociste? → IA", UTMs, cupón) para ver pacientes que llegan por la IA | Should | v1.1 |
| **Landing** | | | |
| HU-26 | Como prospecto quiero una **landing** que explique el servicio y me deje **pedir mi informe gratis** | Must | v1.0 |
| HU-27 | Como prospecto quiero ver el **ranking gratis por rubro y distrito** (solo el top, sin detalle) como gancho | Could | v1.2 |

## 4. Criterios de aceptación
<!-- Formato Dado/Cuando/Entonces: se convierten en pruebas. Solo las historias Must de v1.0 están detalladas aquí; las de v1.1 y v1.2 se detallan al planificarlas, sin cambiar su alcance. -->
### HU-01 · Mercado y preguntas
- **Dado** un rubro y un distrito, **cuando** creo el mercado, **entonces** se genera su banco de 10 preguntas a partir de las plantillas del rubro (§5.1), y puedo editarlas antes de la primera corrida.
- **Dado** un mercado con corridas hechas, **cuando** edito una pregunta, **entonces** se crea una **nueva versión** del banco. El histórico queda asociado a la versión con la que se midió.

### HU-02 / HU-03 · Clínicas y alias
- **Dado** un CSV con las columnas mínimas (nombre, distrito, enlace de la ficha), **cuando** lo importo, **entonces** se crean las clínicas y se me muestran las filas con errores sin detener la importación.
- **Dado** una clínica con alias, **cuando** una respuesta menciona cualquiera de ellos, **entonces** se cuenta como una sola clínica.

### HU-04 / HU-05 · Corrida
- **Dado** un mercado, **cuando** lanzo una corrida, **entonces** se hacen 10 × 3 llamadas por superficie. Cada respuesta se guarda con: fecha y hora, superficie, modelo o proveedor, pregunta y versión del banco, n.º de repetición, texto completo, fuentes (dominio y URL) y el costo estimado.
- **Dado** que una llamada falla, **cuando** termina la corrida, **entonces** la corrida queda como **incompleta**, con la lista de lo que falló, y se puede **reanudar** sin repetir lo que ya se hizo.
- **Dado** un presupuesto mensual configurado (por defecto, **US$10**) o la cuota gratuita de SerpApi, **cuando** una corrida lo superaría, **entonces** no se ejecuta y se me explica cuánto costaría.
- **Dado** ChatGPT por API, **cuando** consulta, **entonces** usa búsqueda web con la ubicación aproximada de Lima (Perú).

### HU-06 · Muestra manual
- **Dado** un mercado y una pregunta, **cuando** pego una respuesta de la app de Gemini o de ChatGPT, **entonces** se guarda marcada como **"manual / app"**, pasa por el mismo extractor y **no entra al índice**: solo a la calibración (§5.4).

### HU-07 / HU-08 · Extractor y revisión
- **Dado** una respuesta, **cuando** se procesa, **entonces** obtengo las clínicas mencionadas **en el orden en que aparecen**, cada una asociada a una clínica del mercado (o marcada como "nueva") y los dominios citados.
- **Dado** el conjunto de evaluación (§5.3), **cuando** corro el extractor, **entonces** cumple las metas de calidad de la §5.3; si no, la versión no se publica.
- **Dado** una corrida extraída, **cuando** la reviso, **entonces** puedo corregir cualquier mención, y el índice se recalcula con la corrección.

### HU-10 / HU-11 / HU-12 · Puntaje
- **Dado** una corrida completa y revisada, **cuando** calculo el puntaje, **entonces** cada clínica del mercado tiene su índice por superficie y combinado, con el intervalo de la §5.2, su posición media y su cuota de menciones. El ranking del mercado se ordena por índice combinado.
- **Dado** el mercado, **cuando** veo las fuentes, **entonces** aparece el top de dominios citados, agrupados por tipo: ficha de Google, Doctoralia, web propia, redes, directorios o rankings y prensa.

### HU-14 · Informe gratis
- **Dado** un prospecto (una clínica del mercado) y una corrida revisada, **cuando** genero el informe, **entonces** obtengo un PDF en español de ≤ 4 páginas con:
  1. su índice frente a sus 3 competidores principales;
  2. ejemplos reales de lo que respondió cada IA (citados, con fecha);
  3. las fuentes que usa la IA en su mercado;
  4. su brecha Maps vs IA;
  5. 3 recomendaciones;
  6. una nota de método: qué se midió, cuántas veces, la variabilidad y que no es un "puesto #1" garantizado.
- **Dado** el informe, **cuando** lo reviso, **entonces** no contiene datos de pacientes ni afirmaciones sin fuente.

### HU-26 · Landing
- **Dado** un visitante, **cuando** deja nombre, clínica, distrito, rubro y un contacto, **entonces** queda registrado como prospecto con la **fuente** (UTM) y el **consentimiento** de contacto, y el operador recibe un aviso.

## 5. Índice de presencia: definición y evaluación (núcleo de datos)
### 5.1 Qué se pregunta
- ✅ **10 plantillas por rubro, con el distrito como variable** (decidido por el Director el 26/09) → [plantillas-preguntas.md](plantillas-preguntas.md).
  - Las 30 preguntas aprobadas el 25/09 se convierten en plantillas y se completan hasta 10 por rubro.
  - Las de "Lima general" pasan a preguntar por el distrito.
  - Todos los distritos de un rubro usan las mismas preguntas, así los mercados son comparables.
- **Por mercado y mes:** 10 preguntas × 3 repeticiones × 2 superficies (ChatGPT API y Google Modo IA) = **60 respuestas**.

### 5.2 Cómo se calcula
- **Aparición:** una clínica "aparece" en una respuesta si se la nombra al menos una vez, después de resolver los alias.
- ✅ **Índice de presencia por superficie** = % de las respuestas de esa superficie en las que aparece la clínica (0–100), con 30 respuestas por superficie. Es un % simple, sin ponderar por posición (decidido por el Director el 26/09): es fácil de explicar a un dueño de clínica.
- **Índice combinado** = promedio de los índices de las superficies medidas (ChatGPT y Google), con el mismo peso.
- **Margen de variación:** intervalo de confianza del 95 % (Wilson) sobre la proporción. Se muestra siempre junto al índice.
- **Cambio "real" entre meses:** solo se informa como subida o bajada si los intervalos de los dos meses no se solapan. Si se solapan, se dice "sin cambio claro".
- **Métricas secundarias:**
  - **Posición media**, cuando aparece (1 = la primera nombrada).
  - **Cuota de menciones:** apariciones de la clínica / apariciones de todas las clínicas del mercado.
  - **Top de fuentes** del mercado.
- **Gemini y la app de ChatGPT (manual):** no entran al índice. Se informan aparte como "muestra de calibración".

### 5.3 Calidad del extractor
- **Conjunto de evaluación:** ≥ **60 respuestas etiquetadas a mano**, empezando por las 31 de la muestra del 26/09 y las 20 de la API de Gemini, más respuestas de las primeras corridas. Cubre los 4 rubros.
- **Metas:**
  - Clínicas: **precisión ≥ 95 %** (lo que marca como clínica lo es) y **exhaustividad ≥ 90 %** (encuentra las que están).
  - Asociación correcta con la clínica del mercado ≥ 95 %.
  - Dominios de las fuentes: ≥ 95 %.
- **Cuándo se evalúa:** en cada cambio del extractor (prueba automática) y una vez al mes sobre 10 respuestas nuevas etiquetadas.

### 5.4 Calibración API vs app
- **Cada mes, por mercado activo:** 1 respuesta manual por pregunta en la app de ChatGPT y 1 en la de Gemini (unos 20 minutos).
- **Qué se informa:**
  - % de clínicas de la app que también aparecen en la API.
  - Si la clínica "líder" coincide.
- **Umbral de alerta:** si en ChatGPT la coincidencia baja de **50 %** dos meses seguidos, el informe lo advierte y se revisa el método.

## 6. Requisitos no funcionales
- **Rendimiento:**
  - Una corrida de un mercado (60 llamadas) termina en **≤ 20 minutos**.
  - El panel carga en **≤ 3 s** en 4G.
  - El PDF se genera en **≤ 1 minuto**.
- **Costo:**
  - Medir un mercado cuesta **≤ US$1 al mes** en APIs.
  - Todo lo demás, en planes gratuitos hasta el primer cliente.
  - Ningún gasto nuevo sin la aprobación del Director (brief).
- **Seguridad y privacidad:**
  - Las claves solo en `.env` o en el gestor de secretos del hosting, nunca en el repositorio.
  - Cada cliente y cada agencia ve **solo sus datos**, y se prueba de forma automática.
  - Contraseñas con hash; conexiones HTTPS.
  - **Retención (ADR-002):** texto de las respuestas 12 meses; métricas mientras el cliente esté activo más 12 meses; ningún dato de pacientes; nombres de profesionales solo como nombre del establecimiento.
  - Prospectos: se registra el origen y el consentimiento, y se respeta "no volver a contactar" (Ley 29733).
  - Registro de accesos del operador a los datos de clientes.
- **Respeto de términos:** solo APIs oficiales y proveedores SERP (ADR-002). **Nunca** automatizar las apps de consumo.
- **Accesibilidad:** contraste AA, textos legibles en el celular, gráficos con su valor en texto.
- **Idioma / zona horaria / moneda:** interfaz e informes en **español (Perú)**; zona **America/Lima**; montos en **soles (S/)**, con los costos de API en US$ solo para el operador.
- **Dispositivos / navegadores:**
  - Panel: primero celular, con las 2 últimas versiones de Chrome, Safari y Edge.
  - El PDF se lee bien en el celular (formato A4 vertical).
- **Confiabilidad:** si falla una corrida, no se pierde lo ya consultado (se reanuda). Copia de seguridad diaria de la base de datos.

## 6-bis. Integraciones externas
| Servicio | Para qué | Entrega | Nota |
|---|---|---|---|
| API de OpenAI (Responses + web search) | Medir ChatGPT | v1.0 | Activar la facturación **requiere la aprobación del Director** (≈ US$4/mes con 5 mercados) |
| SerpApi (Google AI Mode API) | Medir Google Modo IA | v1.0 | Plan gratis de 250 búsquedas/mes; pasar a pago o a DataForSEO con el primer ingreso |
| WhatsApp Business API | Reportes y alertas | v1.2 | Se paga con el primer cliente; los trámites se inician en la semana 1 |
| Culqi o Mercado Pago | Link de pago (v1.1) y suscripción (v1.2) | v1.1 | Comisión ≈ 4 % + IGV |

## 7. Fuera de alcance (explícito)
- Perplexity (ADR-001) y cualquier otra IA fuera de ChatGPT, Google Modo IA y la muestra manual de Gemini.
- Medir Gemini de forma automática (ADR-002).
- Automatizar o hacer scraping de las apps de consumo (ChatGPT, Gemini).
- Rubros o ciudades fuera de los 4 rubros y 3 distritos (más "Lima" en las plantillas).
- Editar la ficha de Google, Doctoralia o la web del cliente por él: solo checklist y schema generado.
- App móvil nativa, API pública para agencias, integración con CRMs.
- Pagos automáticos antes de la v1.2, y facturación electrónica automática (depende del RUC).
- Prometer o mostrar un "puesto #1" garantizado.

## 8. Preguntas abiertas
- ¿Los precios incluyen IGV? Depende del régimen que defina el contador (estrategia). No afecta la construcción de la v1.0.
- Tareas legales de la estrategia: términos de *web search* de OpenAI, créditos de SerpApi en Modo IA, Ley 29733.

## 9. Convenciones
- **Idioma del código y de los commits:** inglés (AGENTS.md). Documentación en español.
- **Idioma de la interfaz y de los informes:** español (Perú).

## ✅ Puerta de aprobación
- Aprobado y congelado por el Director el: _(pendiente)_
