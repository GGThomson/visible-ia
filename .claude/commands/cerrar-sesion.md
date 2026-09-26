---
description: Cierra la sesión de trabajo. Actualiza ESTADO y bitácora y guarda todo en GitHub.
---

Haz esto siempre al final de cada sesión:

1. Crea `memoria/bitacora/<AAAA-MM-DD>-<titulo>.md` desde `_plantilla-sesion.md`. Si ya existe una del mismo día, añade una sección nueva. Incluye los commits de la sesión (`git log --oneline` desde el último cierre).
2. Actualiza `memoria/ESTADO.md`: fecha, fase, tarea actual, avance, próximos 3 pasos, bloqueos y decisiones recientes (solo las últimas 5; las anteriores ya están en los ADRs). **Mantenlo en menos de 60 líneas.**
3. Si cambió algo relevante para los planificadores (fase, decisiones, stack), actualiza también `memoria/contexto-rapido.md`.
4. Git en la rama de trabajo, explicando cada paso:
   - Si estás en una rama de tarea sin terminar: `git add -A && git commit -m "wip(<ID>): <estado>"` y `git push`.
   - Guarda la memoria: `git add memoria docs && git commit -m "docs: cierre de sesión <fecha>"` y `git push`.
5. **Fusiona `memoria/` y `docs/` a `main` y súbelos, aunque la fase siga en curso** (decisión del Director, 26/09/2026). Explica cada paso:
   - `git checkout main && git pull --ff-only origin main`.
   - Por cada rama con cambios de hoy en `memoria/` o `docs/`:
     - **Rama solo de documentación** (`docs/...`): `git merge --no-ff <rama> -m "Merge <rama>: cierre de sesión <fecha>"`.
     - **Rama con código sin terminar** (`feat/`, `fix/`, `chore/`…): trae **solo** la documentación, nunca el código a medio hacer: `git checkout <rama> -- docs memoria` y `git commit -m "docs: sincroniza memoria y docs desde <rama> (<fecha>)"`. Si una rama trae una versión más vieja de un archivo que `main` ya tiene actualizado (p. ej. `ESTADO.md`), trae solo las rutas nuevas y avisa.
   - `git push origin main`.
   - Vuelve a cada rama de trabajo y ponla al día con `git merge main` (si hay conflicto en `memoria/` o `docs/`, gana la versión de `main`) y `git push`.
   - Si aparece un conflicto que no sea de documentación, **detente y pregunta** al Director.
6. Confirma con `git status` que no quedó nada sin guardar y que `main` está al día con `origin/main`. Dile al Director en 3 líneas: qué se hizo, dónde quedó y con qué empezar la próxima vez.
