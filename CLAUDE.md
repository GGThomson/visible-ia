# CLAUDE.md

@AGENTS.md

## Específico de Claude Code
- Al iniciar la sesión, el hook de `.claude/settings.json` te muestra `memoria/ESTADO.md`. Úsalo para orientarte antes de hacer cualquier cosa.
- Los flujos del proyecto están en `.claude/commands/`. Si el director describe algo que coincide con un comando (p. ej. "anota esta idea"), sigue ese flujo aunque no escriba el comando.
- El director está aprendiendo Git/GitHub. Cuando ejecutes comandos de Git, explica en una línea qué hace cada uno y por qué.
- Usa el modo plan para tareas grandes y muestra el plan antes de modificar muchos archivos.
- Si existe un MCP de Gemini configurado, puedes pedirle una segunda opinión en decisiones de arquitectura o revisiones de código grandes. Anota su respuesta en el ADR o el acta correspondiente.

## Web y textos de venta
- Antes de cambiar `web/` o escribir textos de venta, lee `docs/marca/DESIGN.md`, `docs/marca/VOZ.md` y las skills `frontend-design`, `copywriting` y `marketing-psychology` (en `.claude/skills/`).
- Después de cada cambio visual, saca capturas con Playwright en 390, 768 y 1440 px, míralas y corrige antes de mostrar nada.
