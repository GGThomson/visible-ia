# Sesión 2026-10-19 · Corrida de octubre y reorganización del repo (pasos 1–3)

- **Fase / tareas:** corrida mensual de octubre · reorganización de `src/` (acta `2026-09-29-mapa-del-sistema.md`), pasos 1–3
- **Rama(s):** una por paso (ver «Commits»)
- **Commits:** (se completan al cerrar la sesión)

## Qué se hizo
- **Corrida de octubre hecha el 19/10/2026**, a mitad de mes, con la aprobación del Director.
  - El día 1 solo corrió la estimación (issue #71). La aprobación llegó el 19/10 y el Director aceptó que los datos sean de mediados de mes.
  - Corrida 2 · Implantología · Miraflores: 60/60 respuestas, US$1.10, 184 menciones (144 asociadas, 40 sin clínica, 0 dudosas).
  - El workflow cerró el issue #71 y abrió el **#72 «Revisar corridas de octubre»**.
- **Comparación provisional** setiembre → octubre, con las menciones ya asociadas y **antes de la revisión**:
  - NEODENTIS: 2 % → 7 %
  - Clínica Virtual Dent: 2 % → 3 %
  - Clínica Dental Cano: 17 % → 15 %
  - The Dental Clinic & GT Concept: 15 % → 15 %
  - **Top 5:** se repiten las 5. Smiles Peru baja de 50 % a 32 %, y Cano, Teixeira y The Dental Clinic empatan en el 5.º lugar con 15 %.

## Pendiente de la corrida
- Revisar las **40 menciones sin clínica** (`visible-ia revisar corrida 2 --env prod`). Algunas suman a clínicas de la lista: «Clínica Dental Cano / Riedent / Kagem», «Smiles Peru All-on-4…», «Dr. Emmanuel Teixeira» y «Alium».
- Después: `visible-ia revisar cerrar 2 --env prod` y `visible-ia puntaje calcular 2 --env prod`. Recién entonces las cifras de octubre son las oficiales.
