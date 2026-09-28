# Guía: generar un informe gratis de diagnóstico

Para el Director. Tres caminos, de más a menos automático. **Hoy (27/09) se usa el camino A**: C1–C6 están listos, así que el Plan B (caminos B y C) queda solo como respaldo.

---

## A. Informe automático (≈ 10 minutos)

Antes de empezar, abre PowerShell en la carpeta del proyecto y activa el entorno: `.venv\Scripts\activate` (verás `(visible-ia)` al inicio de la línea). Todos los comandos de esta guía se escriben así, sin `uv run`.

Una sola vez en tu PC: `playwright install chromium` (navegador para los PDF).

1. **¿Ya hay una corrida revisada del mercado este mes?**
   `visible-ia puntaje ranking <mercado> --env prod` → si muestra el mes actual, salta al paso 5.
2. **Lanza la corrida** (≈ US$1.2 y 30 créditos de SerpApi; el motor muestra la estimación y se detiene si supera el tope):
   `visible-ia corrida lanzar --mercado <id> --env prod`
   Si se corta: `visible-ia corrida reanudar <corrida> --env prod`.
3. **Extrae las clínicas** (≈ US$0.01): `visible-ia extraer <corrida> --env prod`.
4. **Revisa y cierra**: `visible-ia revisar corrida <corrida> --env prod` (solo muestra lo dudoso) y luego `visible-ia revisar cerrar <corrida> --env prod`.
   Si la clínica prospecto no está en la lista del mercado, agrégala antes con `clinicas importar` (o `revisar corrida` → `n <mención>`), y vuelve a asociar: `visible-ia revisar reasociar <corrida> --env prod`.
5. **Calcula el puntaje** (sin costo): `visible-ia puntaje calcular <corrida> --env prod`.
6. **Genera el informe**: `visible-ia informe diagnostico --clinica <id> --mercado <id> --env prod`.
   Por defecto compara con los 3 mejores del ranking; para elegir otros: `--competidores 12,15,20`.
   El PDF queda en `salida/` y en el bucket privado `informes`.
7. **Revísalo antes de enviarlo** (2 minutos): nombres bien escritos, ningún dato de pacientes, y que las recomendaciones tengan sentido para esa clínica. Envíalo por WhatsApp o correo.

Para buscar ids: `visible-ia mercado listar --env prod` y `visible-ia clinicas listar --mercado <id> --env prod`.

---

## B. Plan B · nivel 1: informe armado a mano con los datos del motor (≈ 30 minutos)

Solo si el PDF automático falla (por ejemplo, Chromium no abre) y hay que enviar el informe igual.

1. Pasos 1–5 del camino A.
2. Copia en un documento (Google Docs o Word) las **6 partes**, con los datos de:
   - `puntaje ranking` (parte 1: índice de la clínica y de sus 3 competidores, con su rango "entre X % y Y %");
   - 2 respuestas reales (parte 2): `revisar exportar <corrida>` abre un CSV con las menciones y un extracto; cita la pregunta y la fecha;
   - `puntaje fuentes` (parte 3) y `puntaje brecha` (parte 4);
   - 3 recomendaciones (parte 5) del checklist `src/visible_ia/informes/recomendaciones.toml`;
   - la nota de método (parte 6): 10 preguntas × 3 veces × 2 IA = 60 respuestas, la diferencia detectable y **"no garantizamos un puesto #1"**.
3. Otra opción: el HTML del informe también queda en `salida/` junto al PDF; se puede abrir en el navegador e imprimir a PDF.

---

## C. Plan B · nivel 2: diagnóstico preliminar con una muestra manual (≈ 60 minutos)

Solo si el motor no estuviera disponible.

1. Haz las 10 preguntas del mercado (`visible-ia mercado preguntas <id> --env prod`) **una vez** en la app de ChatGPT y en Google Modo IA, en una ventana de incógnito. **Nunca automatices las apps** (ADR-002): se hace a mano.
2. Anota cada respuesta en el formato de `docs/01-descubrimiento/prueba-fuentes/registro.csv` y cárgalas con `visible-ia muestra importar <archivo.csv> --env prod`.
3. Arma el informe como en B, contando a mano en cuántas de las 20 respuestas aparece cada clínica.
4. En la nota de método di claramente: **"muestra preliminar de 1 repetición por pregunta; el margen es muy amplio"**.

---

## Reglas que valen para los tres caminos (PRD HU-14)
- Las 6 partes, en ≤ 4 páginas.
- Sin datos de pacientes. Nombres de profesionales solo si son el nombre del establecimiento.
- Sin afirmaciones sin fuente, sin prometer un "puesto #1".
- Si alguna respuesta de Google mostró fichas sin nombre, decirlo en la nota de método (C-006).
