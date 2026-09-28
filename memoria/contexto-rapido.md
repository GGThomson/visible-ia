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
- **Fase:** 5 · Construcción (al 27/09). **Hecho:** C1–C9. **v1.0 "Vender" cerrada** (tag `v1.0`): motor (ChatGPT API + Google Modo IA vía SerpApi), extractor gpt-5-nano (precisión 98 %, exhaustividad 95 %), puntaje con margen de Wilson y regla del ADR-003, informe gratis en PDF, landing con formulario (https://visible-ia.pages.dev). **C7:** panel de la clínica (https://visible-ia.pages.dev/panel/) con acceso por enlace de WhatsApp y aislamiento por cliente (RLS). **C8:** corrida mensual que pide el OK del Director, reporte mensual con calibración contra las apps, checklist priorizado y schema JSON-LD. Primer mercado real: Implantología · Miraflores (34 clínicas; Smiles Peru lidera con 50 %; 5 clínicas con brecha Maps vs IA). **C9 · v1.1 "Servir" cerrada** (tag `v1.1`): pagos manuales con estado al día / vence pronto / atrasado (5 días de gracia, aviso 7 días antes, IGV configurable hasta que el contador defina el régimen) y aviso diario de atrasados; kit de atribución (pregunta de intake, UTM, cupón `IA-<nombre>`) con el conteo mensual "por IA" en el panel y en el reporte. Ventas desde el 05/10. **Marca: Eminia** («Que la IA te nombre a ti», ADR-005; Prominia de respaldo según INDECOPI/.pe); oferta: Diagnóstico gratis / Plan Medir (S/ 349/mes + S/ 490) / Plan Gestionado (S/ 790/mes + S/ 990), sin permanencia, precio fundador para las 5 primeras y garantía de entrega (acta 2026-09-28). Sigue C9b (marca y oferta) y luego C10 (agencias y marca blanca).
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

## Tema de esta conversación
(Lo completa `/contexto` con el tema que se lleve a Gemini o Claude web. El tema del riesgo legal del motor (C-001) ya se resolvió en el ADR-002.)
