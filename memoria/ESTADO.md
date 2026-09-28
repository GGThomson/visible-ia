# 📍 ESTADO DEL PROYECTO
<!-- Máximo ~60 líneas. Lo actualiza /cerrar-sesion. El detalle va a la bitácora. -->

**Proyecto:** visible-ia: visibilidad de clínicas locales en asistentes de IA  
**Tipo:** A (SaaS) + J (datos / IA)  
**Última actualización:** 2026-09-26  

## Dónde estamos
- **Fase actual:** 5 · Construcción. Fase 4 aprobada el 26/09: arquitectura + plan (tags `fase-4-completa`, `plan-aprobado`)
- **Tarea actual:** **C7 (cuentas y panel)**: T01 clientes/sedes/usuarios ✅ y T02 RLS por cliente ✅ en `main` (0006 solo en dev); **T03/T04 acceso + panel listos en el PR #52, sin fusionar** hasta aplicar 0006 en prod y configurar Auth. v1.0 cerrada. Landing: https://visible-ia.pages.dev
- **Rama de trabajo:** cada tarea en `feat/C<n>-T<nn>-...` desde `main` (las fases 1–4 ya están en `main`)
- **Avance general:** ████████░░ 82 % (construcción: C1–C6 y C7 casi, de C1–C12)
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
1. **Director:** aprobar la migración 0006 en prod; en Supabase (dev y prod) → Authentication: Site URL `https://visible-ia.pages.dev`, Redirect URLs `https://visible-ia.pages.dev/panel/` y `https://*.visible-ia.pages.dev/panel/`, y **apagar "Allow new users to sign up"**; decidir correo (SMTP propio, p. ej. Resend gratis) o enlaces por WhatsApp
2. Fusionar el PR #52 → demo de C7: invitar una clínica de prueba (`visible-ia usuario invitar <cliente> <correo> --enlace --env prod`), abrir el panel en el celular y confirmar que otra no ve sus datos
3. Demo v1.0 (formulario → issue) y ventas desde el 05/10 con las 5 clínicas con brecha. Luego C8 (reporte mensual y checklist)

## Bloqueos / esperando decisión
- ⏳ **RUC y régimen tributario** (contador) antes del primer cobro. Define si los S/ 349 incluyen IGV (neto ≈ S/ 296) → revisar la meta de la semana 6
- ⏳ Confirmar a los 8 días que el job diario mantiene activo Supabase dev (C1-T05)
- 🔽 Prueba API Gemini (informativa, baja prioridad): config. B, 1 de 10 hecha (rama `chore/prueba-api-gemini`)

## Decisiones recientes (últimas 5)
- 2026-09-27 · **v1.0 cerrada** por el Director: migración 0005 y bucket `informes` en prod; landing publicada; contacto del informe = WhatsApp +51 920 857 428. Secrets de GitHub recargados desde `.env`
- 2026-09-27 · Corrida 1 revisada y puntuada: Smiles Peru lidera (50); 5 clínicas con brecha Maps vs IA. Plan B (C6-T05) no se activa: la guía queda como respaldo y manual de operación
- 2026-09-27 · C4 cerrada: 63 etiquetas confirmadas por muestreo (1 corrección), salidas del extractor grabadas (US$0.0075), metas del PRD §5.3 cumplidas. Criterios en `data/eval/criterios-etiquetado.md`
- 2026-09-27 · C4-T05: el Director revisa 15 de 63 etiquetas; con ≤ 1 corrección se confirman las 63 por muestreo, si no, Claude revisa el resto y hay otra muestra. Lista IMP · Miraflores confirmada (34 clínicas) e importada en prod
- 2026-09-27 · C-006 → se declara en la nota de método (3 de 30 respuestas de Google con fichas sin nombre). Bug corregido: la CLI no confirmaba cada respuesta (se perdió 1 crédito); ahora `autocommit`. SerpApi: 37/250 usadas; OpenAI ≈ US$1.01/5

## Bandeja de pendientes
- Ver `memoria/cambios-pendientes.md` (0 sin clasificar)
