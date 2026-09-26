---
description: Trabaja el entregable de la fase de planificación actual (descubrimiento, estrategia, especificación o arquitectura).
argument-hint: "[número de fase, opcional]"
---

1. Lee `memoria/ESTADO.md` y `docs/00-inicio/brief.md`. La fase a trabajar es $ARGUMENTS o, si viene vacío, la fase actual del ESTADO.
2. Abre el documento de esa fase:
   - 1 → `docs/01-descubrimiento/investigacion.md`
   - 2 → `docs/02-estrategia/estrategia.md`
   - 3 → `docs/03-especificacion/prd.md`
   - 4 → `docs/04-arquitectura/arquitectura.md` (y termina con `/planificar`)
3. Usa solo las secciones que aplican al **tipo** de proyecto, con la profundidad del brief. Borra las secciones que no apliquen.
4. Trabaja con el Director por secciones: propón un borrador, pregunta lo que falte (máximo 3 preguntas por vez) y completa. Si puedes investigar en la web (competencia, precios, tecnologías), hazlo y cita las fuentes en el documento.
5. Si aparece una decisión importante, usa el flujo de `/decision`.
6. Si el tema necesita segunda opinión, sugiere: "Ejecuta `/contexto <tema>` y llévalo a Gemini y a Claude web".
7. Al terminar la fase, pide la **aprobación explícita** del Director (puerta de aprobación), márcala en el documento, actualiza ESTADO (fase ✅, siguiente 🟡) y haz commit `docs: completa fase N - <nombre>` y el tag `fase-N-completa`.
