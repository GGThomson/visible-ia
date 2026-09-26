# 📦 Contexto rápido — para pegar en cualquier IA
<!-- Lo regenera /contexto. Máximo ~1 página. Pégalo al inicio de un chat nuevo con Gemini o Claude web. -->

Eres parte del equipo de planificación de un proyecto de software. El equipo lo forman: **Director (humano, decide)**, **Claude y Gemini (planificadores: proponen, investigan, critican)** y **Claude Code (ejecutor)**. No tienes acceso al repositorio; lo que sigue es el estado actual.

## Proyecto
- **Nombre:** visible-ia
- **Tipo:** A (SaaS) + J (producto de datos / IA)
- **Propósito en una frase:** medir si ChatGPT, Gemini y Google (Modo IA) recomiendan a un negocio local frente a su competencia, y darle arreglos concretos para aparecer.
- **Para quién:** clínicas de salud electiva de ticket alto en Lima Top (Miraflores, San Isidro, Surco): implantología y estética dental, estética y dermatología. Además, agencias de marketing como canal (marca blanca).
- **Qué es éxito:** S/ 2,500 en preventas o pilotos (3 clínicas o 2 agencias) y > 25 % de respuesta a los informes gratis. Replanteo si 50 clínicas y 10 agencias contactadas no pagan nada.

## Estado
- **Fase:** 2 · Estrategia (ligera). La fase 1 se aprobó el 26/09. Construcción del 28/09 al 08/11/2026, con ventas desde el 05/10.
- **Resultado del descubrimiento (muestra de 31 consultas):**
  - En ChatGPT, Gemini y Google Modo IA, 30 de 30 respuestas nombran clínicas concretas.
  - La fuente principal es la **ficha de Google Maps**; le siguen Doctoralia, la web propia y las redes (Instagram/Facebook).
  - En 7 de 10 preguntas las 3 IAs coinciden en una clínica "líder". Fuera de ella, las respuestas varían mucho.
- **Próximo:** prueba completa de 270 consultas (30 preguntas × 3 superficies × 3 repeticiones) en la semana 1. Antes, se propone probar la API gratuita de Gemini (Search + Maps) para automatizar sus repeticiones. Está pendiente de aprobación y tiene un riesgo: Maps solo admite inglés.
- **Qué ya está decidido (no reabrir sin motivo):**
  - Nicho, canal dual (directo + agencias) y precios: clínica S/ 349/mes por sede + S/ 490 de setup; agencia S/ 690/mes (hasta 5 sedes) + S/ 99 por sede extra.
  - No prometer "puesto #1": índice de presencia con muestreo repetido, calibrado API vs app.
  - SaaS (monitoreo, reportes, schema) separado del servicio (setup).
  - Contacto 100 % en frío, uno por uno, sin envíos masivos.
  - Presupuesto de validación ≤ US$20 en total, solo planes gratuitos. Donde la API cueste: consultas manuales en las apps + script que analiza las respuestas. Nada de scraping ni automatización de las apps de consumo.
  - WhatsApp API, pasarela de pagos y dominio se pagan con el dinero del primer cliente.
  - Perplexity queda fuera del MVP por su baja adopción en Perú y porque sin sesión no localiza bien Lima. Se reevalúa en la v2 con la API Sonar (ADR-001).
  - 8 módulos: motor de consultas, extractor, puntaje, informes PDF, panel web, recomendaciones, WhatsApp, cuentas/pagos.
- **Stack:** por definir en la fase 4 (restricción: planes gratuitos).

## Tema de esta conversación
—

## Lo que necesito de ti
1. Analiza el tema considerando lo ya decidido.
2. Da riesgos, alternativas y una recomendación clara.
3. **Al final**, entrega un ACTA con este formato exacto:

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
