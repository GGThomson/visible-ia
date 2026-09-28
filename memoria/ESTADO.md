# 📍 ESTADO DEL PROYECTO
<!-- Máximo ~60 líneas. Lo actualiza /cerrar-sesion. El detalle va a la bitácora. -->

**Proyecto:** visible-ia: visibilidad de clínicas locales en asistentes de IA  
**Tipo:** A (SaaS) + J (datos / IA)  
**Última actualización:** 2026-09-26  

## Dónde estamos
- **Fase actual:** 5 · Construcción. Fase 4 aprobada el 26/09: arquitectura + plan (tags `fase-4-completa`, `plan-aprobado`)
- **Tarea actual:** **C8** (reporte mensual + checklist + recomendaciones). C7 ✅: panel en https://visible-ia.pages.dev/panel/ con acceso por enlace de WhatsApp; demo aprobada. Landing: https://visible-ia.pages.dev
- **Rama de trabajo:** cada tarea en `feat/C<n>-T<nn>-...` desde `main` (las fases 1–4 ya están en `main`)
- **Avance general:** █████████░ 85 % (construcción: C1–C7 de C1–C12)
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
1. `/siguiente` → **C8** (reporte mensual en PDF, checklist priorizado, schema JSON-LD)
2. **Director:** demo v1.0 (formulario → issue "Prospectos nuevos"); ventas desde el 05/10 con las 5 clínicas con brecha
3. Primer cliente real: `visible-ia cliente crear` → `sede agregar` → `usuario invitar … --enlace` (enlace por WhatsApp). En paralelo: lista de 40 clínicas, pasarela, legales

## Bloqueos / esperando decisión
- ⏳ **RUC y régimen tributario** (contador) antes del primer cobro. Define si los S/ 349 incluyen IGV (neto ≈ S/ 296) → revisar la meta de la semana 6
- ⏳ Confirmar a los 8 días que el job diario mantiene activo Supabase dev (C1-T05)
- 🔽 Prueba API Gemini (informativa, baja prioridad): config. B, 1 de 10 hecha (rama `chore/prueba-api-gemini`)

## Decisiones recientes (últimas 5)
- 2026-09-27 · C7 cerrada: acceso al panel **por enlaces de WhatsApp** (`usuario invitar --enlace`), sin SMTP propio por ahora; registro abierto apagado en Supabase; migración 0006 en prod
- 2026-09-27 · **v1.0 cerrada** por el Director: migración 0005 y bucket `informes` en prod; landing publicada; contacto del informe = WhatsApp +51 920 857 428. Secrets de GitHub recargados desde `.env`
- 2026-09-27 · Corrida 1 revisada y puntuada: Smiles Peru lidera (50); 5 clínicas con brecha Maps vs IA. Plan B (C6-T05) no se activa: la guía queda como respaldo y manual de operación
- 2026-09-27 · C4 cerrada: 63 etiquetas confirmadas por muestreo (1 corrección), salidas del extractor grabadas (US$0.0075), metas del PRD §5.3 cumplidas. Criterios en `data/eval/criterios-etiquetado.md`
- 2026-09-27 · C4-T05: el Director revisa 15 de 63 etiquetas; con ≤ 1 corrección se confirman las 63 por muestreo, si no, Claude revisa el resto y hay otra muestra. Lista IMP · Miraflores confirmada (34 clínicas) e importada en prod

## Bandeja de pendientes
- Ver `memoria/cambios-pendientes.md` (0 sin clasificar)
