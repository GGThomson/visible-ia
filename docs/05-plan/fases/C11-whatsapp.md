# Fase C11 · WhatsApp: reportes y alertas

**Objetivo:** la clínica recibe su reporte mensual y alertas (p. ej., "un competidor te pasó en ChatGPT") por WhatsApp.
**Historias que cubre:** HU-22
**Estado:** ⚪ pendiente
**Depende de (Director):** número de WhatsApp Business API aprobado por Meta y plantillas de mensaje aprobadas. Se paga con el primer cliente.
**Nota:** las tareas se refinan al empezar la fase, sin cambiar su alcance. Diseño de los webhooks: arquitectura, "Webhooks de la v1.2" (Edge Function como "buzón").

## Tareas

### C11-T01 · Envío de plantillas desde Python
- **Estado:** ⚪
- **Qué:** `whatsapp/envio.py` con la API de WhatsApp Cloud: envía la plantilla "reporte mensual" (con el enlace al PDF firmado y temporal) y la plantilla "alerta".
- **Criterios de aceptación:**
  - [ ] Solo se envía a clientes con consentimiento registrado.
  - [ ] Cada envío queda registrado con su costo estimado.
- **Pruebas:** unitarias con un cliente HTTP falso.
- **Depende de:** C8-T02
- **Rama:** `feat/C11-T01-whatsapp-send`

### C11-T02 · Webhook "buzón" en una Supabase Edge Function
- **Estado:** ⚪
- **Qué:**
  - Función `supabase/functions/whatsapp-webhook/index.ts` (≈ 50 líneas):
    1. Responde la verificación GET de Meta.
    2. Valida `X-Hub-Signature-256`.
    3. Guarda el evento en `evento_webhook`.
    4. Responde 200.
  - Migración de `evento_webhook`.
  - Python procesa los eventos (estados de entrega y respuestas).
- **Criterios de aceptación:**
  - [ ] Si la firma no es válida, se rechaza con 401 y no se guarda nada.
  - [ ] Ninguna lógica de negocio en TypeScript.
- **Pruebas:** prueba de Deno para la validación de firma; prueba de Python para el procesamiento.
- **Depende de:** C11-T01
- **Rama:** `feat/C11-T02-whatsapp-webhook`

### C11-T03 · Alertas de cambio
- **Estado:** ⚪
- **Qué:** tras la corrida mensual, detecta los cambios **significativos** (ADR-003) frente a los competidores y envía la alerta. Nunca se alerta por ruido.
- **Criterios de aceptación:**
  - [ ] Solo alerta con un cambio "sube" o "baja" según el ADR-003.
  - [ ] Como máximo 1 alerta por sede al mes.
- **Pruebas:** series sintéticas.
- **Depende de:** C11-T01, C5-T03
- **Rama:** `feat/C11-T03-alerts`

## Demo de la fase
- El Director recibe en su propio WhatsApp el reporte mensual de una sede de prueba y una alerta simulada.
