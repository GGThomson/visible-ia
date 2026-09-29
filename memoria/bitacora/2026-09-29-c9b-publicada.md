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
