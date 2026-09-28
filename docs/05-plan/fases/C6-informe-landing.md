# Fase C6 · Informe gratis + landing → v1.0 "Vender"

**Objetivo:** generar en ≤ 10 minutos de trabajo el **informe gratis de diagnóstico** en PDF para una clínica prospecto, y publicar una landing que registre pedidos de informe.
- Con esto se empieza a vender el 05/10.

**Historias que cubre:** HU-14, HU-26
**Estado:** 🟡 en curso

## Tareas

### C6-T01 · Plantilla HTML del informe de diagnóstico
- **Estado:** ✅
- **Qué:** plantilla `informes/plantillas/diagnostico.html.j2` (A4 vertical, ≤ 4 páginas) con las 6 partes del PRD HU-14:
  1. Índice de la clínica frente a sus 3 competidores principales, con márgenes y una frase simple.
  2. Ejemplos reales de lo que respondió cada IA, citados y con fecha.
  3. Fuentes que usa la IA en su mercado.
  4. Brecha Maps vs IA.
  5. 3 recomendaciones (del checklist base: ficha de Google, Doctoralia, web/schema, según lo que falte).
  6. Nota de método: qué se midió, cuántas veces, la diferencia detectable y "no garantizamos un puesto #1".
     - **C-006 (Director, 26/09):** declarar que algunas respuestas de Google Modo IA muestran fichas de clínicas cuyo nombre no llega por SerpApi (corrida 1: 2 de 30), y que esas menciones no se cuentan.
- **Archivos probables:** `src/visible_ia/informes/plantillas/diagnostico.html.j2`, `src/visible_ia/informes/estilos.css`, `src/visible_ia/informes/contexto.py`
- **Criterios de aceptación:**
  - [ ] Se lee bien en el celular (letra ≥ 11 pt, gráficos de barras con su valor en texto).
  - [ ] Marca visible-ia configurable, preparada para la marca blanca de C10: logo y colores vienen de variables.
  - [ ] Sin datos de pacientes. Los nombres de profesionales solo aparecen si son el nombre del establecimiento.
- **Pruebas:** renderizar con un contexto de ejemplo y verificar que están las 6 secciones y que ninguna variable queda vacía.
- **Depende de:** C5-T04
- **Rama:** `feat/C6-T01-report-template`
- **Notas para Claude Code:**
  - Gráficos como SVG generado en Python o con barras en HTML/CSS. Nada de librerías de gráficos pesadas.
  - Español de Perú, tono claro y sin tecnicismos. El margen se explica como "entre X % y Y %".

### C6-T02 · PDF con Playwright + comando `informe diagnostico`
- **Estado:** ✅ (27/09: PDF real de 3 páginas, 89 KB, 4 s en Windows; Linux/Actions se verifica en C8)
- **Qué:**
  - `informes/pdf.py` convierte el HTML a PDF con Playwright (Chromium).
  - Comando `visible-ia informe diagnostico --clinica <id> --mercado <id> [--competidores a,b,c]`: por defecto, los 3 mejores del ranking que no son la clínica.
  - Guarda el PDF en `salida/` y lo sube a Supabase Storage. Registra el `informe`.
- **Archivos probables:** `src/visible_ia/informes/pdf.py`, `src/visible_ia/cli.py`, `tests/integration/test_pdf.py`
- **Criterios de aceptación:**
  - [ ] Los criterios de HU-14 del PRD §4 (≤ 4 páginas y las 6 partes).
  - [ ] Se genera en ≤ 1 minuto (PRD §6).
  - [ ] Funciona en Windows (la PC del Director) y en Linux (Actions).
- **Pruebas:** generar un PDF de ejemplo, verificar las páginas (con `pypdf`, solo en las pruebas) y el tamaño < 2 MB.
- **Depende de:** C6-T01
- **Rama:** `feat/C6-T02-pdf`
- **Notas para Claude Code:** documentar en el README el paso `uv run playwright install chromium`.

### C6-T03 · Landing con formulario de informe gratis (HU-26)
- **Estado:** ✅ (27/09: migración 0005 en dev y prod; formulario probado de punta a punta en la vista previa)
- **Qué:** completar `web/index.html`:
  - Explicación del servicio y ejemplo anonimizado del informe.
  - Formulario: nombre, clínica, rubro, distrito, contacto, consentimiento de contacto.
  - Inserta en `prospects` con la clave `anon`.
  - Migración `0005_prospects_insert_policy.sql` (el 0002 ya estaba usado): política RLS de **solo insertar** para `anon`.
  - Captura de `utm_*` de la URL.
- **Archivos probables:** `web/index.html`, `web/app.js`, `supabase/migrations/0002_prospects_insert_policy.sql`, `tests/rls/test_prospects_policy.py`
- **Criterios de aceptación:**
  - [ ] Los criterios de HU-26 del PRD §4: guarda la fuente (UTM) y el consentimiento, y avisa al operador. El aviso llega por C6-T04 (issue diario y el comando `visible-ia prospectos nuevos`).
  - [ ] Con la clave `anon` **no** se puede leer `prospects` ni ninguna otra tabla. Hay una prueba automática.
  - [ ] Sin consentimiento, el formulario no se envía.
- **Pruebas:** RLS (insert permitido, select denegado) y revisión manual en el celular.
- **Depende de:** C1-T06, C1-T03
- **Rama:** `feat/C6-T03-landing-form`
- **Notas para Claude Code:**
  - La clave `anon` es pública por diseño. Lo que protege es RLS.
  - Añadir una protección básica contra spam: un campo trampa oculto.

### C6-T04 · Aviso de prospectos nuevos
- **Estado:** ⚪
- **Qué:** comando `visible-ia prospectos nuevos` (lista los no vistos y los marca como vistos) y un paso en el job diario que, si hay prospectos nuevos, abre o actualiza un issue de GitHub "Prospectos nuevos (n)".
- **Archivos probables:** `src/visible_ia/prospectos.py`, `.github/workflows/diario.yml`, `tests/unit/test_prospectos.py`
- **Criterios de aceptación:**
  - [ ] El Director se entera de un pedido de informe en ≤ 24 h sin entrar a Supabase.
  - [ ] El issue no contiene datos de contacto, solo el conteo y el nombre de la clínica.
- **Pruebas:** unitarias con un cliente falso de GitHub.
- **Depende de:** C6-T03, C1-T05
- **Rama:** `feat/C6-T04-prospect-alerts`

### C6-T05 · Plan B: vender el 05/10 con informes semiautomáticos (solo si C1–C5 se atrasan)
- **Estado:** ⚪ (contingencia; decidido por el Director el 26/09)
- **Cuándo se activa:** en el **control del jueves 02/10 al final del día**. Si C5 (puntaje) no está completo, o si se ve que C6-T02 (PDF) no llegará al 04/10, se activa el nivel que corresponda. La decisión queda en la bitácora.
- **Qué:** preparar lo mínimo para que el **05/10** se puedan enviar los primeros informes gratis igual:
  - **Nivel 1 (C3–C5 listos; faltan C6-T01/T02):**
    - Corrida y puntaje por la CLI (`corrida lanzar`, `extraer`, `revisar`, `puntaje ranking/fuentes/brecha`).
    - El informe se arma **a mano** con una plantilla simple (HTML estático en `web/informe-manual/` o un documento), con las mismas 6 partes del PRD HU-14.
    - Meta: ≤ 30 minutos por informe.
  - **Nivel 2 (C3 no está listo):**
    - "Diagnóstico preliminar" con una **muestra manual** como la de la fase 1: 10 preguntas del mercado × 1 repetición en la app de ChatGPT y en Google Modo IA.
    - Registro en el formato de `registro.csv`, conteo con `scripts/comparar_api_vs_muestra.py` (adaptado a la lista de clínicas del mercado) e informe manual.
    - La nota de método dice claramente que es una muestra de 1 repetición, con un margen muy amplio.
- **Archivos probables:** `web/informe-manual/plantilla.html` (nivel 1) · `docs/06-lanzamiento/guia-informe-manual.md` (pasos para ambos niveles)
- **Criterios de aceptación:**
  - [ ] Existe una guía paso a paso para cada nivel, que el Director puede seguir sin ayuda.
  - [ ] El informe manual respeta el PRD: las 6 partes, sin datos de pacientes, sin "puesto #1" y con la nota de método honesta.
  - [ ] Si el Plan B no se activa, la guía queda igual como respaldo.
- **Pruebas:** el Director arma 1 informe de prueba con la guía del nivel que corresponda.
- **Depende de:** — (se prepara el 02/10 si se activa; no bloquea a C6-T01/T02, que siguen en paralelo)
- **Rama:** `docs/C6-T05-plan-b-informe-manual`
- **Notas para Claude Code:**
  - Nunca automatizar las apps de consumo para el nivel 2: la muestra la hace el Director a mano (ADR-002).
  - Al activar el Plan B, C6-T01/T02 siguen siendo prioridad para reemplazar los informes manuales cuanto antes.

## Demo de la fase (= demo de la v1.0)
- Desde un mercado real, el Director genera el informe gratis de una clínica real en ≤ 10 minutos y lo abre en su celular.
- Llena el formulario de la landing y ve el issue "Prospectos nuevos" al día siguiente.
- **Al aprobar la demo:** tag `v1.0`.
