# Fase C2 · Mercados, preguntas y clínicas

**Objetivo:** el operador puede crear un mercado (rubro + distrito) con sus 10 preguntas generadas desde las plantillas aprobadas, importar la lista de clínicas desde un CSV y registrar alias.
**Historias que cubre:** HU-01, HU-02, HU-03
**Estado:** 🟡 en curso

## Tareas

### C2-T01 · Cargar las 40 plantillas aprobadas
- **Estado:** ✅ (26/09) cargadas en dev; en prod las carga el Director (`visible-ia plantillas cargar --env prod`) antes de la primera corrida real
- **Qué:**
  - Convertir `docs/03-especificacion/plantillas-preguntas.md` en `data/plantillas-preguntas.csv` con las columnas `id,rubro,forma,texto,origen`.
  - Comando `visible-ia plantillas cargar`, que las inserta o actualiza en `templates` con `version = 1`.
- **Archivos probables:** `data/plantillas-preguntas.csv`, `src/visible_ia/mercados/plantillas.py`, `tests/unit/test_plantillas.py`
- **Criterios de aceptación:**
  - [ ] Hay 40 plantillas, 10 por rubro, y todas contienen `{d}` una sola vez.
  - [ ] Cargar dos veces no duplica filas.
- **Pruebas:** leer el CSV y validar la cantidad, los rubros, las formas M/R/C/P y el `{d}`.
- **Depende de:** C1-T03
- **Rama:** `feat/C2-T01-templates`
- **Notas para Claude Code:**
  - El texto se copia **exactamente** del documento aprobado. No "mejorar" la redacción: el PRD está congelado.

### C2-T02 · Crear mercado y generar sus preguntas (HU-01)
- **Estado:** ✅ (26/09)
- **Qué:** comando `visible-ia mercado crear --rubro IMP --distrito Miraflores`.
  - Crea el mercado y sus 10 preguntas, reemplazando `{d}`.
  - `visible-ia mercado preguntas <id>` las lista.
  - `visible-ia mercado editar-pregunta` crea una **nueva versión** del banco si el mercado ya tiene corridas.
- **Archivos probables:** `src/visible_ia/mercados/mercado.py`, `src/visible_ia/cli.py`, `tests/unit/test_mercado.py`, `tests/integration/test_mercado_db.py`
- **Criterios de aceptación:**
  - [ ] Los criterios de HU-01 del PRD §4 (se generan las 10 preguntas; editar crea una versión nueva si hay corridas).
  - [ ] Distritos válidos: `Miraflores`, `San Isidro`, `Surco`. Cualquier otro da un error claro.
  - [ ] No se puede crear dos veces el mismo mercado.
- **Pruebas:** unitarias de la sustitución y del versionado; integración contra la base de datos dev.
- **Depende de:** C2-T01
- **Rama:** `feat/C2-T02-create-market`

### C2-T03 · Importar clínicas desde CSV (HU-02)
- **Estado:** ✅ (26/09)
- **Qué:** comando `visible-ia clinicas importar <archivo.csv> --mercado <id>`.
  - Columnas mínimas: `nombre,distrito,maps_url`.
  - Columnas opcionales: `direccion,rating,resenas,web,instagram`.
  - Crea o actualiza las clínicas (por `maps_url`) y las asocia al mercado.
  - Informa las filas con errores sin detener la importación.
  - Incluir `data/ejemplos/clinicas-ejemplo.csv` con 5 filas ficticias.
- **Archivos probables:** `src/visible_ia/mercados/clinicas.py`, `data/ejemplos/clinicas-ejemplo.csv`, `tests/unit/test_import_clinicas.py`
- **Criterios de aceptación:**
  - [ ] Los criterios de HU-02 del PRD §4.
  - [ ] Guarda la **fecha del dato** de ★ y reseñas (para la brecha Maps vs IA de C5).
  - [ ] Una clínica puede estar en varios mercados (p. ej., implantología y estética dental).
- **Pruebas:** CSV con filas buenas y malas (columna faltante, rating no numérico).
- **Depende de:** C2-T02
- **Rama:** `feat/C2-T03-import-clinics`
- **Notas para Claude Code:**
  - Nada de scraping de Google Maps. El CSV lo arma el Director a mano.
  - Aceptar el separador `,` y `;` (Excel en español guarda con `;`) y la codificación UTF-8 con o sin BOM.

### C2-T04 · Alias de clínicas (HU-03)
- **Estado:** ⚪
- **Qué:**
  - `visible-ia clinicas alias agregar <clinica_id> "<alias>"`, `... listar` y `... quitar`.
  - Al importar, se crea automáticamente un alias con el nombre corto: el texto antes de `|`, ` - ` o `(`. Ejemplo: "Implantes Dental | Perez Yance / Clínicas Dentales Americadent" → alias "Implantes Dental", "Perez Yance" y "Americadent".
- **Archivos probables:** `src/visible_ia/mercados/alias.py`, `tests/unit/test_alias.py`
- **Criterios de aceptación:**
  - [ ] Los criterios de HU-03 del PRD §4.
  - [ ] Los alias genéricos que coinciden con palabras comunes del rubro ("Clínica Dental", "Implantes Dentales", "Dermatología") **no** se crean automáticamente. Hay una lista de exclusión por rubro en el código.
- **Pruebas:** casos reales de la muestra del 26/09 (Perez Yance/Americadent, "Mejor Clínica Dental en Miraflores - … Enmanuel Teixeira").
- **Depende de:** C2-T03
- **Rama:** `feat/C2-T04-aliases`

## Demo de la fase
- El Director crea el mercado "Implantología · Miraflores", ve sus 10 preguntas, importa un CSV con 10 clínicas reales y agrega el alias "Americadent" a Perez Yance.
