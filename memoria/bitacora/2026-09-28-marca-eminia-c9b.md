# Sesión 2026-09-28 · Marca Eminia, landing nueva y diagnóstico rediseñado (C9b)

- **Fase / tareas:** acta «Marca y oferta» (C-007) → fase **C9b** (T01–T06 y extensiones), cambio **C-008** (diagnóstico más profundo y rediseñado), **ADR-006** (C-009, sin construir)
- **Rama(s):** `docs/acta-marca-oferta` (PR #66, fusionada) · `feat/C9b-marca-y-oferta` (**PR #67, abierta, sin fusionar ni publicar**)
- **Commits en `main`:** 5883208 docs: acta marca y oferta · dd331f4 merge PR #66
- **Commits en el PR #67:**
  - **Marca (T01–T06):** a22db53 guía de marca · b529ffb logo y marca del informe · 3a48952 colores y letras · ffcc06d landing Eminia · 24cda2a guion.
  - **Guías y rediseño de la landing:** 6e3ffa5 skills · 7e3bfec VOZ.md y DESIGN.md · b47ab10 rediseño de la landing · ed67199 idea, servicios y datos.
  - **Legal y consentimiento:** 13db2eb privacidad y términos · 79990ea versión de la política con el consentimiento (0009) · a5842ee Gestionado como servicio principal, sin reclamaciones.
  - **Landing con producto:** 8d6e0a5 «Qué recibes» con recorrido · 0267a43 imagen en WebP.
  - **Diagnóstico (C-008):** 1cb7ed7 registra C-008 · a7133cd diagnóstico más profundo · f8e1b19 prueba en CI · 1570b34 diagnóstico rediseñado.
  - **Conversión y cierre:** f4eaaaa WhatsApp, oferta concreta y formulario · 9538909 ilustraciones, 6 cifras y garantías + ADR-006 · 39aea72 tabla comparativa y 5 efectos.

## Qué se hizo
- **Acta de Claude web integrada:**
  - marca **Eminia** (ADR-005);
  - planes Diagnóstico gratis / Medir / Gestionado, con el Gestionado como servicio principal;
  - ganchos: sin permanencia, precio fundador para las 5 primeras y entrega en 10 días hábiles;
  - guion de llamada, con la objeción «¿Y si lo mido yo?».
- **Marca aplicada** en la landing, el panel y los PDF: logo, colores, letras Source Serif 4 / IBM Plex (incrustadas en los PDF) y guías `docs/marca/{marca,VOZ,DESIGN}.md`. Skills de diseño y redacción en `.claude/skills/`.
- **Landing rehecha** (CSS propio, sin Pico):
  - portada con chat animado y panel que asoma;
  - 6 cifras con fuente verificada (Osiptel, BrightLocal, Pew, KFF, OpenAI, medición propia);
  - «Qué recibes cada mes» con 5 pestañas ilustradas (SVG propios);
  - «Qué mira la IA» (fase 1) y caso real anónimo;
  - planes con tabla comparativa y distintivo de precio fundador;
  - preguntas frecuentes; «Quién está detrás» (espera la foto);
  - pedido por WhatsApp y formulario con consentimiento.
  - Efectos inspirados en trendos.com, sin copiar nada.
- **Legal (borradores para abogado o contador):** `privacidad.html` (12 meses de conservación) y `terminos.html`. El Libro de Reclamaciones queda en `docs/legal/borradores/` hasta tener RUC.
- **Migraciones en dev y prod:** **0009** (`prospects.consent_version`, todavía opcional) y **0010** (`llm_costs`: el gasto de gpt-5-nano del diagnóstico cuenta en el presupuesto mensual).
- **Diagnóstico gratis rediseñado (C-008, 7 páginas):**
  - resumen con 3 cifras, **semáforo de 4 áreas** (`semaforo.toml`, criterio Eminia), barras, 3 hallazgos y próximo paso;
  - tú frente a tu competencia (posición promedio y cuota de menciones);
  - cuadrícula de preguntas con consistencia entre repeticiones;
  - por qué la IA eligió a tu competencia (**frases literales**: gpt-5-nano solo elige números, US$0.0001 por diagnóstico);
  - dónde te falta estar (solo lugares donde la clínica puede estar);
  - plan de acción con impacto, esfuerzo y quién lo hace;
  - anexo «Método Eminia» y glosario.
  - Encabezado y pie con «Página X de N».
- **Plantilla de auditoría** de la puesta a punto (`docs/06-lanzamiento/auditoria-puesta-a-punto.md`).
- **Revisión de conversión** con la skill `cro`: se aplicaron los cambios 1, 3 y 5.

## Qué se decidió (y dónde quedó registrado)
- **Marca Eminia**, oferta y ganchos → ADR-005, estrategia, acta 2026-09-28, C-007.
- **Diagnóstico más profundo y rediseñado** → C-008, plan de C9b. **PRD HU-14: ≤ 8 páginas** (antes ≤ 4).
- **Planes pagados con 120 respuestas/mes** (20 preguntas × 3 × 2); el diagnóstico sigue en 60; presupuesto +US$2.50 por mercado pagado; Gemini manual; investigar Vertex AI → **ADR-006**, C-009 (sin construir).
- **Contenido:**
  - Libro de Reclamaciones fuera hasta tener RUC;
  - 12 meses de conservación de datos;
  - sin testimonios hasta el primero real con permiso escrito;
  - cifras solo verificadas (se descartaron McKinsey, que no se pudo verificar, y «la mitad del nivel A», de Osiptel);
  - las filas que solo existen en el diagnóstico van con ✓\* en la tabla de planes.

## Problemas y cómo se resolvieron
- **Datos sin fuente en el acta** (el precio de agencias S/ 2,500, «la mitad del nivel A» de Osiptel) → se quitaron o se cambió el argumento.
- **La frase partida en «Dra.»** dejaba sin enmascarar el nombre de un profesional → las abreviaturas ya no cortan frases (hay prueba), y las frases con profesionales no son candidatas.
- **Hacer obligatoria la versión de la política** habría roto el formulario en prod → 0009 la deja opcional; se hará obligatoria al publicar.
- **`\n` convertidos en saltos reales** al escribir código desde scripts → corregidos con la herramienta de edición.
- **El import de pruebas `tests.unit…`** fallaba en CI → se importa el archivo vecino, como en las demás pruebas.
- **El PDF no se podía convertir a imagen** sin poppler → pdf.js dentro de Chromium, sin dependencias nuevas.
- **La CI no tiene Chromium** → las pruebas de PDF y navegador corren en local y se saltan en CI.

## Para la próxima sesión
- **Director:**
  - revisar la vista previa del PR #67 y dar el **OK escrito para publicar**;
  - enviar su foto (`web/marca/gianpol.jpg`);
  - ofrecer el diagnóstico gratis a 3 o 4 clínicas conocidas para conseguir las primeras frases reales.
- **Al publicar:**
  - migración que hace obligatoria `consent_version`;
  - fusionar el PR #67, con lo que se publica la landing en `visible-ia.pages.dev`.
- **1/10:** aprobar la corrida de octubre (issue «Corridas de octubre»).
- **Después:** C10 (agencias) y planificar C-009 (ADR-006).

---

# Sesión 2026-09-28 (noche) · Ajustes del PR #67: foto, RUC, reclamaciones y diagnóstico coherente

- **Fase / tareas:** C9b (ajustes del Director sobre el PR #67)
- **Rama(s):** `feat/C9b-marca-y-oferta` (PR #67, sin fusionar ni publicar)
- **Commits:** d404d43 feat(C9b): foto, pie con RUC y Libro de Reclamaciones; diagnóstico coherente · e37cac6 fix(C9b): semáforo como % del líder; plan siempre con 3 acciones

## Qué se hizo
- **Landing:** foto del Director (`web/marca/gianpol.jpg`); pie «Gianpol Rosazza Bravo · RUC 10707993435» en landing, privacidad y términos (sin dirección); **Libro de Reclamaciones** pasó de `docs/legal/borradores/` a `web/reclamaciones.html`, enlazado en todos los pies. La hoja se envía por WhatsApp (sin tabla nueva en la base).
- **Diagnóstico:** semáforo, hallazgos, plan y página 5 leen un único `Facts` (`semaforo.py`, `build_facts` en `contexto.py`); prueba que falla si se contradicen. Redes propias de otras clínicas fuera de «Páginas que te faltan», con línea aparte de Instagram. Plan ordenado por impacto calculado (respuestas de diferencia con el líder), «Quién lo hace» una vez. Portada con la consecuencia («1 de cada 4 veces; al líder, 5 de cada 10»), leyenda arriba de la cuadrícula, ejemplos en frases completas desde la clínica, un solo formato de números (4,9 · 1 135 · 25 %).
- **Semáforo (regla del Director):** tu cifra ÷ la del líder: Bien ≥ 80 %, Regular 40–80 %, Bajo < 40 %, «Sin datos» si el líder está en 0. En Maps se comparan las reseñas. El plan muestra siempre las 3 acciones de mayor impacto, aunque el área esté en «Bien».
- **Clínicas para el diagnóstico gratis (Implantes · Miraflores, setiembre, sin corridas):** NEODENTIS (2 %) y Clínica Virtual Dent (2 %), casi no nombradas; Clínica Dental Cano (17 %) y The Dental Clinic & GT Concept (15 %), nivel medio. Todas con web y WhatsApp visibles. Alternativas: Odontologists (10 %), Prosmile (2 %).

## Qué se decidió (y dónde quedó registrado)
- Regla del semáforo contra el líder (80 % / 40 %): `src/visible_ia/informes/semaforo.toml` y anexo del informe.
- Plan de acción: siempre 3 acciones por impacto: docstring de `_plan` en `contexto.py`.
- Libro de Reclamaciones publicado sin dirección del proveedor: comentario en `web/reclamaciones.html`.

## Problemas y cómo se resolvieron
- «Rangos que se cruzan» dejaba casi todo en «Bien» con 60 respuestas → regla de proporción del líder.
- El impacto de Doctoralia contaba respuestas y no porcentajes (salía «alto» con 100 % vs 100 %) → usa la misma proporción que el semáforo.

## Para la próxima sesión
- OK escrito del Director para publicar el PR #67 (antes, la migración que hace obligatoria `consent_version`).
- Libro de Reclamaciones: falta, según el reglamento, domicilio del proveedor, número correlativo y copia al correo (revisión legal).
- Ofrecer el diagnóstico gratis a las 4 clínicas elegidas.
