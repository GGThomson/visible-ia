---
description: Documenta una decisión importante como ADR con opciones, pros, contras y consecuencias.
argument-hint: "<tema a decidir>"
---

Tema: $ARGUMENTS

1. Revisa `docs/decisiones/` para confirmar que no exista ya una decisión sobre esto. Si existe, muéstrala y pregunta si hay un motivo nuevo para reabrirla.
2. Crea `docs/decisiones/ADR-<siguiente número>-<tema>.md` desde `ADR-000-plantilla.md` con estado **Propuesta**.
3. Investiga y llena el contexto y al menos 2 opciones con ventajas, desventajas y costo. Da tu recomendación.
4. Pregunta al Director si quiere segunda opinión. Si dice que sí, genera con `/contexto` un resumen para Gemini y Claude web, y espera el `/acta`.
5. Cuando el Director decida: estado **Aceptada**, completa las consecuencias, actualiza los documentos afectados (PRD, arquitectura, plan) y añade la decisión a "Decisiones recientes" en ESTADO.
6. Commit: `docs: ADR-XXX <tema>`.
