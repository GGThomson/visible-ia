# Fase C4 · Extractor y revisión

**Objetivo:** convertir cada respuesta en la lista ordenada de clínicas mencionadas, asociadas a las del mercado, y en su lista de fuentes clasificadas.
- El operador puede corregir lo extraído.
- La calidad se mide de forma automática contra un conjunto etiquetado.

**Historias que cubre:** HU-07, HU-08, HU-09
**Estado:** 🟡 en curso

## Tareas

### C4-T01 · Extracción de menciones con gpt-5-nano
- **Estado:** ✅
- **Qué:** `extractor/llm.py`.
  - Envía el texto de la respuesta a `gpt-5-nano` con **salida estructurada** (JSON Schema): una lista de `{nombre_tal_cual, orden, es_establecimiento_o_profesional}`.
  - Devuelve las menciones en el orden en que aparecen, sin inventar nombres.
- **Archivos probables:** `src/visible_ia/extractor/llm.py`, `src/visible_ia/extractor/prompt.md`, `tests/unit/test_extractor_llm.py`
- **Criterios de aceptación:**
  - [ ] Solo devuelve nombres que aparecen **literalmente** en el texto. Hay una validación posterior que descarta lo que no esté en el texto.
  - [ ] Ignora los nombres de plataformas y fuentes (Doctoralia, Google Maps, Instagram) como si fueran clínicas.
  - [ ] Costo ≤ US$0.0005 por respuesta (se estima con los tokens).
- **Pruebas:** respuestas grabadas del LLM (fixture) + la validación de "literalmente en el texto". Una prueba `live` opcional.
- **Depende de:** C3-T04
- **Rama:** `feat/C4-T01-llm-extraction`
- **Notas para Claude Code:**
  - La instrucción al modelo vive en un archivo aparte (`prompt.md`), versionado; su versión se guarda con cada extracción.
  - Temperatura mínima o determinista si el modelo lo permite.
  - **Hallazgo de la corrida 1 (26/09, Google Modo IA):** cuando Google muestra fichas de clínicas, SerpApi **no incluye el nombre de la ficha** en el texto (quedan "Ubicación: …", "Enfoque: …"). El nombre solo viene en el texto de los enlaces (`snippet_links[].text`, p. ej. "Dental Pérez Yance"), dentro de `raw.text_blocks`. El extractor de Google debe leer también esos textos de enlace, en su orden de aparición. En `references` los enlaces son `google.com/searchviewer/...` (C4-T03).

### C4-T02 · Asociación con las clínicas del mercado
- **Estado:** ✅
- **Qué:** `extractor/matching.py`.
  - Para cada mención busca la clínica del mercado: primero una coincidencia exacta con un alias (sin tildes, en minúsculas, sin puntuación) y después `rapidfuzz` (`token_set_ratio`) con umbral configurable (por defecto 90).
  - Si no hay coincidencia, marca la mención como "nueva" (HU-09).
- **Archivos probables:** `src/visible_ia/extractor/matching.py`, `tests/unit/test_matching.py`
- **Criterios de aceptación:**
  - [ ] Casos reales de la muestra: "Perez Yance" = "Implantes Dental | Perez Yance / Clínicas Dentales Americadent"; "Dr. Enmanuel Teixeira" = "Mejor Clínica Dental en Miraflores - Implantes Dentales en miraflores - Enmanuel Teixeira"; "RenovaSmiles Perú" ≠ "Smiles Peru" (falso positivo que ya ocurrió en la fase 1).
  - [ ] Una mención no se asocia a dos clínicas: si empatan, se marca para revisión.
- **Pruebas:** tabla de casos (entrada → clínica esperada o "nueva" o "revisar").
- **Depende de:** C2-T04, C4-T01
- **Rama:** `feat/C4-T02-matching`

### C4-T03 · Clasificación de fuentes
- **Estado:** ⚪
- **Qué:** `extractor/fuentes.py`, que clasifica cada dominio en: ficha de Google, Doctoralia, web propia, redes, directorio/ranking, prensa u otra.
  - Usa una tabla de dominios conocidos (en `data/`).
  - Marca "web propia" si coincide con el `web` de una clínica del mercado.
- **Archivos probables:** `src/visible_ia/extractor/fuentes.py`, `data/dominios.csv`, `tests/unit/test_fuentes.py`
- **Criterios de aceptación:**
  - [ ] Los dominios de la muestra de la fase 1 quedan bien clasificados (doctoralia.pe, instagram.com, facebook.com, elcomercio.pe, fresha.com, whatclinic.com, dentum.com.pe, webs de clínicas).
- **Pruebas:** tabla de casos.
- **Depende de:** C3-T04
- **Rama:** `feat/C4-T03-source-types`

### C4-T04 · Comando de extracción + revisión desde la CLI (HU-07, HU-08, HU-09)
- **Estado:** ⚪
- **Qué:**
  - `visible-ia extraer <corrida_id>`: extrae, asocia y clasifica todas las respuestas pendientes.
  - `visible-ia revisar <corrida_id>` muestra, por respuesta, el texto resumido y las menciones, y permite:
    - asociar una mención a otra clínica;
    - marcarla como "nueva" y crear la clínica en el mercado;
    - descartarla;
    - unir dos menciones.
  - Al terminar, la corrida pasa a `revisada`.
  - Además: `visible-ia revisar exportar <id>` / `importar <archivo.csv>` para revisar en Excel si es más cómodo.
- **Archivos probables:** `src/visible_ia/extractor/revision.py`, `src/visible_ia/cli.py`, `tests/unit/test_revision.py`
- **Criterios de aceptación:**
  - [ ] Los criterios de HU-07 y HU-08 del PRD §4 (corregir recalcula el puntaje; la corrección queda marcada como `corregida`).
  - [ ] Lista de "clínicas nuevas" del mercado con su n.º de apariciones (HU-09).
- **Pruebas:** revisión simulada: aplicar un CSV de correcciones y verificar los estados.
- **Depende de:** C4-T02, C4-T03
- **Rama:** `feat/C4-T04-review-cli`
- **Notas para Claude Code:** en la terminal, usar `rich` para las tablas. Es la única dependencia nueva permitida en esta tarea.

### C4-T05 · Conjunto de evaluación y prueba de calidad (PRD §5.3)
- **Estado:** ⚪
- **Qué:**
  - Armar `data/eval/extractor-gold.jsonl` con ≥ 60 respuestas y sus menciones correctas:
    - las 31 de la muestra del 26/09 (importadas en C3-T05);
    - las 20 de la API de Gemini (`registro-api.csv`);
    - respuestas de la primera corrida real.
  - Claude Code propone las etiquetas y **el Director las confirma o corrige** (tarea del Director).
  - Prueba `tests/eval/test_extractor_quality.py`, que calcula precisión, exhaustividad y asociación.
- **Archivos probables:** `data/eval/extractor-gold.jsonl`, `tests/eval/test_extractor_quality.py`, `scripts/etiquetar.py` (ayuda de la CLI)
- **Criterios de aceptación:**
  - [ ] Metas del PRD §5.3: precisión ≥ 95 %, exhaustividad ≥ 90 %, asociación ≥ 95 %, dominios ≥ 95 %. Si no se cumplen, la prueba falla.
  - [ ] La prueba corre en la CI con las **salidas del LLM grabadas** (sin costo). Una versión `live` se ejecuta a mano al cambiar `prompt.md`.
- **Pruebas:** la propia evaluación.
- **Depende de:** C4-T04 y la tarea del Director (etiquetado)
- **Rama:** `feat/C4-T05-extractor-eval`
- **Notas para Claude Code:** las respuestas de la fase 1 contienen nombres de médicos. Solo se usan para evaluar y no salen del repositorio privado.

## Demo de la fase
- El Director extrae la corrida real y revisa 3 respuestas en la CLI.
- Corrige una mención, ve la lista de "clínicas nuevas" y ve la prueba de calidad en verde en la CI.
