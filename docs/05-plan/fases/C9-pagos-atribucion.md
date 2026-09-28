# Fase C9 · Cobros manuales y atribución → v1.1 "Servir"

**Objetivo:** el operador registra los pagos manuales y ve qué clientes están al día. La clínica recibe un kit para atribuir los pacientes que llegan por la IA.
**Historias que cubre:** HU-23, HU-25
**Estado:** 🟡 tareas ✅; falta la demo de v1.1 (y la migración 0008 en prod)
**Nota:** las tareas se refinan al empezar la fase, sin cambiar su alcance.

## Tareas

### C9-T01 · Registro de pagos y estado "al día" (HU-23)
- **Estado:** ✅
- **Qué:**
  - `visible-ia pago registrar <cliente> --monto --medio link|yape|transferencia --periodo aaaa-mm --ref`.
  - `visible-ia pagos estado`: al día / vence pronto / atrasado.
  - Un paso en el job diario que avisa de los atrasados con un issue.
- **Criterios de aceptación:**
  - [ ] Los criterios de HU-23 del PRD.
  - [ ] Montos en soles. La inclusión del IGV queda configurable, porque todavía está pendiente del régimen (estrategia).
- **Pruebas:** unitarias por escenario de fechas.
- **Refinamiento aprobado por el Director (27/09; todo ajustable por configuración):**
  - Cada pago cubre un mes (`--periodo`), por adelantado.
  - Un mes vence el día 1, o el día en que se creó el cliente si es posterior, más **5 días de gracia** (`PAGO_DIAS_GRACIA`).
  - **Atrasado:** el mes actual sin pagar y vencido.
  - **Vence pronto:** el mes actual sin pagar pero dentro de la gracia, o pagado con el siguiente sin pagar y a **7 días o menos** (`PAGO_AVISO_DIAS`).
  - **Al día:** el resto.
  - Las clínicas de una agencia no se listan (se cobra a la agencia).
  - `PAGOS_INCLUYEN_IGV` (por defecto `false` mientras el contador no defina el régimen) solo cambia el neto que se muestra.
  - El job diario usa el secret `SUPABASE_DB_URL_PROD`, que ya existe.
- **Depende de:** C7-T01
- **Rama:** `feat/C9-T01-manual-payments`

### C9-T02 · Kit de atribución (HU-25)
- **Estado:** ✅
  - Migración **0008**: tabla `attributions` (sede × mes), en dev; en prod, con el OK del Director.
  - Panel: sección «Pacientes que llegan por la IA».
  - Anexo: `informe kit --sede` genera un PDF local de 1 página para enviar por WhatsApp.
  - `atribucion registrar` sirve cuando la clínica manda el número por WhatsApp.
  - Cupón sugerido: `IA-` + la primera palabra propia del nombre.
  - UTM para la ficha de Google, Doctoralia e Instagram.
- **Qué:** sección del panel y un anexo PDF con:
  - la pregunta de intake "¿Cómo nos conociste?", con la opción "ChatGPT / IA";
  - un generador de enlaces con UTM para la web y Doctoralia;
  - un cupón exclusivo sugerido.
  - La clínica registra en el panel cuántos pacientes llegaron "por IA" cada mes.
- **Criterios de aceptación:**
  - [ ] Los criterios de HU-25 del PRD.
  - [ ] El conteo "por IA" aparece en el reporte mensual.
- **Pruebas:** unitarias del generador de UTM; manuales del panel.
- **Depende de:** C8-T02
- **Rama:** `feat/C9-T02-attribution-kit`

## Demo de la fase (= demo de la v1.1)
- El Director registra un pago, ve el estado de los clientes, y una clínica de prueba carga "3 pacientes por IA" que aparecen en su reporte mensual.
- **Al aprobar:** tag `v1.1`.
