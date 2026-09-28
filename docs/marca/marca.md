# Marca · Eminia
<!-- Decisión: docs/decisiones/ADR-005-marca-eminia.md · Acta: memoria/actas/2026-09-28-marca-y-oferta.md -->

**Eminia**, de «eminencia»: en Perú se dice «es una eminencia» del mejor médico. La idea es que la IA te nombre como la eminencia de tu distrito.

- **Lema:** Que la IA te nombre a ti.
- **Respaldo:** Prominia («Destaca cuando un paciente le pregunta a la IA»), si INDECOPI (clases 35 y 42) o eminia.pe no están libres.
- **Nombre técnico:** el repo, el paquete Python y la URL siguen como `visible-ia`. En los textos que ve una clínica siempre dice **Eminia**.

## Logo
Una «E» hecha con las barras del informe. La barra del medio, más larga y en cobalto, es **«tu clínica»**.

| Archivo | Uso |
|---|---|
| `web/marca/logo.svg` | Logo completo (240 × 48): cabecera de la landing, el panel y los PDF |
| `web/marca/simbolo.svg` | Solo la «E» (48 × 48): favicon y espacios chicos |

- Sobre fondo claro (Niebla o blanco). No se deforma, no se le agregan sombras ni degradados, y no se cambia el color de las barras.
- Espacio libre alrededor: al menos la altura de una barra (5 unidades del SVG).
- En los PDF va incrustado (data URI en `marca.toml`), para que no dependa de internet.

## Colores
| Nombre | Hex | Uso |
|---|---|---|
| Tinta noche | `#0F1B2D` | Primario: títulos, logo y texto principal |
| Pizarra | `#51607A` | Barras de la competencia y texto secundario |
| Cobalto | `#2447C8` | **Solo** «tu clínica» y los botones (texto blanco encima: 7.5:1) |
| Cobalto en fondo oscuro | `#7B93FF` | Lo mismo que el cobalto, sobre fondos oscuros |
| Niebla | `#F4F6F9` | Fondo de página y de tarjetas suaves |
| Línea | `#D9DEE7` | Bordes y separadores |

## Letras
| Familia | Peso | Uso |
|---|---|---|
| Source Serif 4 | 600 | Títulos y logo |
| IBM Plex Sans | 400 / 600 | Texto |
| IBM Plex Mono | 500 | Cifras y etiquetas (%, rangos, meses) |

En la web se cargan desde Google Fonts. En los PDF tienen respaldo (Georgia; Segoe UI / Arial; Consolas), por si no hay conexión.

## Reglas de diseño
Tomadas de los sistemas de diseño de salud y gobierno publicados (NHS, GOV.UK, USWDS, IBM Carbon):
1. Un solo color resalta «tu clínica»: el cobalto. La competencia va en pizarra.
2. Todo texto cumple contraste AA (4.5:1).
3. Nada de degradados ni emojis.
4. Toda cifra va con su rango: «10 % (entre 5 % y 20 %)».

## Tono
- Hablamos como un colega que sabe de marketing de clínicas: claro, cercano y con datos. **Tuteamos.**
- Siempre con número y rango («te nombra en 10 %, entre 5 % y 20 %»). **Nunca** «garantizamos el puesto #1»: nadie controla lo que responde la IA.
- Decimos «pacientes», «tu clínica», «tu distrito». No decimos «prompts», «LLM», «GEO» ni «SEO generativo».
- Usamos nombres reales de Lima y ejemplos de Lima.
- Toda cifra de mercado lleva su fuente.

| Sí | No |
|---|---|
| «La IA ya recomienda clínicas en tu distrito. Veamos si te nombra a ti.» | «Revoluciona tu presencia digital con IA.» |
| «Te nombra en 1 de cada 10 respuestas; a tu competidor, en 5.» | «Domina los resultados de la IA.» |
| «No te garantizamos salir primero: te mostramos cada mes cuánto te nombra.» | «Garantizamos el #1 en ChatGPT.» |
