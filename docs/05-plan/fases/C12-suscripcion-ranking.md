# Fase C12 · Suscripción automática y ranking gratis → v1.2 "Escalar"

**Objetivo:** la clínica puede pagar con una suscripción automática con tarjeta, y la landing muestra un ranking gratis por rubro y distrito como gancho.
**Historias que cubre:** HU-24 (Could), HU-27 (Could)
**Estado:** ⚪ pendiente
**Depende de (Director):** RUC y régimen definidos; cuenta de Culqi o Mercado Pago aprobada.
**Nota:** son historias **Could**. Si el tiempo no alcanza en la semana 6, se pasan a después de la v1.2 sin afectar la venta. Las tareas se refinan al empezar la fase.

## Tareas

### C12-T01 · Suscripción con webhook "buzón" (HU-24)
- **Estado:** ⚪
- **Qué:**
  - Crear la suscripción en Culqi o Mercado Pago (la que elija el Director) con un enlace de alta.
  - Edge Function `payments-webhook`: valida la firma, guarda el evento y responde 200.
  - Python concilia los eventos con `payments`.
- **Criterios de aceptación:**
  - [ ] Los criterios de HU-24 del PRD.
  - [ ] Un cobro exitoso marca el periodo como pagado sin intervención.
  - [ ] Un fallo abre un issue.
- **Pruebas:** eventos de prueba del proveedor (modo sandbox).
- **Depende de:** C9-T01, C11-T02 (patrón de Edge Function)
- **Rama:** `feat/C12-T01-subscription`

### C12-T02 · Ranking gratis por rubro y distrito (HU-27)
- **Estado:** ⚪
- **Qué:** página `web/ranking.html` con el **top 5** de cada mercado medido (nombre y banda de presencia: alta, media o baja), sin porcentajes exactos ni textos de las IAs. Lleva al formulario del informe gratis.
- **Criterios de aceptación:**
  - [ ] Los criterios de HU-27 del PRD: solo el top y sin detalle.
  - [ ] Vista pública de solo lectura con RLS, limitada a esos campos.
  - [ ] Revisión legal: nota de método visible y, si el abogado lo pide, un mecanismo para retirar una clínica (Ley 29733 / reputación).
- **Pruebas:** RLS (la vista pública no expone nada más).
- **Depende de:** C5-T02, C6-T03
- **Rama:** `feat/C12-T02-public-ranking`

## Demo de la fase (= demo de la v1.2)
- El Director se suscribe con una tarjeta de prueba y ve el pago conciliado.
- Abre el ranking público de "Implantología · Miraflores".
- **Al aprobar:** tag `v1.2`.
