# Acta 2026-09-28 · Marca mínima y oferta para las llamadas del 05/10
<!-- Creada con /acta a partir del texto de Claude web pegado por el Director. -->

- **Participantes:** Director, Claude web (planificador), Claude Code (revisión del ejecutor)
- **Tema:** marca mínima (nombre, logo, colores, letras, tono) y oferta más clara antes de las primeras llamadas (05/10)
- **Contexto usado:** `memoria/contexto-rapido.md` versión 2026-09-27

## Contexto
- **Problema:** el Director siente que la landing, el informe y el panel se ven genéricos y que el servicio se vende poco.
- **Objetivo:** llegar a las llamadas del 05/10 con una marca mínima y una oferta clara.
- **Regla acordada:** no construir funciones nuevas antes de validar que las clínicas pagan. Todo usa lo que ya existe (informe, panel, checklist, JSON-LD, kit de atribución) o es servicio manual.

## Propuestas recibidas
Solo hubo un planificador (Claude web), así que no hay desacuerdos entre IAs. La última columna es la revisión de Claude Code contra el repositorio.

| De | Propuesta | A favor | En contra / observación del ejecutor |
|---|---|---|---|
| Claude web | **Nombre "Eminia"**, de "eminencia" (en Perú, "es una eminencia" = el mejor médico). Lema: «Que la IA te nombre a ti». Respaldo: **Prominia** («Destaca cuando un paciente le pregunta a la IA»). Se descartaron Citada (existe Citável en Brasil), Mentio, Relevia, Lumbra, Clarea, Laudia, Aludia y Nombra/Nombrand. | Original; no se encontró ninguna empresa con ese nombre; conecta con el lenguaje de salud de Lima | Antes de comprar el dominio o registrar la marca hay que revisar INDECOPI (clases 35 y 42) y el .pe (cuesta dinero). eminia.com está registrado pero sin sitio activo. El repo, el paquete y la URL siguen como `visible-ia`. |
| Claude web | **Sistema visual** de consultora de datos, sin cruces ni verdes de clínica. Colores: Tinta noche #0F1B2D, Pizarra #51607A, Cobalto #2447C8 (solo «tu clínica» y botones; #7B93FF en fondo oscuro), Niebla #F4F6F9, Línea #D9DEE7. Letras: Source Serif 4 (600), IBM Plex Sans (400/600) e IBM Plex Mono (500). Logo: una «E» hecha con barras del informe; la del medio, en cobalto, es «tu clínica». | Coherente con el producto (barras del ranking); un solo color de resalte | Las fuentes de Google Fonts ya están permitidas en la landing. En el PDF hacen falta fuentes de respaldo por si no hay internet. |
| Claude web | **Reglas de diseño** tomadas de NHS, GOV.UK, USWDS e IBM Carbon: un solo color resalta «tu clínica»; contraste AA (4.5:1); sin degradados ni emojis; cifras siempre con su rango. | Ya coincide con cómo se muestran las cifras (rango de Wilson, ADR-003) | — |
| Claude web | **Planes:** «Diagnóstico gratis» (informe actual); «Plan Medir» S/ 349/mes por sede + S/ 490 de puesta a punto; «Plan Gestionado» S/ 790/mes + S/ 990, con 3 mejoras al mes y una llamada de 15 min, mostrado como «más completo». Agencias (S/ 690) fuera de la landing de clínicas: tendrán su página en C10. | Usa los precios tentativos ya aprobados (estrategia y C-004); solo cambian los nombres y lo que incluye cada uno | **Medir promete «comparación con 5 competidores», pero el informe y el reporte mensual muestran 3** (`informes/mensual.py`, `informe diagnostico`). El panel sí muestra el top 10 del mercado. |
| Claude web | **Ganchos comerciales** (decisión de dinero): a) sin permanencia; b) «precio fundador» para las 5 primeras clínicas (puesta a punto a mitad de precio y mensualidad congelada 12 meses); c) devolución de la puesta a punto si el checklist y los arreglos no se entregan en 10 días hábiles. Recomendación: sí a los tres. | Bajan la barrera de la primera venta (H6); no se promete subir en la IA | Todos tienen impacto en ingresos y los decide el Director. |
| Claude web | **Datos para vender:** Osiptel ERESTEL 2025 (1 de cada 4 personas en Lima Metropolitana usa IA; cerca de la mitad en el NSE A); BrightLocal, marzo 2026 (45 % en EE. UU. pide a la IA recomendaciones de negocios locales; 6 % un año antes); medición propia (30 de 30 respuestas nombran clínicas); el dato propio de cada clínica. | Todos llevan fuente | El dato «30 de 30» está respaldado (`investigacion.md`, fase 1). Osiptel y BrightLocal no están en el repo: hay que enlazar la fuente exacta antes de publicarlos. **En el guion, «las agencias de Lima cobran desde S/ 2,500 al mes» no tiene fuente**: S/ 2,500 es nuestra meta de preventas (H6), no un precio de mercado. |
| Claude web | **Tareas para Claude Code** en una tarea nueva «C9b · Marca y oferta», rama `feat/marca-y-oferta`: T1 documento de marca + ADR; T2 logo y favicon + `marca.toml`; T3 tokens de color y letras; T4 landing nueva (9 bloques, mismo formulario); T5 panel e informe (solo aspecto); T6 guion y planes en la estrategia. Sin dependencias nuevas; el Director aprueba cómo se ve antes de publicar. | No toca funciones; entra antes del 05/10 | Es un cambio de alcance (tarea nueva antes de C10). La landing necesita la **foto y el nombre del Director**. |
| Claude web | **Tono:** colega que sabe de marketing de clínicas; tuteo; siempre con número y rango; nunca «garantizamos el puesto #1»; sin «prompts», «LLM», «GEO»; ejemplos de Lima. | Coincide con los textos actuales del informe | — |

## Decisión del Director
- **Se decidió (28/09):**
  1. Marca **Eminia** («Que la IA te nombre a ti»), con el sistema visual propuesto. **Prominia** queda de respaldo si INDECOPI o el .pe no están libres.
  2. Los **tres ganchos**: sin permanencia; precio fundador para las 5 primeras clínicas (puesta a punto a mitad de precio y mensualidad congelada 12 meses); garantía de entrega en 10 días hábiles.
  3. **C9b · Marca y oferta** se hace **antes de C10**.
  4. La objeción «Está caro» **cambia de argumento**: sin el precio de las agencias (no tiene fuente), se usa el valor de un paciente nuevo según lo que la clínica respondió en la llamada.
  5. El Plan Medir ofrece **3 competidores** en el reporte y el ranking completo en el panel, que es lo que ya existe. No se cambia código.
- **Porque:** llegar al 05/10 con una marca y una oferta claras, sin construir funciones antes de validar que las clínicas pagan (H6), y sin cifras que no se puedan respaldar.
- **ADR generado:** `docs/decisiones/ADR-005-marca-eminia.md`.
- **Otros documentos:** planes y ganchos en `docs/02-estrategia/estrategia.md`; cambio C-007 en `memoria/cambios-pendientes.md`; plan `docs/05-plan/fases/C9b-marca-oferta.md`; roadmap.

## Tareas que salen de aquí
- [ ] **C9b · Marca y oferta** (T01–T06): `docs/05-plan/fases/C9b-marca-oferta.md`.
- [ ] Director: revisar INDECOPI (clases 35 y 42) y la disponibilidad de eminia.pe antes de comprar o registrar.
- [ ] Director: enviar su foto para «Quién está detrás» en la landing (C9b-T04).

## Preguntas que quedan abiertas
- ¿Eminia está libre en INDECOPI y como .pe? Si no, se pasa a Prominia (ADR-005).
- Las fuentes exactas de Osiptel y BrightLocal se enlazan y verifican en C9b-T04; si alguna no se puede verificar, no se publica.

## Anexo A · Logos (SVG, 240 × 48)
El símbolo solo es el mismo SVG sin el `<text>` y con `viewBox="0 0 48 48"`.

Eminia
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 48" role="img" aria-label="Eminia">
  <rect x="10" y="9" width="5" height="30" fill="#0F1B2D"/>
  <rect x="10" y="9" width="20" height="5" fill="#0F1B2D"/>
  <rect x="10" y="21.5" width="28" height="5" fill="#2447C8"/>
  <rect x="10" y="34" width="15" height="5" fill="#0F1B2D"/>
  <text x="50" y="33" font-family="'Source Serif 4', Georgia, serif" font-size="27" font-weight="600" fill="#0F1B2D">Eminia</text>
</svg>
```

Prominia (respaldo)
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 250 48" role="img" aria-label="Prominia">
  <rect x="9" y="9" width="17" height="5" fill="#0F1B2D"/>
  <rect x="9" y="21.5" width="30" height="5" fill="#2447C8"/>
  <rect x="9" y="34" width="22" height="5" fill="#0F1B2D"/>
  <text x="50" y="33" font-family="'Source Serif 4', Georgia, serif" font-size="27" font-weight="600" fill="#0F1B2D">Prominia</text>
</svg>
```

## Anexo B · Guion de llamada (10 a 15 min, por WhatsApp o Meet), tal como lo propuso Claude web
Se pasa a `docs/06-lanzamiento/guion-llamada.md` en C9b-T6, con los cambios que decida el Director.

Antes de llamar: tener abierto el informe de esa clínica y anotar su dato fuerte (estrellas, reseñas y % en la IA).

1. **Apertura (30 s).** «Hola, [nombre], soy Gianpol de [marca]. Te mandé el informe de cómo te ve ChatGPT cuando un paciente busca [tratamiento] en [distrito]. ¿Tienes 10 minutos para que te muestre lo que encontramos?»
2. **El dato (1 min).** «Tienes [4.9★ y 1,135 reseñas] en Google Maps, que es excelente. Pero cuando un paciente le pregunta a la IA, te nombra en [1 de cada 10] respuestas. A [competidor] lo nombra en [5 de cada 10].» Mostrar la barra y una respuesta real de la IA.
3. **Preguntas (3 min).** Escuchar más que hablar:
   - «¿Cuántos pacientes nuevos recibes al mes y de dónde llegan?»
   - «¿Alguno te ha dicho que te encontró por ChatGPT o Google?»
   - «¿Cuánto te deja en promedio un paciente nuevo de [tratamiento]?»
   - «¿Quién ve hoy tu ficha de Google, tu web y Doctoralia?»
4. **Puente de valor (1 min).** «Con lo que me dices, un solo paciente nuevo al mes paga el servicio varias veces. Y hoy la IA manda esos pacientes a [competidor].»
5. **Oferta (2 min).** Dos opciones, nada más:
   - «Plan Medir: cada mes te digo cuánto te nombra la IA frente a tu competencia y te doy la lista exacta de arreglos. Los hace tu equipo. S/ 349 al mes.»
   - «Plan Gestionado: además de medir, nosotros hacemos 3 mejoras al mes y te llamo 15 minutos para contarte cómo vas. S/ 790 al mes.»
   - Si está aprobado: «Eres de las 5 primeras clínicas, así que la puesta a punto va a mitad de precio y el precio queda congelado un año. Sin permanencia.»
6. **Cierre (1 min).** «¿Cuál de las dos te hace más sentido?» Si duda: «¿Qué tendría que pasar para que lo pruebes un mes?»
7. **Anotar siempre** (para validar H6 y H9): qué plan eligió o por qué no; qué precio le pareció caro o barato; si prefiere que lo haga su equipo o nosotros.

### Objeciones
- «Mis pacientes no usan ChatGPT.» → «En Lima, 1 de cada 4 personas ya usa IA, y cerca de la mitad en el nivel A (Osiptel 2025). Tus pacientes de [tratamiento] están en ese grupo. Además, Google ya pone respuestas de IA arriba de todo.»
- «Ya tengo agencia.» → «Genial. Esto mide algo que tu agencia hoy no mide. Si quieres, se lo mandamos a ellos y lo trabajan con nuestra lista.»
- «Está caro.» → «Las agencias de Lima que hacen esto cobran desde S/ 2,500 al mes. Aquí es S/ 349 y un paciente nuevo lo paga.» ⚠️ Sin fuente (ver la revisión del ejecutor).
- «¿Me garantizas salir primero?» → «No, y desconfía de quien lo haga: nadie controla lo que responde la IA. Lo que sí te doy es la medición con su rango cada mes, para que veas si subes.»
- «Déjame pensarlo.» → «Claro. ¿Qué te falta ver para decidir? Te lo mando hoy por WhatsApp.»
