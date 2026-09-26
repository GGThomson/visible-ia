# Fase C7 · Cuentas y panel de la clínica

**Objetivo:** la clínica entra con un enlace mágico a un panel web y ve **solo lo suyo**: su índice con el margen, el ranking frente a los competidores, las fuentes del mercado y la evolución.
- Las políticas RLS están probadas de forma automática.

**Historias que cubre:** HU-19, HU-20 (+ HU-11 y HU-12 en el panel)
**Estado:** ⚪ pendiente
**Nota:** las tareas se refinan al empezar la fase (Notas para Claude Code), sin cambiar su alcance.

## Tareas

### C7-T01 · Clientes, sedes y usuarios desde la CLI
- **Estado:** ⚪
- **Qué:**
  - `visible-ia cliente crear --tipo clinica ...`
  - `visible-ia sede agregar <cliente> --clinica <id> --mercado <id>`
  - `visible-ia usuario invitar <cliente> <correo>`: crea el usuario en Supabase Auth y envía el enlace mágico.
- **Archivos probables:** `src/visible_ia/clientes.py`, `tests/unit/test_clientes.py`
- **Criterios de aceptación:**
  - [ ] Una clínica puede tener varias sedes.
  - [ ] Invitar un correo existente no duplica al usuario.
- **Pruebas:** unitarias + integración en dev.
- **Depende de:** C6 completa
- **Rama:** `feat/C7-T01-clients-sites`

### C7-T02 · Políticas RLS de lectura por cliente + pruebas
- **Estado:** ⚪
- **Qué:** migración `0003_client_read_policies.sql`.
  - El usuario de una clínica lee `monthly_scores`, `mentions`, `sources`, `reports` y `tasks` **solo** de los mercados y sedes de su cliente.
  - Vistas de solo lectura para el panel (`v_panel_*`) que no exponen el texto crudo de otras clínicas.
- **Archivos probables:** `supabase/migrations/0003_client_read_policies.sql`, `tests/rls/test_client_isolation.py`
- **Criterios de aceptación:**
  - [ ] El requisito del PRD §6 "cada cliente ve solo sus datos" tiene una prueba por tabla y por vista: el usuario A no ve nada del B.
  - [ ] Los competidores se ven como ranking agregado (nombre e índice), sin acceso a los datos de sus cuentas.
- **Pruebas:** RLS con dos usuarios de prueba en dev.
- **Depende de:** C7-T01
- **Rama:** `feat/C7-T02-rls-client`

### C7-T03 · Login con enlace mágico (HU-19)
- **Estado:** ⚪
- **Qué:** `web/panel/login.html` + `web/panel/app.js` con `supabase-js` (CDN): pide el correo, envía el enlace, maneja la sesión y cierra sesión.
- **Criterios de aceptación:**
  - [ ] Los criterios de HU-19 del PRD: entra solo con su correo y ve solo lo suyo.
  - [ ] Funciona en el celular (Chrome y Safari).
- **Pruebas:** manuales guiadas (lista de verificación en el PR), más las pruebas RLS de C7-T02.
- **Depende de:** C7-T02
- **Rama:** `feat/C7-T03-magic-link`

### C7-T04 · Panel: índice, ranking, fuentes y evolución (HU-20)
- **Estado:** ⚪
- **Qué:** `web/panel/index.html`, con:
  - índice combinado y por superficie, con su margen y la frase de cambio del ADR-003;
  - ranking del mercado;
  - top de fuentes;
  - evolución mensual y ventana de 3 meses;
  - checklist con sus tareas (se completa en C8).
- **Criterios de aceptación:**
  - [ ] Carga en ≤ 3 s en 4G (PRD §6).
  - [ ] Los gráficos muestran su valor en texto (accesibilidad AA).
- **Pruebas:** manuales, más una prueba de humo que valida la estructura de las vistas `v_panel_*`.
- **Depende de:** C7-T03
- **Rama:** `feat/C7-T04-panel`

## Demo de la fase
- El Director invita a una clínica de prueba, entra con el enlace desde su celular, ve su panel y confirma que otra clínica de prueba no ve sus datos.
