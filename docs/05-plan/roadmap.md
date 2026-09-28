# 🗺️ Roadmap (Fase 4 → guía de la Fase 5)
<!-- Lo genera /planificar desde el PRD y la arquitectura. Cada fase de construcción tiene su archivo en fases/. -->
<!-- Nombres: las fases de construcción usan el prefijo C (C1…C12) para no confundirse con las fases de planificación (F1–F4, tags fase-N-completa). Tareas: C<n>-T<nn>. Ramas: feat/C<n>-T<nn>-descripcion. -->

**Base:**
- [PRD v1 congelado](../03-especificacion/prd.md)
- [Arquitectura aprobada](../04-arquitectura/arquitectura.md)
- ADR-001 a ADR-004

**Calendario:**
- **Plan aprobado por el Director el 26/09/2026.** Seguimiento: `memoria/ESTADO.md` (sin GitHub Issues).
- Construcción del 28/09 al 08/11/2026.
- Ventas desde el 05/10: la v1.0 tiene que estar lista para generar informes gratis ese día.

## Fases de construcción
| Fase | Objetivo (resultado visible) | Historias | Archivo | Entrega | Semana | Estado |
|---|---|---|---|---|---|---|
| C1 | **Proyecto base:** paquete Python, CLI "hola", pruebas y CI en verde, Supabase dev/prod con el esquema inicial, job diario de mantenimiento, landing vacía publicada | — | [fases/C1-base.md](fases/C1-base.md) | v1.0 | 1 (28–29/09) | ✅ |
| C2 | **Mercados y clínicas:** crear un mercado con sus 10 preguntas e importar un CSV de clínicas con alias | HU-01, HU-02, HU-03 | [fases/C2-mercados.md](fases/C2-mercados.md) | v1.0 | 1 (29–30/09) | ✅ |
| C3 | **Motor de consultas:** una corrida real de un mercado (ChatGPT API + Google Modo IA), reanudable y con tope de presupuesto; carga de muestras manuales | HU-04, HU-05, HU-06 | [fases/C3-motor.md](fases/C3-motor.md) | v1.0 | 1 (30/09–01/10) | ✅ |
| C4 | **Extractor y revisión:** clínicas en orden y fuentes por respuesta; corrección desde la CLI; evaluación automática contra el conjunto etiquetado | HU-07, HU-08, HU-09 | [fases/C4-extractor.md](fases/C4-extractor.md) | v1.0 | 1 (01–02/10) | ✅ |
| C5 | **Puntaje:** ranking del mercado con índice, margen de Wilson, fuentes y brecha Maps vs IA | HU-10, HU-11, HU-12, HU-13 | [fases/C5-puntaje.md](fases/C5-puntaje.md) | v1.0 | 1–2 (02–03/10) | ✅ |
| C6 | **Informe gratis + landing:** PDF de diagnóstico para un prospecto y landing con formulario que registra prospectos → **v1.0 lista para vender** | HU-14, HU-26 | [fases/C6-informe-landing.md](fases/C6-informe-landing.md) | **v1.0** | 2 (03–04/10) | ✅ |
| C7 | **Cuentas y panel:** login con enlace mágico y panel de la clínica (índice, competidores, fuentes, evolución), con RLS probado | HU-19, HU-20 (+ HU-11/12 en el panel) | [fases/C7-cuentas-panel.md](fases/C7-cuentas-panel.md) | v1.1 | 3 | ✅ |
| C8 | **Reporte mensual y recomendaciones:** corrida mensual automática, reporte PDF con la regla del ADR-003, checklist y schema JSON-LD | HU-15, HU-17, HU-18 | [fases/C8-reporte-recomendaciones.md](fases/C8-reporte-recomendaciones.md) | v1.1 | 3–4 | ✅ |
| C9 | **Cobros manuales y atribución:** registro de pagos, estado "al día" y kit de atribución → **v1.1 lista para servir** | HU-23, HU-25 | [fases/C9-pagos-atribucion.md](fases/C9-pagos-atribucion.md) | **v1.1** | 4 | ✅ |
| C9b | **Marca y oferta:** marca Eminia (ADR-005) en la landing, el panel y el informe; landing nueva con planes y ganchos; guion de llamada (acta 2026-09-28, C-007) | apoya HU-26 | [fases/C9b-marca-oferta.md](fases/C9b-marca-oferta.md) | v1.1 | antes del 05/10 | ⚪ |
| C10 | **Agencias y marca blanca:** vista de agencia y PDFs con logo y colores | HU-16, HU-21 | [fases/C10-agencias.md](fases/C10-agencias.md) | v1.2 | 5 | ⚪ |
| C11 | **WhatsApp:** reporte mensual y alertas por WhatsApp; webhook en una Edge Function "buzón" | HU-22 | [fases/C11-whatsapp.md](fases/C11-whatsapp.md) | v1.2 | 5–6 | ⚪ |
| C12 | **Suscripción y ranking gratis:** cobro recurrente con tarjeta y ranking público por rubro y distrito → **v1.2** | HU-24, HU-27 | [fases/C12-suscripcion-ranking.md](fases/C12-suscripcion-ranking.md) | **v1.2** | 6 | ⚪ |

**Regla:** cada fase termina en algo que **puedes ver y probar**, no en "la mitad del backend".

**Plan B de la v1.0 (decidido el 26/09):** si C1–C5 se atrasan, el **05/10** se vende igual con **informes semiautomáticos**. Es la tarea **C6-T05**:
- **Control:** el jueves 02/10.
- **Nivel 1:** CLI + informe armado a mano.
- **Nivel 2:** muestra manual como la de la fase 1, si el motor no está listo.

**Prueba de fuentes completa (decidido el 26/09):** la prueba manual de 270 consultas se **reemplaza** por las **primeras corridas reales** del motor (60 respuestas por mercado, con repeticiones) más la **calibración manual** del PRD §5.4. Con eso se evalúan H2 y H3 (fase 1) sobre datos reales.

**Tareas del Director** (no las hace Claude Code; bloquean las fases indicadas):

| Tarea | Para | Cuándo |
|---|---|---|
| Crear los proyectos **dev** y **prod** en Supabase (plan gratis) y pasar las claves a `.env` y a GitHub Secrets | C1 | 28/09 |
| Crear la cuenta de **Cloudflare Pages** y conectar el repositorio | C1 | 28/09 |
| Crear la cuenta gratis de **SerpApi** y guardar la clave | C3 | 29/09 |
| **Aprobar y activar la facturación de OpenAI** (≈ US$4/mes con 5 mercados, tope US$10) y guardar la clave | C3 | 29/09 |
| Etiquetar a mano las respuestas del conjunto de evaluación (con ayuda de la CLI) | C4 | 01–02/10 |
| Armar la lista de 40 clínicas (CSV) de los mercados a vender | C2 / ventas | Semana 1 |
| Iniciar los trámites sin costo de WhatsApp Business API y de la pasarela de pagos | C11 / C12 | Semana 1 |
| Tareas legales de la estrategia (términos de OpenAI, SerpApi, Ley 29733, RUC con contador) | Antes del primer cobro | Semanas 1–2 |
| Validar la hipótesis **H9 / plan Gestionado** (C-004) en las llamadas con las primeras 40 clínicas, preguntando con los precios tentativos (S/ 990 + S/ 790/mes) | Ventas | Semanas 2–6 |

## Definición de Terminado (DoD) para cada tarea
- [ ] Cumple sus criterios de aceptación
- [ ] Tiene pruebas y todas pasan (`uv run pytest`), y `ruff` sin errores
- [ ] No rompe pruebas existentes (la CI está en verde)
- [ ] Sin secretos en el código ni en los logs
- [ ] Documentación actualizada si cambió algo visible (README técnico, ayuda de la CLI)
- [ ] Commit(s) con Conventional Commits y el ID de la tarea (p. ej., `feat(C3-T02): ...`)
- [ ] Rama fusionada a `main` mediante PR (el Director aprueba; si trabaja solo, merge local acordado)

## Definición de Terminado para cada fase
- [ ] Todas las tareas ✅
- [ ] Demo revisada por el Director
- [ ] Resumen de la fase en la bitácora
- [ ] Tag `construccion-C<n>-completa` (y `v1.0`, `v1.1`, `v1.2` al cerrar C6, C9 y C12)
