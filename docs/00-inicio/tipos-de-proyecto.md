# 🧩 Tipos de proyecto y su ruta

Lo primero que hace `/iniciar` es **identificar el tipo de proyecto**, porque el tipo cambia qué hay que investigar, qué documentos importan y qué significa "terminado". Un proyecto puede combinar tipos, por ejemplo un encargo de empresa que es una herramienta interna.

**Leyenda de profundidad por fase:** ●●● completa · ●● ligera · ● mínima · — se omite

## Tabla general

| Tipo | 1 Descubrimiento | 2 Estrategia | 3 Especificación | 4 Arquitectura | 6 Lanzamiento | Pregunta clave |
|---|---|---|---|---|---|---|
| **A. SaaS / producto propio** | ●●● | ●●● | ●●● | ●●● | ●●● | ¿Alguien pagará por esto? |
| **B. Encargo de empresa** | ●● | ● | ●●● | ●●● | ●● | ¿Qué necesita exactamente el negocio y quién aprueba? |
| **C. Freelance para clientes** | ●● | ●● | ●●● | ●● | ●● | ¿Qué está dentro y fuera del contrato? |
| **D. Personal / aprendizaje** | ● | — | ● | ● | ● | ¿Qué quiero aprender o resolver? |
| **E. Herramienta interna / automatización** | ●● | ● | ●● | ●● | ●● | ¿Cuánto tiempo o dinero ahorra? |
| **F. Open source** | ●● | ●● | ●● | ●●● | ●●● | ¿Quién lo usará y cómo contribuirán otros? |
| **G. MVP / validación de startup** | ●●● | ●●● | ●● | ● | ●● | ¿Cuál es el experimento más barato que prueba la idea? |
| **H. Migración / modernización (legacy)** | ●●● (auditar lo existente) | ● | ●●● | ●●● | ●●● | ¿Cómo cambiar sin romper lo que funciona? |
| **I. Hackathon / prototipo rápido** | ● | ● | ● | ● | ● (demo) | ¿Qué se muestra en la demo? |
| **J. Producto de datos / IA** | ●● | ●● | ●●● | ●●● | ●● | ¿Qué datos hay y cómo se mide si funciona? |
| **K. App móvil / extensión / plugin** | ●● | ●● | ●●● | ●● | ●●● (tiendas) | ¿Qué exige la tienda o la plataforma? |
| **L. Contenido técnico / curso / plantilla para vender** | ●● | ●●● | ●● | ● | ●●● | ¿Qué resultado obtiene quien lo compra? |

La **Construcción (fase 5)** existe en todos los tipos. El **Cierre (fase 7)** también: incluso un prototipo se archiva para poder retomarlo.

---

## Qué investigar por tipo (fase 1) y qué estrategia definir (fase 2)

### A. SaaS / producto propio
- **Descubrimiento:** problema y a quién le duele (entrevistas a 5–10 usuarios potenciales), competidores y alternativas actuales (incluida "no hacer nada"), tamaño de mercado aproximado (TAM/SAM/SOM), por qué ahora.
- **Estrategia:** propuesta de valor, *Lean Canvas*, modelo de precios (freemium, suscripción, por uso), canales de adquisición, métrica norte (North Star), MVP mínimo, costos de infraestructura y de las APIs de IA, aspectos legales (términos de uso, privacidad, datos personales; en Perú, Ley 29733).
- **Criterio para seguir:** ¿hay señales reales de demanda, como una lista de espera o preventas? Si no, vuelve a descubrimiento o pivotea.

### B. Encargo de empresa
- **Descubrimiento:** actores (quién pide, quién usa, quién aprueba, quién paga), proceso actual, sistemas con los que debe integrarse, restricciones (seguridad, stack obligatorio, políticas de TI), plazo.
- **Estrategia:** criterios de aceptación firmados, calendario de entregas y demos, plan de comunicación con el responsable, riesgos.
- **Clave:** toda aclaración del cliente interno queda por escrito en `memoria/actas/`.

### C. Freelance para clientes
- Igual que B, más: **propuesta y presupuesto**, alcance *dentro/fuera*, número de revisiones incluidas, forma de pago por hitos, propiedad del código, qué pasa si piden cambios (→ `/cambio` con impacto en costo).

### D. Personal / aprendizaje
- Objetivo de aprendizaje, qué tecnología practicar y un límite de tiempo. La estrategia se omite.

### E. Herramienta interna / automatización
- Tiempo o dinero ahorrado (el ROI), quién la mantendrá, dónde correrá, qué pasa si falla.

### F. Open source
- Licencia, documentación para contribuidores (CONTRIBUTING.md), versionado semántico, comunidad objetivo, sostenibilidad.

### G. MVP / validación
- Hipótesis escritas ("creemos que X hará Y; lo sabremos cuando Z"), el experimento más pequeño que las prueba, fecha límite para decidir si se sigue.

### H. Migración / legacy
- Inventario del sistema actual, dependencias, datos a migrar, pruebas que congelan el comportamiento actual antes de cambiar nada, plan de reversa (*rollback*).

### I. Hackathon / prototipo
- Guion de la demo, lo que se simula y lo que es real, límite de horas. El plan cabe en una sola fase.

### J. Datos / IA
- Fuentes de datos, calidad, privacidad, cómo evaluar el modelo o el prompt, costo por uso, sesgos.

### K. Móvil / extensión / plugin
- Requisitos de la tienda o la plataforma, permisos, revisión y publicación, actualizaciones.

### L. Contenido / plantillas para vender
- Público, resultado prometido, precio, plataforma de venta, plan de marketing.

---

## Árbol de decisión rápido (lo usa /iniciar)

```
¿Hay alguien que te paga por hacerlo?
 ├─ Sí, es mi empleador ──────────────► B (y si es para uso interno, + E)
 ├─ Sí, es un cliente externo ────────► C
 └─ No
     ├─ ¿Quieres venderlo / ganar usuarios?
     │    ├─ ¿Ya validaste que hay demanda? ─ No ─► G, luego A
     │    │                                  └ Sí ─► A (o K / L según el formato)
     ├─ ¿Es para la comunidad? ──────────────► F
     ├─ ¿Reemplaza un sistema existente? ────► H
     ├─ ¿Tienes horas o días de plazo? ──────► I
     └─ ¿Es para ti o para aprender? ────────► D (o E si automatiza algo tuyo)
Si el núcleo del producto son datos o un modelo de IA → añade J.
```
