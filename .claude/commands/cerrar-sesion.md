---
description: Cierra la sesión de trabajo. Actualiza ESTADO y bitácora y guarda todo en GitHub.
---

Haz esto siempre al final de cada sesión:

1. Crea `memoria/bitacora/<AAAA-MM-DD>-<titulo>.md` desde `_plantilla-sesion.md`. Si ya existe una del mismo día, añade una sección nueva. Incluye los commits de la sesión (`git log --oneline` desde el último cierre).
2. Actualiza `memoria/ESTADO.md`: fecha, fase, tarea actual, avance, próximos 3 pasos, bloqueos y decisiones recientes (solo las últimas 5; las anteriores ya están en los ADRs). **Mantenlo en menos de 60 líneas.**
3. Si cambió algo relevante para los planificadores (fase, decisiones, stack), actualiza también `memoria/contexto-rapido.md`.
4. Git, explicando cada paso:
   - Si estás en una rama de tarea sin terminar: `git add -A && git commit -m "wip(<ID>): <estado>"` y `git push`.
   - Guarda la memoria: `git add memoria docs && git commit -m "docs: cierre de sesión <fecha>"` y `git push`.
5. Confirma con `git status` que no quedó nada sin guardar y dile al Director en 3 líneas: qué se hizo, dónde quedó y con qué empezar la próxima vez.
