---
description: Ejecuta la próxima tarea del plan (rama, código, pruebas, commit, PR).
argument-hint: "[ID de tarea, opcional, p. ej. F2-T03]"
---

1. Lee `memoria/ESTADO.md`. La tarea es $ARGUMENTS o la **tarea actual** del ESTADO. Abre su archivo en `docs/05-plan/fases/`.
2. Verifica que las dependencias estén ✅. Si no, avisa y propón el orden correcto.
3. Revisa `memoria/cambios-pendientes.md`: si hay algo sin clasificar que afecte esta tarea, avisa antes de empezar.
4. Git (explica cada comando en una línea):
   - `git checkout main && git pull`
   - `git checkout -b feat/<ID>-<descripcion-corta>` (usa `fix/` para bugs)
5. Para tareas grandes, muestra primero un plan breve de los archivos a tocar.
6. Implementa la tarea respetando PRD, arquitectura y ADRs. Si algo contradice la especificación, **detente y pregunta**.
7. Escribe o actualiza las pruebas y ejecútalas. No declares la tarea terminada con pruebas fallando.
8. Revisa la Definición de Terminado del roadmap.
9. Commits con Conventional Commits que incluyan el ID, p. ej. `feat(F2-T03): formulario de login`.
10. `git push -u origin <rama>` y, si hay GitHub, abre el PR con `gh pr create` usando la plantilla. Explica al Director cómo revisarlo y fusionarlo (o hazlo tú si él lo pide).
11. Marca la tarea ✅ en su archivo de fase, actualiza "tarea actual" y "próximos 3 pasos" en ESTADO.
12. Si era la última tarea de la fase: prepara la demo y cierra la fase según la Definición de Terminado de fase.
13. Pregunta: "¿Sigo con la siguiente tarea o cerramos la sesión?"
