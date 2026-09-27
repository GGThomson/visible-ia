# Fase C5 · Puntaje de presencia

**Objetivo:** calcular, para una corrida revisada, el índice de cada clínica por superficie y combinado, con su margen de Wilson, posición media y cuota de menciones.
- Además: el ranking del mercado, el top de fuentes y la brecha Maps vs IA.
- Aplica la regla de cambio del ADR-003.

**Historias que cubre:** HU-10, HU-11, HU-12, HU-13
**Estado:** 🟡 en curso

## Tareas

### C5-T01 · Estadística: Wilson y prueba de 2 proporciones
- **Estado:** ✅
- **Qué:** `puntaje/estadistica.py`, en Python puro, con:
  - `wilson(k, n, z=1.96) -> (bajo, alto)`;
  - `dos_proporciones(k1, n1, k2, n2) -> (z, p_valor)` (bilateral);
  - `diferencia_detectable(p, n)`, que calcula la subida mínima que se puede informar, para mostrarla en los informes.
- **Archivos probables:** `src/visible_ia/puntaje/estadistica.py`, `tests/unit/test_estadistica.py`
- **Criterios de aceptación:**
  - [ ] Reproduce la tabla del PRD §5.5: p. ej., 30 % con n = 30 → [17 %, 48 %]; diferencia detectable ≈ 23 puntos (2 proporciones) con n = 30.
  - [ ] Casos límite: k = 0, k = n, n = 0 (devuelve "sin datos").
- **Pruebas:** tabla de casos contra valores conocidos (verificados con otra fuente).
- **Depende de:** C1-T01
- **Rama:** `feat/C5-T01-statistics`
- **Notas para Claude Code:** no agregar `scipy` ni `statsmodels`. La CDF normal se calcula con `math.erf`.

### C5-T02 · Índice mensual del mercado (HU-10, HU-11)
- **Estado:** ✅
- **Qué:** `puntaje/indice.py` y el comando `visible-ia puntaje calcular <corrida_id>`.
  - Por clínica y superficie calcula: respuestas, apariciones, índice, límites de Wilson, posición media y cuota de menciones.
  - Calcula también el **combinado** (promedio de ChatGPT y Google).
  - Guarda en `monthly_scores`.
  - `visible-ia puntaje ranking <mercado> [--mes]` muestra el ranking.
- **Archivos probables:** `src/visible_ia/puntaje/indice.py`, `src/visible_ia/cli.py`, `tests/unit/test_indice.py`
- **Criterios de aceptación:**
  - [ ] Los criterios de HU-10/11 del PRD §4 y la definición del §5.2.
  - [ ] Solo cuenta las respuestas de tipo API. Las manuales se excluyen (§5.2).
  - [ ] Solo se calcula sobre corridas `revisada`. Si no, da un error claro.
  - [ ] Una clínica con 0 apariciones aparece en el ranking con índice 0 si está en la lista del mercado.
- **Pruebas:** corrida sintética con resultados conocidos → índices exactos.
- **Depende de:** C5-T01, C4-T04
- **Rama:** `feat/C5-T02-monthly-index`

### C5-T03 · Cambio mensual y ventana de 3 meses (ADR-003)
- **Estado:** ⚪
- **Qué:** al calcular un mes:
  - Compara el **combinado** con el mes anterior usando la prueba de 2 proporciones (α = 0.05): "sube", "baja" o "sin cambio claro".
  - Calcula el índice de la **ventana móvil de 3 meses**, con su intervalo.
  - Si no hay meses previos: "primer mes".
- **Archivos probables:** `src/visible_ia/puntaje/indice.py`, `tests/unit/test_cambio.py`
- **Criterios de aceptación:**
  - [ ] Aplica la regla del ADR-003. La regla de "intervalos sin solaparse" no se usa.
  - [ ] Guarda la diferencia detectable del periodo, para que los informes la muestren.
- **Pruebas:** series sintéticas: subida clara, ruido y bajada; ventana con 1, 2 y 3 meses de datos.
- **Depende de:** C5-T02
- **Rama:** `feat/C5-T03-change-rule`

### C5-T04 · Fuentes del mercado y brecha Maps vs IA (HU-12, HU-13)
- **Estado:** ⚪
- **Qué:**
  - `visible-ia puntaje fuentes <mercado>`: top de dominios por tipo, con el % de respuestas que los citan.
  - `visible-ia puntaje brecha <mercado>`: por clínica, sus ★, n.º de reseñas e índice combinado.
  - Marca la **brecha** cuando ★ ≥ 4.5, reseñas ≥ 100 e índice ≤ 10 % (criterio de H4, fase 1). Los umbrales son configurables.
- **Archivos probables:** `src/visible_ia/puntaje/fuentes.py`, `src/visible_ia/puntaje/brecha.py`, `tests/unit/test_brecha.py`
- **Criterios de aceptación:**
  - [ ] Los criterios de HU-12 del PRD §4.
  - [ ] La brecha muestra la fecha del dato de ★ y reseñas.
- **Pruebas:** datos sintéticos.
- **Depende de:** C5-T02, C4-T03
- **Rama:** `feat/C5-T04-sources-gap`

## Demo de la fase
- El Director calcula el puntaje de la corrida real y ve el ranking de "Implantología · Miraflores" con sus márgenes.
- Ve el top de fuentes y qué clínicas tienen brecha Maps vs IA.
