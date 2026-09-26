# AGENTS.md — Reglas para todas las IAs de este proyecto

Este archivo lo leen Claude Code, Gemini/Antigravity, Cursor y cualquier agente compatible. Es la **constitución** del proyecto: mantenlo corto y estable.

## Idioma
- Responde y documenta en **español**. El código, los nombres de variables y los commits van en inglés salvo que el proyecto indique otra cosa en `docs/03-especificacion/prd.md`.

## Roles del equipo
- **Director (humano)**: decide. Ninguna decisión de alcance, arquitectura, costo o seguridad se toma sin su aprobación explícita.
- **Planificadores (Claude chat, Gemini)**: proponen, investigan y revisan críticamente.
- **Ejecutor (Claude Code)**: redacta documentos y construye código siguiendo el plan aprobado.

## Fuente de verdad
1. `memoria/ESTADO.md` indica la fase actual, la tarea actual y los próximos pasos. **Léelo al empezar.**
2. Los documentos de `docs/` son la especificación. Si el código y la especificación se contradicen, **detente y pregunta**; no "arregles" la especificación por tu cuenta.
3. Las decisiones tomadas están en `docs/decisiones/`. No las reabras sin un motivo nuevo.
4. Nada importante vive solo en el chat: si se decidió, se escribe.

## Reglas de trabajo
- **Una tarea a la vez.** Cada tarea tiene su ID (p. ej. `F2-T03`) en `docs/05-plan/fases/`.
- **Git**:
  - Nunca trabajes directo en `main`. Crea ramas `tipo/ID-descripcion-corta` (p. ej. `feat/F2-T03-login`).
  - Usa Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`. Incluye el ID de la tarea.
  - Commits pequeños y frecuentes. Nunca subas secretos (`.env`, claves, tokens).
- **Calidad**: escribe o actualiza las pruebas de cada tarea y ejecútalas antes de darla por terminada. Cumple la "Definición de Terminado" de `docs/05-plan/roadmap.md`.
- **Cambios de alcance**: si el director pide algo nuevo durante una tarea, regístralo en `memoria/cambios-pendientes.md` y termina primero la tarea actual, salvo que sea urgente.
- **Incertidumbre**: si una instrucción es ambigua o una decisión es difícil de revertir, pregunta antes de actuar.

## Mantener la memoria sana
- `memoria/ESTADO.md` debe caber en una pantalla (≈ 60 líneas). Mueve el detalle a la bitácora.
- Al cerrar una sesión: actualiza `ESTADO.md`, añade una entrada en `memoria/bitacora/`, haz commit y push, y **fusiona `memoria/` y `docs/` a `main`** aunque la fase siga en curso, para que los Proyectos de claude.ai lean la memoria actual. El código sin terminar se queda en su rama. Detalle en `/cerrar-sesion`.
- Al cerrar una fase: resume la fase en `memoria/bitacora/` y crea un tag de Git `fase-N-completa`.

## Mapa rápido
- Tipo y ruta del proyecto: `docs/00-inicio/brief.md`
- Requisitos: `docs/03-especificacion/prd.md`
- Arquitectura: `docs/04-arquitectura/arquitectura.md`
- Plan: `docs/05-plan/roadmap.md` y `docs/05-plan/fases/`
- Pendientes: `memoria/cambios-pendientes.md`
