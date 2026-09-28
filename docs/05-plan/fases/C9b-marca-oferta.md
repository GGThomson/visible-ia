# Fase C9b · Marca y oferta (antes de las llamadas del 05/10)

**Objetivo:** llegar a las primeras llamadas con la marca **Eminia** (ADR-005) aplicada en la landing, el panel y el informe, y con una oferta clara (planes, ganchos y guion). Sin funciones nuevas: solo aspecto, textos y documentos.
**Origen:** acta `memoria/actas/2026-09-28-marca-y-oferta.md` · cambio C-007
**Historias que cubre:** apoya HU-26 (landing) y la venta de la v1.1
**Estado:** 🟡 tareas ✅; falta que el Director apruebe la vista previa (y su foto) antes de publicar
**Nota:** no agrega dependencias. El repo, el paquete y la URL siguen como `visible-ia`; solo cambian los textos visibles.

## Tareas

### C9b-T01 · Documento de marca
- **Estado:** ✅ (`docs/marca/marca.md`)
- **Qué:**
  - Crear `docs/marca/marca.md` con: nombre, lema, colores, tipografías, reglas de uso del logo y el tono.
  - Tono: colega que sabe de marketing de clínicas; tuteo; siempre con número y rango; nunca «garantizamos el puesto #1»; sin «prompts», «LLM», «GEO»; ejemplos de Lima.
  - El ADR ya existe: ADR-005.
- **Criterios de aceptación:** [ ] coincide con el ADR-005 y con el acta.
- **Rama:** `feat/C9b-marca-y-oferta` (una rama para toda la fase; un commit por tarea)

### C9b-T02 · Logo, favicon y `marca.toml`
- **Estado:** ✅ (el SVG lleva ancho y alto para que el PDF lo muestre; una prueba verifica que el logo incrustado coincide con `web/marca/logo.svg`)
- **Qué:**
  - Guardar `web/marca/logo.svg` y `web/marca/simbolo.svg` (el SVG del anexo A del acta; el símbolo es sin `<text>` y con `viewBox="0 0 48 48"`).
  - Usar el símbolo como favicon de la landing y el panel.
  - En `src/visible_ia/informes/marca.toml`: `nombre`, `lema`, `color_primario` (#0F1B2D), `color_acento` (= «tu clínica», #2447C8), `color_suave` y `logo_url` como data URI del SVG, para que el PDF no dependa de internet.
- **Criterios de aceptación:** [ ] el PDF sale con el logo sin conexión.

### C9b-T03 · Colores y letras (tokens)
- **Estado:** ✅ (hoja común `web/marca/eminia.css`; en el informe, la competencia va en pizarra y el cobalto solo marca a la clínica; el diagnóstico de ejemplo bajó de 4 a 3 páginas)
- **Qué:**
  - Landing y panel: mantener Pico CSS, pero sobrescribir sus variables (`--pico-primary`, `--pico-primary-background`, `--pico-font-family`, fondos) con los colores del ADR-005.
  - Cargar Source Serif 4, IBM Plex Sans e IBM Plex Mono desde Google Fonts.
  - En `estilos.css` del informe, las mismas fuentes con respaldo a las actuales.
- **Criterios de aceptación:**
  - [ ] Contraste AA (4.5:1) en todo texto.
  - [ ] Un solo color (cobalto) para «tu clínica» y los botones.
- **Pruebas:** `tests/unit/test_informe_diagnostico.py` y `test_informe_mensual.py`; regenerar el PDF de ejemplo para que lo mire el Director.

### C9b-T04 · Landing nueva
- **Estado:** ✅ con una pendiente: la foto del Director (por ahora, un monograma «GR»). Dato de Osiptel verificado: **23 % en Lima Metropolitana** («casi 1 de cada 4»); «cerca de la mitad en el nivel A» no se pudo verificar y no se publica
- **Qué:** `web/index.html` con el mismo formulario y el mismo `app.js`, en este orden:
  1. Título «¿Qué clínica recomienda ChatGPT cuando un paciente pregunta por implantes en Miraflores?», un subtítulo y el botón «Mira cómo te ve la IA (gratis)».
  2. Tarjeta que imita un chat: la pregunta del paciente y una respuesta de ejemplo que nombra 3 clínicas y no a «tu clínica». Marcada como ejemplo.
  3. Franja de 3 datos con fuente enlazada: Osiptel ERESTEL 2025; BrightLocal, marzo 2026 (se dice que es EE. UU.); medición propia (30 de 30).
  4. Cómo funciona (los 3 pasos actuales).
  5. Así se ve tu informe (las barras actuales).
  6. Planes: «Diagnóstico gratis», «Plan Medir» y «Plan Gestionado» (este último marcado «más completo»), con «sin permanencia», precio fundador y garantía de entrega. Nota «precios sin IGV».
  7. Preguntas frecuentes: las 5 objeciones del guion, con respuestas cortas.
  8. Quién está detrás: nombre, foto y WhatsApp del Director.
  9. El formulario actual.
- **Criterios de aceptación:**
  - [ ] Se ve bien en celular (400 px).
  - [ ] Ninguna cifra sin fuente.
  - [ ] El Plan Medir dice **3 competidores** en el reporte y el ranking completo en el panel, que es lo que existe.
  - [ ] El Director aprueba cómo se ve (vista previa del PR) antes de publicar.
- **Necesita del Director:** su foto.
- **Notas para Claude Code:** HTML plano, sin compilar ni cambiar de stack; referencia de estructura `PaulleDemon/awesome-landing-pages`. Los datos de Osiptel y BrightLocal se enlazan a la fuente exacta; si no se puede verificar alguno, no se publica.

### C9b-T05 · Panel e informe con la marca
- **Estado:** ✅ (entró con T03; «visible-ia» queda solo en nombres internos: clave de almacenamiento, comando de la CLI y la URL)
- **Qué:** solo colores, fuentes y logo en el panel, el informe de diagnóstico, el reporte mensual y el kit de atribución. Reemplazar «visible-ia» por «Eminia» en los textos visibles. Sin cambios de funciones.
- **Criterios de aceptación:** [ ] las pruebas del panel, del informe y del reporte pasan.

### C9b-T06 · Guion de llamada
- **Estado:** ✅ (`docs/06-lanzamiento/guion-llamada.md`, con las fuentes de cada cifra)
- **Qué:** `docs/06-lanzamiento/guion-llamada.md` con el guion del anexo B del acta, más estos cambios:
  - la oferta incluye sin permanencia, precio fundador y garantía de entrega (aprobados);
  - la objeción «Está caro» **no usa el precio de las agencias** (no tiene fuente). Dice: «Con lo que me contaste, un solo paciente nuevo de [tratamiento] paga varios meses del servicio»;
  - el Plan Medir compara con 3 competidores.
- Los planes y los ganchos ya quedaron en `docs/02-estrategia/estrategia.md` al procesar el acta.

### C9b · Rediseño de la landing (pedido del Director, 28/09)
- **Estado:** ✅ en el PR #67, pendiente de la aprobación del Director.
- **Skills** en `.claude/skills/`: frontend-design, ui-ux-pro-max, copywriting, copy-editing, cro y marketing-psychology.
- **Guías:** `docs/marca/VOZ.md` y `docs/marca/DESIGN.md`; en `CLAUDE.md`, la sección «Web y textos de venta».
- **Landing rehecha** con CSS propio, sin Pico (el panel sigue con Pico):
  - contenedor de 1120 px y encabezado fijo;
  - primera pantalla en dos columnas, con el chat animado;
  - una sola sección en Tinta (los datos);
  - imagen real de la página 1 del informe, con clínicas ficticias (`scripts/imagen_informe_landing.py`);
  - planes de igual altura con un solo botón principal;
  - formulario en una tarjeta de 640 px;
  - pie en Tinta.
- **Animaciones:** solo 3, que se apagan con `prefers-reduced-motion`.
- **Pendiente:** la foto del Director (`web/marca/gianpol.jpg`).

### C9b · Contenido, legal y consentimiento (Director, 28/09)
- **Estado:** ✅ en el PR #67, pendiente de publicación.
- **Landing:**
  - Índice Eminia (también en el PDF, el reporte y el panel) y la sección «Qué mira la IA» (fase 1);
  - caso real anónimo y datos propios (34 clínicas, 1 de cada 2, 5 de 9);
  - «Qué pasa después» (3 días hábiles) y «Para quién no es»;
  - Pew en las preguntas frecuentes y el bloque de testimonios oculto;
  - el **Plan Gestionado como servicio principal** («Te ayudamos a que la IA te recomiende») y la objeción «¿Y si lo mido yo?», también en el guion.
- **Legal (borradores para abogado o contador):** `privacidad.html` (12 meses de conservación, confirmado) y `terminos.html`. El Libro de Reclamaciones queda **fuera de `web/`** (`docs/legal/borradores/`) hasta tener RUC y una forma de recibir los reclamos.
- **Migración 0009** (`prospects.consent_version`), en dev y prod. Queda **opcional** hasta publicar la landing nueva. **Pendiente:** al publicar, una migración que la haga obligatoria.

### C9b-C008 · Diagnóstico más profundo (cambio C-008, 28/09)
- **Estado:** ✅ en el PR #67; migración 0010 en dev y prod (28/09). «Dónde te falta estar» excluye también las fichas de Google de otras clínicas (Director, 28/09).
- **Tres secciones nuevas** en el diagnóstico gratis, solo con respuestas guardadas y sin corridas nuevas:
  - «Por qué la IA eligió a tu competencia»: frases **literales**; gpt-5-nano solo elige números, se valida que la frase esté tal cual en la respuesta y hay respaldo sin IA;
  - «En qué preguntas apareces»: tabla por forma;
  - «Dónde te falta estar»: máx. 8 páginas; sin las webs de los competidores.
- **Costo real:** 3 llamadas, US$0.0001 por diagnóstico. Se registra en el presupuesto mensual (migración **0010**, `llm_costs`). Opción `--sin-ia`.
- **Plantilla** `docs/06-lanzamiento/auditoria-puesta-a-punto.md`.
- **Ejemplo:** `scripts/ejemplo_diagnostico.py` (demo ficticio en dev). El diagnóstico queda en **5 páginas**; la landing y la estrategia ya lo dicen.

### C9b · Cambios de conversión 1, 3 y 5 (revisión CRO, Director 28/09)
- **1.** «Pídelo por WhatsApp» con mensaje ya escrito, en la portada y junto al botón del formulario.
- **3.** La oferta concreta sobre el botón: «Gratis y en 3 días hábiles: tu Índice Eminia frente a 3 competidores de tu distrito, y 3 arreglos concretos». Botón en primera persona: «Quiero mi diagnóstico gratis».
- **5.** Formulario:
  - «1 minuto · Sin compromiso · Te respondemos por WhatsApp»;
  - se quitó el distrito «Otro»;
  - al enviar: plazo y enlace para adelantarlo por WhatsApp.
- Los pedidos por WhatsApp no quedan en la base con su consentimiento: se registran a mano.

### C9b-C008 · Rediseño del diagnóstico gratis (Director, 28/09)
- **Estado:** ✅ en el PR #67.
- **Estructura:**
  1. Resumen, solo en la página 1: banda con la clínica; 3 cifras (índice con rango, puesto y posición promedio); semáforo de 4 áreas; barras; 3 hallazgos; próximo paso.
  2. Tú frente a tu competencia.
  3. En qué preguntas apareces: cuadrícula y consistencia.
  4. Por qué la IA eligió a tu competencia, con 2 respuestas de ejemplo.
  5. Dónde te falta estar.
  6. Tu plan de acción.
  - Anexo «Método Eminia» y glosario.
- **Reglas:**
  - semáforo en `informes/semaforo.toml` (criterio Eminia), con pruebas en `tests/unit/test_semaforo.py`;
  - esfuerzo de cada arreglo en `recomendaciones.toml`.
- **Diseño:**
  - letras en `informes/fuentes/` (OFL), incrustadas en el HTML;
  - encabezado y pie de Chromium con «Página X de N»;
  - las secciones comparten página sin cortar tarjetas ni tablas.
  - Resultado: **7 páginas** (6 más el anexo).
- **Scripts:**
  - `scripts/ejemplo_diagnostico.py` saca todas las páginas como imagen con pdf.js;
  - `scripts/imagen_informe_landing.py` saca la portada para la landing;
  - capturas de la landing a doble resolución.

## Demo de la fase
- El Director ve en la vista previa del PR la landing nueva en su celular y en la computadora, el panel y un PDF de ejemplo con la marca Eminia.
- Si los aprueba, se publica en Cloudflare Pages al fusionar a `main`.
