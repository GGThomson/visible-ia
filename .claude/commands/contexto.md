---
description: Regenera el paquete de contexto para llevar un tema a Gemini o a Claude web.
argument-hint: "<tema de la conversación>"
---

Tema a discutir con los planificadores: $ARGUMENTS

1. Lee ESTADO, brief, los ADRs aceptados y el documento de la fase actual.
2. Reescribe `memoria/contexto-rapido.md` (máximo ~1 página) respetando su estructura: proyecto, estado, lo ya decidido, stack, **tema de esta conversación** con los datos concretos necesarios y el formato de ACTA al final.
3. Si el tema necesita un documento completo (p. ej. revisar el PRD), dile al Director qué archivo adjuntar además del contexto.
4. Muestra el contenido final en un bloque para que lo copie y dile:
   "Pégalo en un chat nuevo de Gemini y otro de Claude web. Cuando respondan, copia sus ACTAS y ejecuta `/acta`."
5. Commit: `docs: actualiza contexto rápido`.
