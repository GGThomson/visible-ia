# 📍 ESTADO DEL PROYECTO
<!-- Máximo ~60 líneas. Lo actualiza /cerrar-sesion. El detalle va a la bitácora. -->

**Proyecto:** visible-ia: visibilidad de clínicas locales en asistentes de IA  
**Tipo:** A (SaaS) + J (datos / IA)  
**Última actualización:** 2026-09-26  

## Dónde estamos
- **Fase actual:** 5 · Construcción. Fase 4 aprobada el 26/09: arquitectura + plan (tags `fase-4-completa`, `plan-aprobado`)
- **Tarea actual:** **C6 (v1.0 "Vender")**: T01 informe ✅, T02 PDF ✅, T04 aviso ✅, T05 guía ✅ (Plan B no se activa). **T03 landing lista en el PR #44, sin fusionar**: faltan las claves `anon` en Secrets y la migración 0005 en prod. Luego, la demo de la v1.0 → tag `v1.0`. Landing: https://visible-ia.pages.dev
- **Rama de trabajo:** cada tarea en `feat/C<n>-T<nn>-...` desde `main` (las fases 1–4 ya están en `main`)
- **Avance general:** ████████░░ 75 % (construcción: C1–C5 y C6 casi, de C1–C12)
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
1. **Director:** agregar a Secrets `SUPABASE_ANON_KEY_DEV`, `SUPABASE_ANON_KEY_PROD` y `SERPAPI_API_KEY`; dar el contacto real para el pie del informe (`informes/marca.toml`); aprobar la migración 0005 y el bucket `informes` en prod
2. Fusionar el PR #44 (landing) → demo de la v1.0: informe real en ≤ 10 min + formulario → issue al día siguiente → tag `v1.0` (meta 04/10)
3. Ventas desde el 05/10: primeros prospectos = las 5 clínicas con brecha (Odontologists, Digital Smiles, Elisseum, Virtual Dent, Neodentis). En paralelo: lista de 40 clínicas, WhatsApp, pasarela, legales

## Bloqueos / esperando decisión
- ⏳ **RUC y régimen tributario** (contador) antes del primer cobro. Define si los S/ 349 incluyen IGV (neto ≈ S/ 296) → revisar la meta de la semana 6
- ⏳ Confirmar a los 8 días que el job diario mantiene activo Supabase dev (C1-T05)
- 🔽 Prueba API Gemini (informativa, baja prioridad): config. B, 1 de 10 hecha (rama `chore/prueba-api-gemini`)

## Decisiones recientes (últimas 5)
- 2026-09-27 · Corrida 1 revisada y puntuada: Smiles Peru lidera (50); 5 clínicas con brecha Maps vs IA. Plan B (C6-T05) no se activa: la guía queda como respaldo y manual de operación
- 2026-09-27 · C4 cerrada: 63 etiquetas confirmadas por muestreo (1 corrección), salidas del extractor grabadas (US$0.0075), metas del PRD §5.3 cumplidas. Criterios en `data/eval/criterios-etiquetado.md`
- 2026-09-27 · C4-T05: el Director revisa 15 de 63 etiquetas; con ≤ 1 corrección se confirman las 63 por muestreo, si no, Claude revisa el resto y hay otra muestra. Lista IMP · Miraflores confirmada (34 clínicas) e importada en prod
- 2026-09-27 · C-006 → se declara en la nota de método (3 de 30 respuestas de Google con fichas sin nombre). Bug corregido: la CLI no confirmaba cada respuesta (se perdió 1 crédito); ahora `autocommit`. SerpApi: 37/250 usadas; OpenAI ≈ US$1.01/5
- 2026-09-26 · C4: extractor con gpt-5-nano y prompt v2 (la v1 descartaba todo con razonamiento mínimo); migraciones 0003 y 0004 en prod; `dentum.com.pe` = web de clínica. Gasto del mes ≈ US$1.01 de US$5

## Bandeja de pendientes
- Ver `memoria/cambios-pendientes.md` (0 sin clasificar)
