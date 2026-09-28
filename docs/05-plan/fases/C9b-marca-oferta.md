# Fase C9b · Marca y oferta (antes de las llamadas del 05/10)

**Objetivo:** llegar a las primeras llamadas con la marca **Eminia** (ADR-005) aplicada en la landing, el panel y el informe, y con una oferta clara (planes, ganchos y guion). Sin funciones nuevas: solo aspecto, textos y documentos.
**Origen:** acta `memoria/actas/2026-09-28-marca-y-oferta.md` · cambio C-007
**Historias que cubre:** apoya HU-26 (landing) y la venta de la v1.1
**Estado:** ⚪ pendiente (aprobada por el Director el 28/09, antes de C10)
**Nota:** no agrega dependencias. El repo, el paquete y la URL siguen como `visible-ia`; solo cambian los textos visibles.

## Tareas

### C9b-T01 · Documento de marca
- **Estado:** ⚪
- **Qué:**
  - Crear `docs/marca/marca.md` con: nombre, lema, colores, tipografías, reglas de uso del logo y el tono.
  - Tono: colega que sabe de marketing de clínicas; tuteo; siempre con número y rango; nunca «garantizamos el puesto #1»; sin «prompts», «LLM», «GEO»; ejemplos de Lima.
  - El ADR ya existe: ADR-005.
- **Criterios de aceptación:** [ ] coincide con el ADR-005 y con el acta.
- **Rama:** `feat/C9b-marca-y-oferta` (una rama para toda la fase; un commit por tarea)

### C9b-T02 · Logo, favicon y `marca.toml`
- **Estado:** ⚪
- **Qué:**
  - Guardar `web/marca/logo.svg` y `web/marca/simbolo.svg` (el SVG del anexo A del acta; el símbolo es sin `<text>` y con `viewBox="0 0 48 48"`).
  - Usar el símbolo como favicon de la landing y el panel.
  - En `src/visible_ia/informes/marca.toml`: `nombre`, `lema`, `color_primario` (#0F1B2D), `color_acento` (= «tu clínica», #2447C8), `color_suave` y `logo_url` como data URI del SVG, para que el PDF no dependa de internet.
- **Criterios de aceptación:** [ ] el PDF sale con el logo sin conexión.

### C9b-T03 · Colores y letras (tokens)
- **Estado:** ⚪
- **Qué:**
  - Landing y panel: mantener Pico CSS, pero sobrescribir sus variables (`--pico-primary`, `--pico-primary-background`, `--pico-font-family`, fondos) con los colores del ADR-005.
  - Cargar Source Serif 4, IBM Plex Sans e IBM Plex Mono desde Google Fonts.
  - En `estilos.css` del informe, las mismas fuentes con respaldo a las actuales.
- **Criterios de aceptación:**
  - [ ] Contraste AA (4.5:1) en todo texto.
  - [ ] Un solo color (cobalto) para «tu clínica» y los botones.
- **Pruebas:** `tests/unit/test_informe_diagnostico.py` y `test_informe_mensual.py`; regenerar el PDF de ejemplo para que lo mire el Director.

### C9b-T04 · Landing nueva
- **Estado:** ⚪
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
- **Estado:** ⚪
- **Qué:** solo colores, fuentes y logo en el panel, el informe de diagnóstico, el reporte mensual y el kit de atribución. Reemplazar «visible-ia» por «Eminia» en los textos visibles. Sin cambios de funciones.
- **Criterios de aceptación:** [ ] las pruebas del panel, del informe y del reporte pasan.

### C9b-T06 · Guion de llamada
- **Estado:** ⚪
- **Qué:** `docs/06-lanzamiento/guion-llamada.md` con el guion del anexo B del acta, más estos cambios:
  - la oferta incluye sin permanencia, precio fundador y garantía de entrega (aprobados);
  - la objeción «Está caro» **no usa el precio de las agencias** (no tiene fuente). Dice: «Con lo que me contaste, un solo paciente nuevo de [tratamiento] paga varios meses del servicio»;
  - el Plan Medir compara con 3 competidores.
- Los planes y los ganchos ya quedaron en `docs/02-estrategia/estrategia.md` al procesar el acta.

## Demo de la fase
- El Director ve en la vista previa del PR la landing nueva en su celular y en la computadora, el panel y un PDF de ejemplo con la marca Eminia.
- Si los aprueba, se publica en Cloudflare Pages al fusionar a `main`.
