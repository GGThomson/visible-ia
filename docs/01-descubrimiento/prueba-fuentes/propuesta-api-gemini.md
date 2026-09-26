# 🧪 Propuesta: prueba con la API de Gemini antes de las 270 consultas manuales
<!-- Pedida por el Director el 26/09/2026. Estado: PROPUESTA, pendiente de aprobación. No se ejecuta nada ni se gasta nada sin su "sí". -->

## Objetivo
Saber si la **API gratuita de Gemini** (con búsqueda en Google Search y en Google Maps) da respuestas **parecidas** a las de la app que el Director registró en la muestra del 26/09. Si se parecen, las repeticiones de Gemini de la prueba completa (90 de las 270 consultas) se automatizan con un script. Esa medición automática puede ser la base del producto.

## Qué dice la documentación oficial (consultada el 26/09/2026)
| Tema | Dato | Fuente |
|---|---|---|
| Nivel gratuito | Hay acceso limitado a modelos Flash y Flash-Lite (Gemini 3.x) **sin tarjeta** | [Precios de la API de Gemini](https://ai.google.dev/gemini-api/docs/pricing) |
| Búsqueda en Google (grounding) | ⚠️ **Corregido el 26/09:** con Gemini 3.x, en el nivel gratuito figura como **"Not available"**; las 5,000 gratis al mes son del nivel **de pago**. Con **Gemini 2.5 Flash / Flash-Lite**, en cambio, el nivel gratuito la incluye: *"Free of charge, up to 500 RPD"* | [Precios](https://ai.google.dev/gemini-api/docs/pricing) |
| Búsqueda en Google Maps (grounding) | Igual que Search: con 3.x no está en el nivel gratuito. **Gemini 2.5 Flash:** 500 consultas al día gratis. Se le pasa una ubicación (latitud y longitud) | [Precios](https://ai.google.dev/gemini-api/docs/pricing) · [Grounding with Google Maps](https://ai.google.dev/gemini-api/docs/maps-grounding) |
| Combinar Maps + Search | Se puede desde Gemini 3.5 Flash en adelante | [Grounding with Google Maps](https://ai.google.dev/gemini-api/docs/maps-grounding) |
| ⚠️ **Idioma de Maps** | *"Grounding with Google Maps currently only supports English language prompts and responses."* | [Grounding with Google Maps](https://ai.google.dev/gemini-api/docs/maps-grounding) |
| ⚠️ Privacidad del nivel gratuito | Google puede usar lo que enviamos para mejorar sus productos. No es problema aquí: solo enviamos las preguntas públicas de un paciente, sin datos de clínicas ni de personas | [Precios](https://ai.google.dev/gemini-api/docs/pricing) |
| ⚠️ Atribución | Si mostramos resultados de Maps a terceros (por ejemplo, en un informe), hay que citar "Google Maps" con el nombre y el enlace de cada fuente | [Grounding with Google Maps](https://ai.google.dev/gemini-api/docs/maps-grounding) |

## Diseño de la prueba
- **Preguntas:** las mismas 10 de la muestra (Q01, Q05, Q10, Q11, Q16, Q19, Q22, Q24, Q29, Q30), **en español** y sin cambios.
- **Configuraciones (3):**
  | Config. | Herramientas | Para qué |
  |---|---|---|
  | **A** | Google Search | La más simple. Es la que más debería parecerse a Google Modo IA |
  | **B** | Google Search + Google Maps, con la ubicación de Lima (Miraflores: −12.1211, −77.0297) | Es la más parecida a la app de Gemini, que mostró fichas de Maps en 10 de 10 respuestas. **Riesgo:** Maps dice aceptar solo inglés. La prueba nos dirá si con preguntas en español falla, lo ignora o funciona |
  | **B-en** (solo si B falla por idioma) | Igual que B, con las preguntas traducidas al inglés y pidiendo "answer in Spanish" | Ver si el idioma es el único problema. Se compara con cautela porque ya no es la misma pregunta del paciente |
- **Repeticiones:** 3 por pregunta y configuración. Son **60 llamadas** (90 si hace falta B-en), lejos del límite gratuito de 5,000 al mes.
- **Modelo:** el Flash gratuito más reciente que admita Maps + Search. Al ejecutar resultó ser **Gemini 2.5 Flash**, porque con 3.x el grounding da error 429 en el nivel gratuito. La versión exacta se anota en el registro.
- **Registro:** un CSV nuevo `registro-api.csv` con las mismas columnas que `registro.csv`, más `modelo`, `config` y la lista de fuentes (Search y Maps) que devuelve la API.

## Cómo se compara con la muestra
Por cada pregunta se compara la respuesta de la API (las 3 repeticiones juntas) con la de la **app de Gemini** y, como referencia, con la de **Google Modo IA**:
1. **Nombra clínicas:** ¿la API nombra ≥ 1 clínica, como la app?
2. **Coincidencia:** ¿qué parte de las clínicas que dio la app aparece también en la API?
3. **Líder:** ¿aparece la clínica "líder" de la pregunta, la que nombraron las 3 superficies (Smiles Peru, Top Smile, Cuidamedic…)?
4. **Fuentes:** ¿la API se apoya en fichas de Maps, Doctoralia, webs y redes, como la app?

**Regla propuesta para decir "se parecen" y automatizar:**
- ✅ **Automatizar Gemini** si se cumplen las tres:
  - la API nombra clínicas en ≥ 9 de 10 preguntas;
  - en ≥ 7 de 10 preguntas comparte ≥ 1 clínica con la app;
  - aparece la líder en ≥ 5 de las 7 preguntas que la tienen.
- ⚠️ **Parecido parcial:** las repeticiones se automatizan, pero siempre con una calibración manual (1 consulta en la app por cada 10 de la API), y se informa como "Gemini (API)".
- ❌ **No se parecen:** las 270 consultas siguen siendo manuales, como está planeado.

Aunque se parezcan, la API **no reemplaza** a ChatGPT ni a Google Modo IA: esas 180 consultas siguen siendo manuales. Si la configuración A se parece mucho a Google Modo IA, se evalúa aparte usarla también para esa superficie.

## Qué necesita el Director (sin costo)
1. Crear una **clave de API en Google AI Studio** (aistudio.google.com) con su cuenta de Google, **sin activar la facturación**. Sin facturación, la API no puede cobrar: al pasar el límite gratuito devuelve un error, no un cargo.
2. Guardar la clave en un archivo `.env` en la raíz del proyecto (`GEMINI_API_KEY=...`). `.env` ya está en `.gitignore`, así que nunca se sube a GitHub. **No pegar la clave en el chat.**

## Qué hace Claude Code
1. Escribir un script corto en Python (`scripts/prueba_api_gemini.py`) con el SDK oficial `google-genai`, que lea las 10 preguntas, llame a la API y guarde `registro-api.csv`.
2. Ejecutarlo: son 60 llamadas, unos minutos.
3. Comparar con la muestra y escribir los resultados en `investigacion.md`, con una recomendación según la regla de arriba.

**Esfuerzo estimado:** ~2 h, en la semana 1 (28/09), antes de empezar las consultas manuales de Gemini.
**Costo:** US$0. Si en algún momento algo pudiera costar, se detiene y se pregunta.

## Riesgos
| Riesgo | Mitigación |
|---|---|
| Maps no funciona en español | Es justamente lo que mide la config. B. Si falla, se usa B-en y se compara con cautela, o solo la config. A |
| La API difiere mucho de la app (según Surfer, solo coinciden ~24 %) | Es lo que mide esta prueba. Si difieren, seguimos a mano, como ya estaba planeado |
| Los términos de uso de Maps y Search limitan guardar resultados o mostrarlos en informes | Antes de usar la API en el **producto**, revisar los términos de grounding. Esta prueba es interna y no muestra resultados a terceros |
| Los límites del nivel gratuito cambian | Se revisa la página de precios el día de la prueba. Sin facturación activa no hay cargos posibles |

## Resultados parciales (26/09) · 19 de 60 llamadas
Datos: [registro-api.csv](registro-api.csv) y [registro-api-crudo.jsonl](registro-api-crudo.jsonl). Comparación: `scripts/comparar_api_vs_muestra.py`.

**Qué pasó al ejecutar:**
- Con **Gemini 3.x** el grounding da error 429 en el nivel gratuito, así que se usó **Gemini 2.5 Flash** (US$0).
- El nivel gratuito de 2.5 Flash tiene un tope de **20 llamadas al día por modelo** (así lo dice el error de la API). La corrida se detuvo sola en la llamada 19, sin costo.
- Se completaron: **config. A (solo Search), Q01–Q19 × 3 repeticiones y Q22 × 1**. Faltan Q22–Q30 de A y **toda la config. B (Search + Maps)**.
- En una llamada de diagnóstico, **Maps sí respondió en español**, pese a la advertencia de la documentación. Devolvió fichas con ★ y n.º de reseñas, como la app.

**Comparación (config. A, 7 preguntas):**
| Criterio de la regla | Resultado parcial | Meta (sobre 10) |
|---|---|---|
| Nombra ≥ 1 clínica | **7 de 7** preguntas (19 de 19 respuestas) | ≥ 9 |
| Comparte ≥ 1 clínica con la app de Gemini | **5 de 7** (Q01, Q05, Q16, Q19, Q22). En Q10 y Q11: 0 | ≥ 7 |
| Aparece la clínica líder | **3 de 4** (Smiles Peru, Cuidamedic, Medi Esthetic sí; Top Smile no) | ≥ 5 de 7 |

**Lo que se ve:**
- **Coincidencia desigual:** en Q16 la API y la app coinciden en 3 de 4 clínicas; en Q10 (carillas en San Isidro) no coinciden en ninguna.
- **Fuentes distintas de la app:** la config. A cita **webs**, no fichas de Maps. Las más frecuentes: Doctoralia (en 7 de 19 respuestas), webs propias (smilesperu, dentalperezyance, draviolemunoz, cuidamedic…), directorios (fresha, whatclinic) y prensa (elcomercio). La app se apoyaba en fichas de Maps, así que la **config. B** es la que debería parecerse más a la app.
- **La API es más estable que la app:** cerca de la mitad de las clínicas se repite en las 3 repeticiones, y en Q16 las 5 son idénticas. En la app de ChatGPT (Q22) solo se repitió 1 de 5.

**Conclusión provisional:** con la config. A el parecido es **parcial**. No alcanza para decidir. Falta la config. B, que es la clave.

**Implicación para el producto:** 20 llamadas al día gratis no alcanzan para monitorear clínicas con la API. Sirven para la prueba completa: las 90 repeticiones de Gemini tomarían ~5 días corriendo solas. El monitoreo mensual necesitará el nivel de pago cuando haya ingresos (con aprobación del Director).

**Cambio de plan (Director, 26/09):**
- **No se retoman las 41 llamadas.** Solo se hace la **config. B con 1 repetición (10 llamadas)**. Como el riesgo C-001 (términos de grounding) afecta al motor, esta prueba queda como **informativa y de baja prioridad**.
- **Avance:** B Q01 hecha (4 lugares de Maps). Faltan 9 llamadas: `python scripts/prueba_api_gemini.py --configs B --reps 1`.

## ✅ Aprobación
- [x] El Director aprueba la prueba y crea la clave sin facturación (fecha: 2026-09-26)
