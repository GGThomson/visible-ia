# 🤝 Flujo del equipo de planificación (tú + Claude + Gemini + Claude Code)

## 1. Roles
| Miembro | Rol | Fortaleza | Dónde trabaja |
|---|---|---|---|
| **Tú** | Director: decides, apruebas, priorizas | Criterio, contexto de negocio | Todas partes |
| **Claude (web o app)** | Arquitecto y planificador | Razonamiento, estructura, redacción | Chat |
| **Gemini** | Revisor crítico e investigador | Contexto enorme, búsqueda, segunda opinión | Chat o CLI |
| **Claude Code** | Ejecutor y secretario | Lee y escribe el repo, código, Git | Terminal / app |

La clave es que **Claude Code también es el secretario del equipo**: todo lo que se decide en los chats vuelve al repositorio mediante `/acta`.

## 2. El problema de la memoria y cómo lo resolvemos

Las IAs olvidan porque cada chat tiene un límite (la ventana de contexto), y al empezar un chat nuevo se pierde todo. La solución no consiste en buscar una IA con memoria infinita. Consiste en **sacar la memoria de las IAs y ponerla en archivos**:

1. **El repositorio es el cerebro.** Las IAs solo "piensan" en él por un rato.
2. **La memoria está en capas** (ver el README, sección 7). Las IAs leen primero lo corto (AGENTS.md y ESTADO.md) y buscan el detalle solo cuando lo necesitan. Por eso el proyecto puede crecer sin límite sin saturar a nadie.
3. **Siempre se cierra el ciclo.** Toda conversación termina en un archivo: una acta, un ADR, la bitácora o el ESTADO.
4. **Git guarda la historia.** Aunque ESTADO.md se reescriba, `git log` y la bitácora conservan todo lo que pasó.

## 3. Protocolo de una reunión de planificación

```
 ┌─ 1. /contexto <tema>        Claude Code prepara el paquete de 1 página
 │
 ├─ 2. Pegas el paquete en ────► Claude web  → propone
 │                         └───► Gemini      → critica / investiga
 │      (opcional: le pasas a cada uno la respuesta del otro para un 2º round)
 │
 ├─ 3. Cada uno termina con su ACTA (formato fijo)
 │
 ├─ 4. /acta + pegas las actas  Claude Code compara y te pregunta qué decides
 │
 └─ 5. Tú decides ─────────────► ADR + tareas + ESTADO actualizados + commit
```

**Consejos:**
- Usa un **chat nuevo por tema**. Los chats cortos y enfocados rinden mucho mejor que uno eterno.
- En Claude web puedes crear un **Proyecto** por cada proyecto de software y subir ahí `AGENTS.md`, `ESTADO.md`, `brief.md` y `prd.md`. Actualízalos cuando cambien de fase.
- En Gemini puedes hacer lo mismo con un **Gem** que tenga esos archivos como conocimiento.
- Pide siempre a Gemini que actúe como abogado del diablo. Su valor está en encontrar lo que falta.

## 4. Para que tú nunca te pierdas
| Si quieres saber… | Mira |
|---|---|
| Dónde estoy y qué sigue | `/estado` o `memoria/ESTADO.md` |
| Qué hice la semana pasada | `memoria/bitacora/` |
| Por qué decidimos X | `docs/decisiones/` |
| Qué ideas quedaron pendientes | `memoria/cambios-pendientes.md` |
| Qué opinaron las IAs sobre X | `memoria/actas/` |
| Qué cambió en el código | GitHub → Commits / Pull Requests |

**Hábito de 2 minutos:** empieza cada sesión con `/estado` y termínala siempre con `/cerrar-sesion`.

## 5. Niveles de integración (empieza por el 1)

| Nivel | Cómo | Ventaja | Esfuerzo |
|---|---|---|---|
| **1. Manual (recomendado al inicio)** | Copias y pegas el contexto con `/contexto` y las actas con `/acta` | Funciona hoy, control total, sin configuración | Bajo |
| **2. Proyectos / Gems** | Subes los archivos clave a un Proyecto de Claude y a un Gem de Gemini | Menos copiar y pegar | Bajo |
| **3. Gemini dentro de Claude Code (MCP)** | Claude Code consulta a Gemini directamente | Segunda opinión automática | Medio |
| **4. NotebookLM como archivo consultable (MCP)** | Subes `docs/` y `memoria/` a un cuaderno y lo consultas desde Claude Code | Preguntas a todo el historial con citas | Medio |
| **5. Misma carpeta, dos agentes** | Claude Code y Antigravity CLI trabajan sobre el mismo repo (AGENTS.md sirve a ambos) | Colaboración real sobre archivos | Medio-alto |

Los detalles de los niveles 3 a 5 están en `mcp-integraciones.md`.
