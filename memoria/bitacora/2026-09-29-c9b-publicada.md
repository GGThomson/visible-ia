# Sesión 2026-09-29 · C9b publicada

- **Fase / tareas:** C9b (publicación)
- **Rama(s):** `feat/C9b-marca-y-oferta` (PR #67, fusionado) · `docs/cierre-c9b-publicada`
- **Commits:** 33ed6b4 feat(C9b): consent_version obligatoria (migración 0011) · 2ff3ebf Merge PR #67

## Qué se hizo
- Migración **0011**: `prospects.consent_version` pasa a NOT NULL y la política de inserción anónima la exige. Probada en dev (27 pruebas de RLS y formulario en verde).
- PR #67 fusionado con el OK escrito del Director; la landing Eminia quedó publicada en https://visible-ia.pages.dev y se comprobó que el formulario en línea envía `consent_version`.
- El **Director aplicó la 0011 en prod** (el permiso automático bloqueó aplicarla con confirmación ciega); `db status --env prod`: sin migraciones pendientes.

## Qué se decidió (y dónde quedó registrado)
- Orden seguro: publicar la landing primero y migrar después, para no rechazar pedidos de la landing vieja (comentario en `0011_*.sql`).

## Problemas y cómo se resolvieron
- `visible-ia db migrate --env prod` con `echo y` fue bloqueado por el permiso automático → lo ejecutó el Director.

## Para la próxima sesión
- Ofrecer el diagnóstico gratis a las 4 clínicas elegidas; corrida de octubre el 1/10; luego C10.
- Pendiente legal del Libro de Reclamaciones (domicilio, correlativo, copia por correo).

---

# Sesión 2026-09-29 (tarde) · Diagnósticos gratis en lote (C-010)

- **Fase / tareas:** C-010 (mejora pedida por el Director, antes de las ventas del 05/10)
- **Rama(s):** `feat/C-010-diagnostico-lote` (PR #68, fusionado) · `fix/C-010-plan-sin-repetir`
- **Commits:** 6bec7c3 feat(C-010): diagnósticos en lote con mensaje de WhatsApp · 46e34d8 merge PR #68 · fix(C-010): el plan no repite dos acciones con la misma medida

## Qué se hizo
- Comando `visible-ia diagnostico lote <archivo> --mercado N [--mes AAAA-MM]`: PDF + primer mensaje de WhatsApp (dato más fuerte, sin jerga) por cada nombre o id de la lista, solo con datos guardados. Resumen en `salida/diagnosticos/<mes>/mensajes.md`.
- Vocabulario del nicho en `src/visible_ia/nicho.toml`; firma en `marca.toml`; una prueba impide escribir «clínica» o «paciente» en el código nuevo.
- Diagnóstico de vuelta en ≤ 8 páginas (HU-14) con datos reales: 2 frases por competidor, ejemplos de ≤ 400 caracteres y versión compacta automática (1 ejemplo) si se pasa.
- Plan de acción sin acciones repetidas: «Más reseñas» y «Convierte tu reputación en Maps» miden la misma diferencia; queda la de mayor impacto (en empate, la primera de `recomendaciones.toml`) y entra la siguiente.
- 4 diagnósticos generados (Implantes · Miraflores, setiembre; ~US$0.001 en gpt-5-nano, sin corridas): NEODENTIS, Clínica Virtual Dent (regenerado con el plan sin repetir), Clínica Dental Cano, The Dental Clinic & GT Concept.

## Qué se decidió (y dónde quedó registrado)
- C-010 en `memoria/cambios-pendientes.md`. Regla de acciones con la misma medida: `GAP_MEASURE` en `semaforo.py`.

## Problemas y cómo se resolvieron
- Con datos reales el PDF llegaba a 9 páginas y variaba según las frases que elige gpt-5-nano → red de seguridad que cuenta páginas y rehace el PDF compacto.
- «0 de las 1 respuestas» → frase en singular y cero bien escrita.

## Para la próxima sesión
- Director: revisar y enviar los 4 diagnósticos y mensajes (`salida/diagnosticos/2026-09/`).
