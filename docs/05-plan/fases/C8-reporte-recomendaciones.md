# Fase C8 · Corrida mensual automática, reporte mensual y recomendaciones

**Objetivo:** cada mes, sin intervención salvo la revisión:
- corren los mercados activos;
- se genera el reporte mensual de cada sede, con la regla del ADR-003;
- la clínica tiene un checklist priorizado y su schema JSON-LD.

**Historias que cubre:** HU-15, HU-17, HU-18
**Estado:** ⚪ pendiente
**Nota:** las tareas se refinan al empezar la fase, sin cambiar su alcance.

## Tareas

### C8-T01 · Workflow de corrida mensual
- **Estado:** ⚪
- **Qué:** `corrida-mensual.yml` (cron el día 1 a las 06:00 hora de Lima, más ejecución manual). Lanza las corridas de los mercados activos en **prod**, con el tope de presupuesto, y extrae las respuestas. Deja un issue "Revisar corridas de <mes>".
- **Criterios de aceptación:**
  - [ ] Respeta el presupuesto: si se superaría, no corre y lo dice en el issue.
  - [ ] Si falla a mitad, se puede reanudar con la ejecución manual.
- **Pruebas:** ejecución manual en dev con 1 mercado.
- **Depende de:** C3, C4 y C5 completas
- **Rama:** `feat/C8-T01-monthly-workflow`

### C8-T02 · Reporte mensual PDF (HU-15)
- **Estado:** ⚪
- **Qué:** plantilla `mensual.html.j2` y el comando `visible-ia informe mensual --sede <id> --mes <aaaa-mm>`, con:
  - evolución del índice;
  - cambio frente al mes anterior (ADR-003);
  - ventana de 3 meses;
  - competidores;
  - fuentes;
  - tareas del checklist (hechas y pendientes);
  - calibración con la app (PRD §5.4).
- **Criterios de aceptación:**
  - [ ] Los criterios de HU-15 del PRD.
  - [ ] Muestra la diferencia detectable del periodo.
  - [ ] Advierte si la calibración con ChatGPT bajó de 50 % dos meses seguidos (§5.4).
- **Pruebas:** renderizado con 1, 2 y 3 meses de datos.
- **Depende de:** C8-T01
- **Rama:** `feat/C8-T02-monthly-report`

### C8-T03 · Checklist priorizado (HU-17)
- **Estado:** ⚪
- **Qué:**
  - Catálogo de tareas en `data/checklist.yaml`, en este orden: ficha de Google → Doctoralia → web con schema → redes → Bing Places. Cada tarea tiene su condición.
  - Prioriza según lo que le falta a la sede y según las fuentes que más cita su mercado.
  - La clínica marca las tareas como hechas desde el panel (migración con la política RLS de actualización de `tasks`).
- **Criterios de aceptación:**
  - [ ] Los criterios de HU-17 del PRD.
  - [ ] Ninguna tarea recomienda prácticas prohibidas por Google (p. ej., palabras clave en el nombre de la ficha).
- **Pruebas:** casos por perfil de clínica.
- **Depende de:** C7-T04
- **Rama:** `feat/C8-T03-checklist`

### C8-T04 · Generador de schema JSON-LD (HU-18)
- **Estado:** ⚪
- **Qué:** comando y botón en el panel que generan el JSON-LD `Dentist`/`MedicalClinic` de la sede (nombre, dirección, teléfono, horario, `sameAs` hacia la ficha de Google, Doctoralia e Instagram), listo para copiar.
- **Criterios de aceptación:**
  - [ ] El JSON es válido según schema.org. Hay una prueba con un validador local de estructura.
- **Pruebas:** unitarias.
- **Depende de:** C8-T03
- **Rama:** `feat/C8-T04-jsonld`

## Demo de la fase
- El Director ejecuta la corrida mensual a mano en dev, revisa, genera el reporte mensual de una sede de prueba, marca una tarea como hecha en el panel y copia su JSON-LD.
