# ADR-005 · Marca "Eminia" y sistema visual

- **Fecha:** 2026-09-28
- **Estado:** Aceptada
- **Decide:** Director
- **Consultados:** Claude web (acta `memoria/actas/2026-09-28-marca-y-oferta.md`), Claude Code (revisión)

## Contexto
La landing, el informe y el panel se veían genéricos con el nombre de trabajo «visible-ia», y las llamadas de venta empiezan el 05/10. Hacía falta una marca mínima antes de hablar con clínicas, sin construir funciones nuevas.

## Opciones consideradas
| Opción | Ventajas | Desventajas | Costo / esfuerzo |
|---|---|---|---|
| Visible IA (nombre de trabajo) | Ya está en todo el producto | Genérico; el Director lo rechazó (ronda 1) | 0 |
| Citada | La línea que eligió el Director (ronda 2) | Ya existe «Citável» (citavel.ai, Brasil) en el mismo negocio | — |
| **Eminia** | De «eminencia» («es una eminencia» = el mejor médico, en Perú); original; no se encontró ninguna empresa con ese nombre | eminia.com está registrado (sin sitio activo); hay que revisar INDECOPI y el .pe | Registro .pe + INDECOPI (lo decide el Director) |
| Prominia | De «prominencia»; prominia.com está en venta | Menos ligado al lenguaje de salud | Igual |

Otros nombres descartados porque ya existen: Mentio, Relevia, Lumbra, Clarea, Laudia, Aludia, Nombra/Nombrand.

## Decisión
Elegimos **Eminia**, con el lema **«Que la IA te nombre a ti»**. **Prominia** queda de respaldo si INDECOPI (clases 35 y 42) o eminia.pe no están libres.

El sistema visual es de consultora de datos, no de clínica (sin cruces ni verdes):
- **Logo:** una «E» hecha con las barras del informe; la barra del medio, más larga y en cobalto, es «tu clínica».
- **Colores:**
  - Tinta noche #0F1B2D: primario, títulos y logo.
  - Pizarra #51607A: barras de la competencia y texto secundario.
  - Cobalto #2447C8: **solo** «tu clínica» y los botones (texto blanco encima, contraste 7.5:1). En fondo oscuro pasa a #7B93FF.
  - Niebla #F4F6F9: fondo.
  - Línea #D9DEE7: bordes.
- **Letras:** Source Serif 4 (600) para títulos y logo; IBM Plex Sans (400/600) para texto; IBM Plex Mono (500) para cifras y etiquetas.
- **Reglas**, tomadas de NHS, GOV.UK, USWDS e IBM Carbon:
  - un solo color resalta «tu clínica»;
  - contraste AA (4.5:1);
  - sin degradados ni emojis;
  - cifras siempre con su rango.

El detalle y el tono van en `docs/marca/marca.md` (C9b-T1).

## Consecuencias
- **Positivas:**
  - Una identidad coherente en la landing, el panel y el informe antes de las llamadas.
  - El logo repite la idea del producto: «tu clínica» destacada frente a la competencia.
- **Negativas / lo que aceptamos:**
  - El repo, el paquete Python y la URL siguen como `visible-ia` por ahora; solo cambian los textos visibles.
  - Hasta revisar INDECOPI y el .pe, la marca podría tener que cambiar a Prominia.
- **Si cambiamos de opinión:** el nombre, los colores y el logo viven en `marca.toml` (informe) y en variables CSS (landing y panel), así que cambiar a Prominia es cambiar esos valores y el SVG.
