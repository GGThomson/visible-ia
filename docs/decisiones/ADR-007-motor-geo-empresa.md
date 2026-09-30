# ADR-007 · El motor GEO es la empresa; Eminia es su primera vertical

- **Fecha:** 2026-09-29
- **Estado:** Aceptada. El diseño del sistema se escribe en `docs/motor-geo/` antes de construir más.
- **Decide:** Director
- **Consultados:** Claude Code (alternativas de operación y choques con decisiones anteriores; acta 2026-09-29)
- **Relación:** cambia el alcance del brief, la estrategia y el roadmap. No reemplaza ADR-001 a ADR-006, pero varios de ellos se revisan al diseñar cada etapa (ver «Consecuencias»).

## Contexto
- Hasta el 28/09 el proyecto era un servicio para clínicas de Lima: medir si la IA las recomienda y venderles arreglos (brief, estrategia, ADR-005 marca Eminia).
- El Director redefine la visión: el activo real es un **motor de Generative Engine Optimization (GEO)**. Mide y mejora la visibilidad de una entidad en las respuestas de las IAs y sirve para cualquier nicho cambiando su configuración.
- **Eminia** (clínicas dentales en Lima) pasa a ser el **cliente cero**: la primera vertical, que valida y financia el motor.
- Hay que decidir quién opera el motor, porque eso define el diseño del panel, de la base de datos y del cobro.

## Opciones consideradas (quién opera el motor)
| Opción | Ventajas | Desventajas | Costo / esfuerzo |
|---|---|---|---|
| 1 · Nosotros, vertical por vertical | Rápido y barato; control de calidad; ingreso alto por cliente | Crecer exige vender y atender con más gente | Bajo |
| 2 · Nosotros + agencias con marca blanca | Las agencias traen clientes; validación en muchos nichos | Menos margen por cliente; soporte a agencias; depende de que quieran revender | Medio |
| 3 · SaaS abierto (autoservicio) | La mayor escala; cada cliente cuesta pocas horas | Lo más caro y lento; precio bajo; competencia grande; el cliente suele no ejecutar los arreglos | Alto |
| **4 · Empezar interno, diseñado para abrirse** | Velocidad de la 1; deja abiertas la 2 y la 3 sin rehacer | Exige no construir partes de SaaS antes de tiempo | Bajo, algo más que la 1 |

## Decisión
1. **La empresa es el motor GEO.** Cada vertical (Eminia para dental, otras después) es una configuración del motor con su propia marca.
2. **Operación: opción 4.** Se diseña para varios operadores (nosotros, agencias y autoservicio), pero se construye y opera primero solo para uso interno. Cada apertura (agencias, autoservicio) se decide con datos, con su propio ADR.
3. **Alcance del diseño:**
   - **Entidades:** negocios locales con sede, profesionales (personas), marcas sin zona y personas públicas (qué dice la IA de ellas, no solo si las recomienda).
   - **Geografía e idioma:** global y multi-idioma.
   - **IAs:** las que sean tendencia; cada IA es un adaptador que se agrega o se retira sin cambiar el resto.
4. **Orden de trabajo (Director, 29/09):**
   1. Diseñar el sistema completo en teoría, etapa por etapa (`docs/motor-geo/`).
   2. Construir el producto con su panel a ese nivel.
   3. Recién entonces salir a buscar clientes.
   Esto **reemplaza** «ventas desde el 05/10» del brief y de ESTADO.
5. **Arquitectura propuesta por el Director** (se detalla y valida en el diseño):
   - Python (`visible-ia`) hace el trabajo pesado: medición, LLM, métricas y PDF, como CLI o API sin interfaz.
   - n8n solo orquesta y comunica.
   - Google Tag Manager entrega los cambios en la web del cliente.
   - Tres motores: **Adquisición**, **Ejecución** y **Retención**.
6. **Reglas de código:**
   - Nada del nicho escrito a mano en `src/`.
   - Preguntas, intenciones, taxonomías y vocabulario viven en archivos de configuración por industria.

## Consecuencias
- **Positivas:**
  - Cada vertical nueva cuesta configuración, no código.
  - El diseño evita rehacer la base de datos y el panel al abrir a agencias o autoservicio.
  - Lo ya construido (C1–C9, C9b y C-010) se reutiliza como la primera versión del motor.
- **Negativas / lo que aceptamos:**
  - **Se posterga la venta y con ella la validación del brief:** 3 clínicas pagando o S/ 2,500 al 08/11, y el criterio de replanteo tras 50 clínicas y 10 agencias. Hay que redefinir cuándo y cómo se valida.
  - Más trabajo de diseño antes de ingresos. El presupuesto de validación (US$20) sigue vigente mientras no se decida otro.
- **Choques a resolver en el diseño (no se deciden aquí):**
  1. **Envío masivo de WhatsApp y correo** (motor de adquisición) frente a «sin envíos masivos» del brief, las reglas de Meta, la Ley 29733 y la normativa contra el spam.
  2. **Schema JSON-LD vía GTM:** hay que verificar si los rastreadores de las IAs ejecutan JavaScript. Si no lo hacen, el schema inyectado no les llega.
  3. **Scraping y Gemini:** el ADR-002 prohíbe automatizar las apps de consumo. Cada IA nueva necesita una vía permitida.
  4. **Automatizar Google Business Profile:** su API exige aprobación de Google, y el PRD §7 excluye editar perfiles del cliente.
  5. **Configuración por industria** repartida hoy en varios archivos (`data/plantillas-preguntas.csv`, `nicho.toml`, `recomendaciones.toml`, `checklist.toml`) y unas 100 palabras del nicho escritas a mano en `src/`.
- **Si cambiamos de opinión:** volver a la opción 1 no exige rehacer nada. Pasar a la 2 o a la 3 requiere su propio ADR con datos de demanda.
