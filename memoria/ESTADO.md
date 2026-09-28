# 📍 ESTADO DEL PROYECTO
<!-- Máximo ~60 líneas. Lo actualiza /cerrar-sesion. El detalle va a la bitácora. -->

**Proyecto:** visible-ia: visibilidad de clínicas locales en asistentes de IA  
**Tipo:** A (SaaS) + J (datos / IA)  
**Última actualización:** 2026-09-28  

## Dónde estamos
- **Fase actual:** 5 · Construcción. Fase 4 aprobada el 26/09: arquitectura + plan (tags `fase-4-completa`, `plan-aprobado`)
- **Tarea actual:** **C9b · Marca y oferta**: T01–T06 ✅ en el PR (marca Eminia, landing nueva, guion). Falta que el Director apruebe la **vista previa** y envíe su foto; luego C10. Panel: https://visible-ia.pages.dev/panel/
- **Rama de trabajo:** cada tarea en `feat/C<n>-T<nn>-...` desde `main` (las fases 1–4 ya están en `main`)
- **Avance general:** █████████░ 91 % (construcción: C1–C9 de C1–C12 completas; v1.0 y v1.1 listas)
- **Calendario:** construcción del 28/09 al 08/11 · **v1.0 "Vender" el 04/10** · ventas desde el 05/10 · control del Plan B el **jue 02/10** (C6-T05)

## Ruta de fases
| # | Fase | Prof. | Estado |
|---|---|---|---|
| 0 | Inicio | — | ✅ |
| 1 | Descubrimiento | ●● | ✅ |
| 2 | Estrategia | ● | ✅ |
| 3 | Especificación | ●● | ✅ |
| 4 | Arquitectura y plan | ●● | ✅ |
| 5 | Construcción (C1–C12) | ●●● | 🟡 en curso |
| 6 | Lanzamiento | ●● | ⚪ |
| 7 | Cierre / mantenimiento | ● | ⚪ |
<!-- ⚪ pendiente · 🟡 en curso · ✅ completa · ⏭️ omitida (explicar por qué en el brief) -->

## Próximos 3 pasos
1. **Director:** el **1/10** llega el issue "Corridas de octubre · esperando tu OK" → aprobar lanzando *Corrida mensual* en modo `correr`
2. **Director:** revisar la vista previa del PR de C9b en el celular y en la computadora; si la aprueba, se fusiona y se publica. Enviar su foto
3. Ventas desde el 05/10 con las 5 clínicas con brecha, usando el guion y los planes Medir / Gestionado; luego **C10**

## Bloqueos / esperando decisión
- ⏳ **Al publicar la landing (C9b):** migración que haga obligatoria `prospects.consent_version` (0009 la dejó opcional). Libro de Reclamaciones: esperando RUC y la forma de recibir reclamos
- ⏳ **Director:** revisar INDECOPI (clases 35 y 42) y eminia.pe antes de comprar o registrar (si no están libres → Prominia); enviar su foto para la landing (C9b-T04)
- ⏳ **RUC y régimen tributario** (contador) antes del primer cobro. Define si los S/ 349 incluyen IGV (neto ≈ S/ 296) → revisar la meta de la semana 6
- ⏳ Confirmar a los 8 días que el job diario mantiene activo Supabase dev (C1-T05)
- 🔽 Prueba API Gemini (informativa, baja prioridad): config. B, 1 de 10 hecha (rama `chore/prueba-api-gemini`)

## Decisiones recientes (últimas 5)
- 2026-09-28 · **Marca Eminia** (ADR-005) y oferta para las llamadas: planes Diagnóstico gratis / Medir (S/ 349 + 490) / Gestionado (S/ 790 + 990), sin permanencia, precio fundador (5 primeras) y garantía de entrega en 10 días; fase C9b antes de C10 (acta 2026-09-28)
- 2026-09-27 · **C9 cerrada, v1.1 lista** (tag `v1.1`): pagos manuales con las reglas de «al día» aprobadas (5 días de gracia, aviso 7 días antes, IGV configurable), kit de atribución y conteo «por IA» en el reporte; migración 0008 en prod
- 2026-09-27 · **C8 cerrada**: demo del Director aprobada en prod (sede de prueba borrada después); migración 0007 en prod; las URLs de Instagram se guardan sin `?hl=en` ni otros parámetros
- 2026-09-27 · C8: la corrida mensual **pide OK**: el día 1 solo estima y abre un issue; se aprueba lanzando el workflow en modo `correr`. Checklist en TOML (sin dependencia nueva); JSON-LD sin reseñas propias
- 2026-09-27 · C7 cerrada: acceso al panel **por enlaces de WhatsApp** (`usuario invitar --enlace`), sin SMTP propio por ahora; registro abierto apagado en Supabase; migración 0006 en prod

## Bandeja de pendientes
- Ver `memoria/cambios-pendientes.md` (0 sin clasificar)
