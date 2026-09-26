---
description: Convierte PRD y arquitectura en roadmap, fases y tareas ejecutables por Claude Code.
---

1. Lee `docs/03-especificacion/prd.md`, `docs/04-arquitectura/arquitectura.md`, `docs/decisiones/` y `memoria/cambios-pendientes.md`.
2. Verifica que el PRD esté **aprobado**. Si no, detente y avisa.
3. Diseña las fases de construcción en `docs/05-plan/roadmap.md`:
   - F1 siempre es la base: estructura, dependencias, `.env.example`, pruebas configuradas, CI en `.github/workflows/`, README técnico y despliegue mínimo.
   - Cada fase siguiente entrega **algo visible y probable** y cubre historias concretas.
4. Por cada fase crea `docs/05-plan/fases/F<n>-<nombre>.md` desde `_plantilla-fase.md`. Cada tarea debe ser pequeña (idealmente menos de 1–2 horas de trabajo de Claude Code), con criterios de aceptación, pruebas, dependencias y "Notas para Claude Code" suficientes para no tener que preguntar.
5. Revisa el plan con el Director. Sugiere enviarlo a Gemini como revisor crítico (`/contexto revisión del plan`).
6. Con la aprobación: actualiza ESTADO (fase 4 ✅, fase 5 🟡, tarea actual = F1-T01), haz commit `docs: plan de construcción aprobado` y el tag `plan-aprobado`.
7. (Opcional, si el Director quiere usar GitHub Issues) Ofrece crear un Issue por tarea con `gh issue create`, explicando antes qué hace el comando.
