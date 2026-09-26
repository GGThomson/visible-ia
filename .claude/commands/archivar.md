---
description: Cierra el proyecto o una versión. Retrospectiva, release y guía para retomarlo.
---

1. Verifica con el Director que la versión está terminada o que el proyecto se pausa (esto también es válido: "archivar" no significa abandonar).
2. Llena `docs/07-cierre/retrospectiva.md`: resumen, resultados frente al brief, aprendizajes, deuda técnica, ideas v2 (desde `cambios-pendientes.md`) y la sección **Cómo retomar** con los comandos reales, que debes **probar**.
3. Revisa que exista `.env.example` con todas las variables (sin valores reales) y que el README técnico esté al día.
4. Actualiza ESTADO: estado "📦 Archivado vX.Y.Z" y los pasos para retomar.
5. Git: commit `docs: retrospectiva y archivo vX.Y.Z`, tag `vX.Y.Z` y `gh release create vX.Y.Z --generate-notes`, explicando cada comando.
6. Pregunta al Director si alguna lección debería llevarse a la **plantilla maestra**. Si es así, lista los cambios exactos a hacer allí.
7. (Opcional) Sugiere subir `docs/` y `memoria/` a un cuaderno de NotebookLM del proyecto para consultar la historia a futuro (ver `docs/guias/mcp-integraciones.md`).
