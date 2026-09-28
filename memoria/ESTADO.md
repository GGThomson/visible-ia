# 📍 ESTADO DEL PROYECTO
<!-- Máximo ~60 líneas. Lo actualiza /cerrar-sesion. El detalle va a la bitácora. -->

**Proyecto:** visible-ia: visibilidad de clínicas locales en asistentes de IA  
**Tipo:** A (SaaS) + J (datos / IA)  
**Última actualización:** 2026-09-26  

## Dónde estamos
- **Fase actual:** 5 · Construcción. Fase 4 aprobada el 26/09: arquitectura + plan (tags `fase-4-completa`, `plan-aprobado`)
- **Tarea actual:** **C8**: T01 corrida mensual con OK ✅, T02 reporte mensual ✅, T03 checklist ✅, T04 JSON-LD ✅. Falta la **demo** del Director y la **migración 0007 en prod**. Panel: https://visible-ia.pages.dev/panel/
- **Rama de trabajo:** cada tarea en `feat/C<n>-T<nn>-...` desde `main` (las fases 1–4 ya están en `main`)
- **Avance general:** █████████░ 88 % (construcción: C1–C8 de C1–C12, demo de C8 pendiente)
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
1. **Director:** aprobar la migración 0007 en prod; demo de C8 con una sede de prueba (checklist, JSON-LD, reporte mensual de setiembre); el **1/10** llega el issue "Corridas de octubre · esperando tu OK" → aprobar lanzando *Corrida mensual* en modo `correr`
2. Ventas desde el 05/10 con las 5 clínicas con brecha; demo v1.0 (formulario → issue)
3. `/siguiente` → **C9** (pagos manuales y atribución)

## Bloqueos / esperando decisión
- ⏳ **RUC y régimen tributario** (contador) antes del primer cobro. Define si los S/ 349 incluyen IGV (neto ≈ S/ 296) → revisar la meta de la semana 6
- ⏳ Confirmar a los 8 días que el job diario mantiene activo Supabase dev (C1-T05)
- 🔽 Prueba API Gemini (informativa, baja prioridad): config. B, 1 de 10 hecha (rama `chore/prueba-api-gemini`)

## Decisiones recientes (últimas 5)
- 2026-09-27 · C8: la corrida mensual **pide OK**: el día 1 solo estima y abre un issue; se aprueba lanzando el workflow en modo `correr`. Checklist en TOML (sin dependencia nueva); JSON-LD sin reseñas propias
- 2026-09-27 · C7 cerrada: acceso al panel **por enlaces de WhatsApp** (`usuario invitar --enlace`), sin SMTP propio por ahora; registro abierto apagado en Supabase; migración 0006 en prod
- 2026-09-27 · **v1.0 cerrada** por el Director: migración 0005 y bucket `informes` en prod; landing publicada; contacto del informe = WhatsApp +51 920 857 428. Secrets de GitHub recargados desde `.env`
- 2026-09-27 · Corrida 1 revisada y puntuada: Smiles Peru lidera (50); 5 clínicas con brecha Maps vs IA. Plan B (C6-T05) no se activa: la guía queda como respaldo y manual de operación
- 2026-09-27 · C4 cerrada: 63 etiquetas confirmadas por muestreo (1 corrección), salidas del extractor grabadas (US$0.0075), metas del PRD §5.3 cumplidas. Criterios en `data/eval/criterios-etiquetado.md`

## Bandeja de pendientes
- Ver `memoria/cambios-pendientes.md` (0 sin clasificar)
