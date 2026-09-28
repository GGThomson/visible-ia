# DESIGN.md · Eminia
<!-- Formato DESIGN.md (Stitch / VoltAgent awesome-design-md). Base: docs/marca/marca.md y ADR-005: colores, letras y logo NO cambian aquí. Léelo antes de tocar web/. -->

## 1. Visual Theme & Atmosphere
Consultora de datos, no clínica: sin cruces, verdes ni fotos de stock de doctores.
- Sobria, clara y con aire. Se lee como un informe bien hecho, no como una app de moda.
- La idea que se repite en todo (logo, barras del informe, landing): **«tu clínica» destacada en cobalto frente a la competencia en gris pizarra**.
- La densidad es baja: mucho espacio en blanco, una idea por sección y una acción por sección.
- Solo imágenes reales: el producto (el informe, el panel) y la persona real detrás.

## 2. Color Palette & Roles
| Token | Hex | Rol |
|---|---|---|
| `--tinta` | `#0F1B2D` | Primario: títulos, texto principal, logo, **una** sección oscura por página y el pie |
| `--pizarra` | `#51607A` | Texto secundario, barras de la competencia, bordes de botones secundarios |
| `--cobalto` | `#2447C8` | **Solo** «tu clínica», el botón principal y los enlaces. Texto blanco encima (7.5:1) |
| `--cobalto-oscuro` | `#1B369C` | Hover y presionado del cobalto |
| `--cobalto-claro` | `#7B93FF` | Cobalto sobre fondo Tinta (sección oscura, pie) |
| `--niebla` | `#F4F6F9` | Fondo alterno de secciones y tarjetas suaves |
| `--blanco` | `#FFFFFF` | Fondo alterno de secciones y tarjetas |
| `--linea` | `#D9DEE7` | Bordes y separadores |

- **Contraste AA (4.5:1) en todo texto.** Tinta sobre Niebla: 16:1. Pizarra sobre blanco: 6.4:1 (sobre Niebla, 5.9:1). Blanco sobre Cobalto: 7.5:1. Cobalto claro sobre Tinta: 6.1:1.
- Sobre Tinta, el texto va en blanco o en `#C9D1E0` (secundario), y los enlaces en cobalto claro.
- **Un solo color de resalte.** Si algo no es «tu clínica», un botón principal o un enlace, no va en cobalto.
- Sin degradados. Sin colores de estado decorativos.

## 3. Typography Rules
| Familia | Uso | Respaldo |
|---|---|---|
| **Source Serif 4** 600 | Títulos, logo y **cifras grandes** (23 %, S/ 349) | Georgia, serif |
| **IBM Plex Sans** 400 / 600 | Texto, botones y formularios | Segoe UI, system-ui, Arial |
| **IBM Plex Mono** 500 | **Solo** etiquetas pequeñas y rangos («entre 5 % y 20 %», fechas) | Consolas, monospace |

Escala (base 16 px; interlineado del texto 1.6, de los títulos 1.15):

| Rol | Computadora | Celular |
|---|---|---|
| Título principal (h1) | 48 px, máx. 3 líneas | 32 px |
| Título de sección (h2) | 36 px | 28 px |
| Subtítulo (h3) | 22 px | 20 px |
| Cifra grande | 56 px, Source Serif 4 | 40 px |
| Frase de apoyo (lead) | 20 px | 18 px |
| Texto | 17 px | 16 px |
| Pequeño / nota | 14 px | 14 px |
| Etiqueta mono | 13 px | 13 px |

- Párrafos de **65 caracteres como máximo** (`max-width: 65ch`).
- Todo en minúsculas normales (sentence case). **Sin etiquetas en MAYÚSCULAS.**
- Sin resaltar una sola palabra del titular con otro color o cursiva.

## 4. Component Stylings
**Botón principal**
- Fondo cobalto, texto blanco, Plex Sans 600, 16 px.
- Relleno 14 × 24 px, radio 8 px, altura mínima 48 px.
- Hover: cobalto oscuro. Foco: anillo de 3 px `#7B93FF` con 2 px de separación.
- **Uno solo por sección.**

**Botón secundario**
- Fondo transparente, borde 1.5 px pizarra y texto tinta.
- Hover: fondo Niebla. Mismas medidas que el principal.

**Tarjeta**
- Fondo blanco (sobre Niebla) o Niebla (sobre blanco), borde 1 px línea, radio 12 px, relleno 32 px (24 px en celular).
- Sin sombra, salvo la tarjeta destacada (ver §6).

**Tarjeta de plan**
- Todas de la misma altura, con el botón alineado abajo.
- El servicio principal (Plan Gestionado) va primero y lleva borde 2 px cobalto, una etiqueta «Servicio principal» (mono 13 px, sin mayúsculas) y el **único** botón principal. Los demás llevan botón secundario.

**Formulario**
- Dentro de una tarjeta de **máximo 640 px**, centrada.
- Dos columnas en computadora (nombre / clínica, especialidad / distrito) y una en celular.
- Etiqueta siempre visible encima del campo, nunca solo placeholder.
- Campos de 48 px de alto, borde 1 px línea, radio 8 px; foco con borde cobalto y anillo.
- Error debajo del campo, en texto (no solo en color).
- El botón va a ancho normal en computadora y a ancho completo solo en celular.

**Encabezado**
- Fijo arriba, fondo blanco con borde inferior línea, 64 px de alto.
- Logo a la izquierda; a la derecha, enlaces (Cómo funciona, Planes, Preguntas) y el botón «Informe gratis».
- En celular, solo el logo y el botón.

**Pie**
- Fondo tinta, logo en versión clara, WhatsApp y la nota «No prometemos un puesto #1».

**Barras del ranking**
- Riel en línea (`#D9DEE7`), relleno pizarra para la competencia y cobalto para «tu clínica».
- Radio 4 px. El valor va en texto con su rango.

## 5. Layout Principles
- **Espacios en múltiplos de 8 px:** 8, 16, 24, 32, 48, 64, 96, 128.
- **Contenedor de máximo 1120 px**, centrado, con márgenes laterales de 24 px (16 px en celular).
- **Entre secciones:** de 96 a 128 px en computadora y de 64 a 80 px en celular.
- **Ritmo de fondos:** las secciones alternan Niebla y blanco, con **una sola** sección en Tinta por página (la de los datos).
- **Primera pantalla** en dos columnas (texto a la izquierda, ejemplo a la derecha). En celular, una debajo de la otra.
- Texto alineado a la izquierda. Centrado solo en el formulario y en títulos de sección cortos.

## 6. Depth & Elevation
| Nivel | Uso | Sombra |
|---|---|---|
| 0 | Casi todo: secciones, tarjetas, campos | Ninguna (borde 1 px línea) |
| 1 | Tarjeta de chat de ejemplo, tarjeta del formulario | `0 8px 24px rgba(15, 27, 45, 0.08)` |
| 2 | Imagen del informe (inclinada 2–3°) | `0 16px 40px rgba(15, 27, 45, 0.14)` |

Radios: 4 px (barras), 8 px (botones y campos), 12 px (tarjetas), 16 px (foto de la persona).

## 7. Do's and Don'ts
| Sí | No |
|---|---|
| Un solo color de resalte (cobalto) para «tu clínica» y el botón principal | Cobalto decorativo en títulos, íconos o fondos |
| Cifras con su rango y su fuente | Cifras sin fuente o redondeadas a favor |
| Imágenes reales del informe y del panel | Fotos de stock de doctores, cruces o estetoscopios |
| Una acción por sección | Varios botones principales compitiendo |
| Etiquetas en minúsculas normales | Etiquetas en MAYÚSCULAS con espaciado |
| Ejemplos marcados como ejemplo | Testimonios o logos de clientes inventados |
| Tres animaciones con propósito (§8) | Animaciones en bucle, en cada tarjeta o al pasar el cursor por todo |
| Degradados: nunca | Degradados, brillos, emojis |

## 8. Responsive Behavior
- **Puntos de corte:** 390 px (celular), 768 px (tableta) y 1120 px o más (computadora).
- Sin desplazamiento horizontal en ningún ancho.
- Zonas táctiles de 44 × 44 px como mínimo.
- En celular:
  - el encabezado muestra solo el logo y el botón;
  - las columnas pasan a una;
  - el botón del formulario va a ancho completo.
- **Animaciones permitidas (solo tres, de 200 a 600 ms, nada en bucle):**
  1. el chat de ejemplo: aparece la pregunta, la respuesta se escribe línea por línea y al final aparece «Tu clínica no aparece»;
  2. las barras del informe crecen de 0 a su valor al entrar en pantalla;
  3. una aparición suave de las secciones al bajar (opacidad y 16 px de desplazamiento).
- **`prefers-reduced-motion: reduce` las apaga todas** y muestra el estado final.
- **Accesibilidad:** foco visible en todo lo que se puede tocar, textos alternativos en las imágenes, contraste AA.

## 9. Agent Prompt Guide
**Referencia rápida:** tinta `#0F1B2D` · pizarra `#51607A` · cobalto `#2447C8` (solo «tu clínica» y el botón principal) · niebla `#F4F6F9` · línea `#D9DEE7`. Títulos y cifras grandes en Source Serif 4 600; texto en IBM Plex Sans; mono solo en etiquetas pequeñas y rangos. Contenedor de 1120 px, espacios de 8 px, radios de 8 y 12 px.

**Antes de cambiar `web/`:**
1. Lee este archivo, `docs/marca/VOZ.md` y las skills `frontend-design`, `copywriting` y `marketing-psychology` (`.claude/skills/`).
2. HTML y CSS propios, sin paso de compilación ni frameworks nuevos.
3. Después de cada cambio visual, saca capturas con Playwright en **390, 768 y 1440 px**, míralas y corrige antes de mostrar nada.

**Ejemplo de encargo:** «Agrega una sección de preguntas frecuentes siguiendo DESIGN.md: fondo Niebla, título h2 en Source Serif 4, acordeones con borde inferior línea y texto de 65 caracteres de ancho, sin botón principal (la acción de la página es el formulario).»
