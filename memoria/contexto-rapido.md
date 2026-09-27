# 📦 Contexto rápido — para pegar en cualquier IA
<!-- Lo regenera /contexto. Máximo ~1 página. Pégalo al inicio de un chat nuevo con Gemini o Claude web. -->

Eres parte del equipo de planificación de un proyecto de software. El equipo lo forman: **Director (humano, decide)**, **Claude y Gemini (planificadores: proponen, investigan, critican)** y **Claude Code (ejecutor)**. No tienes acceso al repositorio; lo que sigue es el estado actual.

## Proyecto
- **Nombre:** visible-ia
- **Tipo:** A (SaaS) + J (producto de datos / IA)
- **Propósito en una frase:** medir si ChatGPT, Gemini y Google (Modo IA) recomiendan a un negocio local frente a su competencia, y darle arreglos concretos para aparecer.
- **Para quién:** clínicas de salud electiva de ticket alto en Lima Top (Miraflores, San Isidro, Surco): implantología y estética dental, estética y dermatología. Además, agencias de marketing como canal (marca blanca).
- **Qué es éxito:** S/ 2,500 en preventas o pilotos (3 clínicas o 2 agencias) y > 25 % de respuesta a los informes gratis.

## Estado
- **Fase:** 5 · Construcción. **Hecho (26/09):** C1 base (CLI Python, CI, Supabase dev/prod con RLS, job diario, landing "Próximamente" en https://visible-ia.pages.dev) y C2 mercados (plantillas, mercados, clínicas desde CSV, alias). Sigue C3 (motor; necesita aprobar la facturación de OpenAI). Arquitectura aprobada: Python sin servidor (Supabase + GitHub Actions + Cloudflare Pages), ADR-003 = 3 repeticiones + prueba de 2 proporciones + ventana de 3 meses. Plan C1–C12 (46 tareas) con Plan B para vender el 05/10. Antes: PRD v1 congelado el 26/09: entregas v1.0 "Vender" (semanas 1–2: informe gratis + landing), v1.1 "Servir" (3–4), v1.2 "Escalar" (5–6); 10 plantillas de preguntas por rubro; índice = % de respuestas donde aparece la clínica, con margen de Wilson; pendiente ADR-003 (repeticiones: con 30 respuestas al mes el margen es ±15–17 puntos). Estrategia aprobada el 26/09: métrica norte = sedes activas pagando con reporte entregado; cobro inicial con link de pago manual; falta definir si los precios incluyen IGV (RUC pendiente). Construcción del 28/09 al 08/11/2026, con ventas desde el 05/10.
- **Descubrimiento aprobado (26/09), con una muestra de 31 consultas manuales:**
  - 30 de 30 respuestas nombran clínicas concretas.
  - La fuente principal es la ficha de Google Maps; le siguen Doctoralia, la web propia y las redes.
  - Las respuestas varían mucho entre IAs.
- **Qué ya está decidido (no reabrir sin motivo):**
  - Nicho, canal dual y precios: clínica S/ 349/mes + S/ 490 de setup; agencia S/ 690/mes (hasta 5 sedes).
  - Índice de presencia con ≥ 3 repeticiones, sin prometer "puesto #1".
  - Presupuesto de validación ≤ US$20 en total.
  - **No automatizar las apps de consumo** (scraping de ChatGPT o Gemini): violaría sus términos.
  - Perplexity queda fuera del MVP (ADR-001).
  - **Motor de medición (ADR-002):** API de OpenAI (ChatGPT) + Google Modo IA vía SerpApi (gratis al inicio) + muestra manual mensual de Gemini. Texto 12 meses, métricas mientras el cliente esté activo + 12 meses, nada de pacientes.
  - Marca blanca para agencias: aceptada.
  - **Hipótesis H9 (C-004), no decidida:** plan Gestionado, en el que ejecutamos los arreglos. Tentativo: S/ 990 de puesta a punto + S/ 790/mes (medición, reporte, 3 mejoras al mes y una llamada). Se valida en las llamadas con las primeras 40 clínicas.
- **Stack (ADR-004):** Python 3.12 (uv, pytest, typer, OpenAI SDK, rapidfuzz, jinja2, Playwright), Supabase (Postgres + RLS + Auth + Storage), GitHub Actions (corridas, job diario), Cloudflare Pages (landing y panel estáticos). US$0 fijo; ≈ US$4/mes de API con 5 mercados.

## Tema de esta conversación: riesgo legal del motor de medición (C-001)
El producto necesita consultar a las IAs de forma repetida (10 preguntas × 3 repeticiones por mercado y mes), **guardar las respuestas y analizarlas** (clínicas mencionadas, posición, fuentes). Medir con API cuesta poco (≈ US$5–29 al mes para 5–30 mercados). El problema son los términos de uso.

**Lo que encontramos (fuentes oficiales, 26/09/2026):**
- **API de Gemini con grounding (Search):**
  - Prohíbe *"cache, frame, syndicate, resell, **analyze**, train on, or otherwise learn from Grounded Results"*.
  - Solo permite guardar el texto ≤ 2 años para casos puntuales y obliga a mostrar las "Search Suggestions".
  - **Maps:** caché ≤ 90 días y prohíbe exportar sus datos.
  - En el nivel gratuito, el grounding de Gemini 3.x no está disponible, y Gemini 2.5 Flash tiene un tope de 20 llamadas al día.
- **OpenAI:**
  - Los términos de consumidor prohíben *"automatically or programmatically extract data or Output"* de la app.
  - Por **API** el cliente *"own[s] the Output"*. No hallamos restricciones específicas sobre *web search*; falta verificarlo. La API admite `user_location` (Lima).
- **Google Modo IA vía proveedores SERP:**
  - **SerpApi** asume la responsabilidad de la recolección, *"but not for how that data is ultimately used"*. Su Legal Shield (US$2M) solo está desde el plan de US$150/mes.
  - **DataForSEO** §7.1 dice que los datos *"shall not be used to compete with or adversely affect the business interests of the search engine providers"*, y el cliente lo indemniza.
  - Google demandó a SerpApi (dic. 2025). La jueza desestimó las demandas DMCA el 20/07/2026, pero Google puede presentar una demanda corregida.
- **Competidores:** Otterly, Peec AI y Profound miden **automatizando la interfaz web** (lo que ve el usuario) y usan API solo como excepción. CreceRank repite cada prompt ≥ 3 veces, sin decir si usa API o la interfaz.
- **Ley 29733 (Perú):** las respuestas incluyen nombres de médicos.

**Opciones que evaluamos:**
- **A. Automatizar la interfaz**, como los competidores. Riesgo alto; el Director ya lo descartó.
- **B. Solo APIs, incluida Gemini con grounding.** Choca con el "analyze".
- **C. Recomendada por Claude Code:**
  - API de OpenAI para ChatGPT (guardar y analizar permitido).
  - Google Modo IA vía DataForSEO (o SerpApi cuando haya ingresos).
  - Gemini sin motor: una muestra manual mensual como "calibración".
  - Guardar el texto completo 12 meses y las métricas derivadas mientras el cliente esté activo más 12 meses. Nada de pacientes.
- **D. Solo la API de OpenAI.** Es lo más seguro, pero deja fuera a Google.
- **E. Consultar a Google** (Vertex AI u otra vía) si existe un uso permitido para medir la visibilidad.

## Lo que necesito de ti
1. Critica el análisis: ¿leímos bien los términos? ¿Hay vías que no vimos, como Vertex AI, Bing/Copilot, AI Overviews o un panel de usuarios con opt-in?
2. Evalúa las opciones C y E con riesgos concretos. ¿Es defendible vender un índice que mide "ChatGPT + Google Modo IA + muestra de Gemini"?
3. Recomienda qué datos guardar y por cuánto tiempo, y qué revisar con un abogado en Perú (Ley 29733).
4. **Al final**, entrega un ACTA con este formato exacto:

```
## ACTA
Fecha: 
Participante: (Gemini / Claude web)
Tema: 
Propuestas:
- 
Recomendación:
Preguntas abiertas para el Director:
- 
Tareas sugeridas:
- 
```
