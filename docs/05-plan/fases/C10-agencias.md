# Fase C10 · Agencias y marca blanca

**Objetivo:** una agencia ve en una sola vista todas las sedes de sus clientes, y sus informes salen con su logo y sus colores, sin la marca visible-ia.
**Historias que cubre:** HU-16, HU-21
**Estado:** ⚪ pendiente
**Nota:** las tareas se refinan al empezar la fase, sin cambiar su alcance. Si una agencia lo pide antes, el PDF con su logo puede generarse a mano desde la v1.0 (PRD HU-16), porque la plantilla ya lee el logo y los colores de variables.

## Tareas

### C10-T01 · Agencia como cliente madre + RLS de agencia
- **Estado:** ⚪
- **Qué:**
  - `visible-ia cliente crear --tipo agencia`; clientes con `--agencia <id>`.
  - Migración `0004_agency_policies.sql`: el usuario de una agencia lee las sedes de sus clientes y **no** las de otras agencias.
- **Criterios de aceptación:**
  - [ ] Prueba RLS: la agencia A no ve a los clientes de la agencia B, ni a las clínicas directas.
- **Pruebas:** RLS con dos agencias de prueba.
- **Depende de:** C9 completa
- **Rama:** `feat/C10-T01-agency-rls`

### C10-T02 · Vista de agencia (HU-21)
- **Estado:** ⚪
- **Qué:** página `web/panel/agencia.html`: tabla de todas las sedes, con su índice, su cambio y sus tareas pendientes, que lleva al detalle de cada sede.
- **Criterios de aceptación:**
  - [ ] Los criterios de HU-21 del PRD.
- **Pruebas:** manuales + las pruebas RLS de C10-T01.
- **Depende de:** C10-T01
- **Rama:** `feat/C10-T02-agency-view`

### C10-T03 · Marca blanca en los PDF (HU-16)
- **Estado:** ⚪
- **Qué:**
  - La agencia sube su logo y elige sus colores (Storage + `clients`).
  - Los informes diagnóstico y mensual de sus clientes salen con su marca, sin la marca visible-ia.
- **Criterios de aceptación:**
  - [ ] Los criterios de HU-16 del PRD.
  - [ ] El logo tiene como máximo 1 MB, en PNG o SVG, y se valida.
- **Pruebas:** renderizado con y sin marca blanca.
- **Depende de:** C10-T01
- **Rama:** `feat/C10-T03-white-label`

## Demo de la fase
- El Director crea una agencia de prueba con 2 clínicas, entra como agencia, ve las 2 sedes y genera un reporte con el logo de la agencia.
