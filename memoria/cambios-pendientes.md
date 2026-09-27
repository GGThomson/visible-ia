# 📥 Bandeja de cambios, ideas y bugs
<!-- Todo lo que surge "en el camino" entra aquí con /cambio. Nada se pierde y nada interrumpe la tarea en curso. -->

## Cómo se clasifica
- **Tipo:** 🐛 bug · ✨ mejora · 🔁 cambio de alcance · 💡 idea futura · ❓ pregunta
- **Impacto:** Bajo (≤ 1 tarea) · Medio (varias tareas) · Alto (cambia especificación o arquitectura → requiere `/decision`)
- **Destino:** tarea nueva en fase X · próxima versión · descartado (con motivo)

## Sin clasificar
| ID | Fecha | Tipo | Descripción | Impacto | Destino |
|---|---|---|---|---|---|
| — | | | | | |

## Clasificados (historial)
| ID | Fecha | Tipo | Descripción | Impacto | Destino | Estado |
|---|---|---|---|---|---|---|
| C-005 | 2026-09-26 | 🔁 cambio de alcance | C3-T05 solo admitía muestras manuales de ChatGPT y Gemini, pero C4-T05 espera las 31 de la fase 1 (incluye 10 de Google Modo IA a mano y preguntas de 8 mercados, 2 sobre "Lima"). Se agrega la superficie `google_ai_mode_manual` y la muestra se importa en dev con mercados inactivos | Bajo (1 migración, sin tocar el índice) | C3-T05 | ✅ Decidido por el Director; 0003 aplicada en dev, **pendiente en prod** |
| C-004 | 2026-09-26 | 💡 idea (hipótesis de negocio) | Plan **Gestionado**: nosotros ejecutamos los arreglos (ficha de Google, Doctoralia, web/schema, redes) además de medir. Se valida con las primeras 40 clínicas. Sin cambios de código por ahora. **Propuesta tentativa (Director, 26/09; precios para preguntar en las llamadas, no definitivos):** **puesta a punto S/ 990** (pago único: ficha de Google, Doctoralia, web y plan de reseñas) + **S/ 790/mes** (medición, reporte, 3 mejoras al mes y una llamada corta) | Bajo (sin código; toca hipótesis y precios) | Validación comercial, semanas 2–6 → **H9** en `investigacion.md` | ✅ Registrado con precios tentativos; se definen tras las llamadas |
| C-002 | 2026-09-26 | 🔁 cambio de alcance | Reemplazar la prueba manual de 270 consultas por las primeras corridas reales + calibración manual | Medio | Construcción (C3–C5) | ✅ Decidido por el Director |
| C-003 | 2026-09-26 | ✨ mejora | Plan B de la v1.0: informes semiautomáticos si C1–C5 se atrasan | Bajo | C6-T05 | ✅ Decidido por el Director |
| C-001 | 2026-09-26 | ❓ pregunta | Riesgo legal del motor de medición (los términos de grounding de Gemini prohíben "analyze") | Alto | Fase 2 | ✅ Resuelto: ADR-002 (opción C) |
