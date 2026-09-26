---
description: Registra un cambio, idea o bug en cualquier momento y evalúa su impacto sin perder el hilo.
argument-hint: "<descripción del cambio>"
---

Cambio propuesto por el Director: $ARGUMENTS

1. Añádelo a `memoria/cambios-pendientes.md` con el siguiente ID `C-XXX`, la fecha de hoy y el tipo (🐛 ✨ 🔁 💡 ❓).
2. Evalúa el impacto leyendo PRD, arquitectura y plan:
   - **Bajo**: propone una tarea nueva en la fase adecuada.
   - **Medio**: lista las tareas afectadas y el esfuerzo estimado.
   - **Alto**: cambia la especificación o la arquitectura, así que recomienda `/decision` y, si es un proyecto freelance o de empresa, avisa que puede afectar costo o plazo.
3. Presenta al Director las opciones: **hacerlo ahora**, **agregarlo al plan** (en qué fase), **dejarlo para la v2** o **descartarlo**.
4. Aplica lo que decida: crea la tarea en el archivo de fase o mueve la fila a "Clasificados" con su destino.
5. Si se estaba trabajando en otra tarea, recuerda en qué punto quedó y vuelve a ella.
6. Commit: `docs: registra cambio C-XXX`.
