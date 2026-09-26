---
description: Integra en la memoria lo acordado con Gemini o Claude web (pegar sus actas).
argument-hint: "<pega aquí las actas o respuestas>"
---

Contenido de la reunión de planificación:

$ARGUMENTS

1. Si el contenido viene vacío, pídele al Director que pegue las actas o las respuestas.
2. Crea `memoria/actas/<AAAA-MM-DD>-<tema>.md` desde `_plantilla-acta.md`. Compara las propuestas en la tabla y señala coincidencias y desacuerdos entre las IAs.
3. Pregunta al Director **qué decide** en cada punto abierto. No decidas por él.
4. Aplica sus decisiones:
   - Decisión importante → crea o actualiza el ADR (flujo `/decision`).
   - Cambios de alcance → `memoria/cambios-pendientes.md`.
   - Tareas → el archivo de la fase correspondiente.
   - Documentos afectados → actualízalos.
5. Actualiza ESTADO (decisiones recientes, bloqueos resueltos, próximos pasos).
6. Commit: `docs: acta <tema>`.
