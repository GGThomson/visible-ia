# Fase C9 · Cobros manuales y atribución → v1.1 "Servir"

**Objetivo:** el operador registra los pagos manuales y ve qué clientes están al día. La clínica recibe un kit para atribuir los pacientes que llegan por la IA.
**Historias que cubre:** HU-23, HU-25
**Estado:** ⚪ pendiente
**Nota:** las tareas se refinan al empezar la fase, sin cambiar su alcance.

## Tareas

### C9-T01 · Registro de pagos y estado "al día" (HU-23)
- **Estado:** ⚪
- **Qué:**
  - `visible-ia pago registrar <cliente> --monto --medio link|yape|transferencia --periodo aaaa-mm --ref`.
  - `visible-ia pagos estado`: al día / vence pronto / atrasado.
  - Un paso en el job diario que avisa de los atrasados con un issue.
- **Criterios de aceptación:**
  - [ ] Los criterios de HU-23 del PRD.
  - [ ] Montos en soles. La inclusión del IGV queda configurable, porque todavía está pendiente del régimen (estrategia).
- **Pruebas:** unitarias por escenario de fechas.
- **Depende de:** C7-T01
- **Rama:** `feat/C9-T01-manual-payments`

### C9-T02 · Kit de atribución (HU-25)
- **Estado:** ⚪
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
