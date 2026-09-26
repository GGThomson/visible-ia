---
description: Entrevista inicial. Identifica tipo y propósito del proyecto y arma la ruta de fases.
argument-hint: "[idea en una frase, opcional]"
---

Vas a iniciar un proyecto nuevo (o una nueva versión de uno existente). Idea inicial del Director: $ARGUMENTS

1. Lee `docs/00-inicio/tipos-de-proyecto.md` y `memoria/ESTADO.md`. Si `docs/00-inicio/brief.md` ya está lleno, pregunta si es una **nueva versión**. En ese caso no borres nada: crea `brief-v2.md` y trabaja sobre él.
2. Entrevista al Director **en rondas de máximo 3 preguntas**, en lenguaje simple:
   - Ronda 1: ¿Qué quieres construir? ¿Quién te lo pide o para quién es? ¿Por qué?
   - Ronda 2: usa el árbol de decisión para proponer el **tipo** (o combinación) y confírmalo con el Director.
   - Ronda 3 en adelante: las preguntas clave de ese tipo (éxito, plazo, presupuesto, restricciones, tiempo por semana).
3. Propón la **ruta de fases** con profundidad (●●●/●●/●/—) y justifica cada omisión.
4. Llena `docs/00-inicio/brief.md` y actualiza `memoria/ESTADO.md` (tipo, ruta de fases, próximos 3 pasos, fase 0 ✅ cuando el Director apruebe).
5. Llena la primera versión de `memoria/contexto-rapido.md`.
6. Explica qué es un commit y haz: `git add -A && git commit -m "docs: brief inicial del proyecto"`. Luego `git push` si existe un remoto.
7. Termina diciendo cuál es la siguiente fase y qué comando usar (`/fase`).
