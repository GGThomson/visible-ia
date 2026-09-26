# 🧪 Propuesta: prueba con la API de Gemini antes de las 270 consultas manuales
<!-- Pedida por el Director el 26/09/2026. Estado: PROPUESTA, pendiente de aprobación. No se ejecuta nada ni se gasta nada sin su "sí". -->

## Objetivo
Saber si la **API gratuita de Gemini** (con búsqueda en Google Search y en Google Maps) da respuestas **parecidas** a las de la app que el Director registró en la muestra del 26/09. Si se parecen, las repeticiones de Gemini de la prueba completa (90 de las 270 consultas) se automatizan con un script. Esa medición automática puede ser la base del producto.

## Qué dice la documentación oficial (consultada el 26/09/2026)
| Tema | Dato | Fuente |
|---|---|---|
| Nivel gratuito | Hay acceso limitado a modelos Flash y Flash-Lite (Gemini 3.x) **sin tarjeta** | [Precios de la API de Gemini](https://ai.google.dev/gemini-api/docs/pricing) |
| Búsqueda en Google (grounding) | **5,000 consultas gratis al mes** con los modelos Gemini 3.x (compartidas). Después cuesta US$14 por 1,000 | [Precios](https://ai.google.dev/gemini-api/docs/pricing) |
| Búsqueda en Google Maps (grounding) | **5,000 consultas gratis al mes** con Gemini 3.x. Después cuesta US$14 por 1,000. Se le pasa una ubicación (latitud y longitud) | [Precios](https://ai.google.dev/gemini-api/docs/pricing) · [Grounding with Google Maps](https://ai.google.dev/gemini-api/docs/maps-grounding) |
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
- **Modelo:** el Flash gratuito más reciente que admita Maps + Search (hoy, Gemini 3.x Flash). Se anota la versión exacta en el registro.
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

## ✅ Aprobación
- [ ] El Director aprueba la prueba y crea la clave sin facturación (fecha: ____ )
