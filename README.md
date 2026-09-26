# 🧭 Plantilla de Proyecto con Equipo de IAs

Sistema reutilizable para llevar **cualquier proyecto de programación** desde la idea hasta el mantenimiento. El equipo de planificación está formado por **tú + Claude + Gemini**, y **Claude Code** es el ejecutor.

> **Regla de oro:** nada importante vive solo en un chat. Todo lo que se decide se escribe en este repositorio. Por eso la memoria es "infinita": está en archivos versionados con Git, no en la ventana de contexto de una IA.

---

## 1. ¿Cómo funciona? (en 30 segundos)

```
 IDEA ──► 0. Inicio ──► 1. Descubrimiento ──► 2. Estrategia ──► 3. Especificación
                                                                      │
 MANTENIMIENTO ◄── 7. Cierre ◄── 6. Lanzamiento ◄── 5. Construcción ◄── 4. Arquitectura y Plan
        │
        └──► (cambios nuevos vuelven a entrar por /cambio en cualquier momento)
```

- **Fases 0 a 4**: se planifica todo. Aquí conversan tú, Claude (chat) y Gemini. Claude Code redacta los documentos.
- **Fase 5**: Claude Code construye tarea por tarea, siguiendo el plan. Cada tarea usa una rama de Git y termina en un *commit*.
- **Fases 6 y 7**: lanzamiento, retrospectiva y archivo, para retomar el proyecto cuando quieras.

No todos los proyectos recorren todas las fases con la misma profundidad. El tipo de proyecto lo decide; ver `docs/00-inicio/tipos-de-proyecto.md`.

---

## 2. Mapa de la plantilla

| Carpeta / archivo | Para qué sirve | ¿Quién lo lee? |
|---|---|---|
| `memoria/ESTADO.md` | **Tablero**: dónde estamos, qué sigue y qué está bloqueado. | Tú, siempre. Todas las IAs, al empezar. |
| `memoria/contexto-rapido.md` | Resumen de 1 página para **pegar en cualquier chat** (Gemini, Claude web). | IAs de chat |
| `memoria/cambios-pendientes.md` | Bandeja de entrada: ideas, cambios y bugs que surgen en cualquier momento. | Tú + Claude Code |
| `memoria/bitacora/` | Diario de cada sesión de trabajo. | Bajo demanda |
| `memoria/actas/` | Actas de las reuniones de planificación con las IAs. | Bajo demanda |
| `docs/decisiones/` | ADRs: cada decisión importante con su porqué. | Bajo demanda |
| `docs/00-inicio … 07-cierre` | Los entregables de cada fase. | Según la fase |
| `docs/guias/` | Guías para aprender Git/GitHub, el flujo con IAs y MCP. | Tú |
| `AGENTS.md` | Reglas universales para **todas** las IAs. | Claude Code, Gemini/Antigravity, Cursor… |
| `CLAUDE.md` / `GEMINI.md` | Puntos de entrada de cada herramienta (apuntan a AGENTS.md). | Automático |
| `.claude/commands/` | Comandos `/` para Claude Code. | Tú los ejecutas |

---

## 3. Primeros pasos (una sola vez en tu computadora)

1. Instala **Git**: https://git-scm.com/downloads
2. Crea una cuenta en **GitHub** e instala **GitHub CLI** (`gh`): https://cli.github.com/, y luego ejecuta `gh auth login`.
3. Instala **Claude Code** siguiendo la documentación oficial: https://docs.claude.com/en/docs/claude-code/overview
4. (Opcional) Instala la CLI de Gemini. Ojo: Google retiró *Gemini CLI* para cuentas gratuitas/Pro/Ultra en junio de 2026; su sucesora es **Antigravity CLI (`agy`)**. Revisa `docs/guias/mcp-integraciones.md`.
5. Guarda esta plantilla en GitHub como **Template repository**: Settings → marca *Template repository*.

Lee `docs/guias/git-github-para-empezar.md`. Está escrito para aprender desde cero.

---

## 4. Empezar un proyecto nuevo

```bash
# Opción A: script incluido (crea carpeta, git y repo privado en GitHub)
bash scripts/nuevo-proyecto.sh mi-proyecto

# Opción B: desde GitHub → "Use this template" → clonar
```

Luego, dentro de la carpeta:

```bash
claude            # abre Claude Code
/iniciar          # entrevista inicial: tipo de proyecto, propósito, ruta de fases
```

---

## 5. Los comandos (tu control remoto)

| Comando | Cuándo usarlo | Qué hace |
|---|---|---|
| `/iniciar` | Al crear el proyecto | Te entrevista, clasifica el proyecto y arma la ruta de fases |
| `/fase` | Para avanzar la planificación | Trabaja el entregable de la fase actual contigo |
| `/planificar` | Al terminar la especificación | Genera roadmap, fases y tareas ejecutables |
| `/siguiente` | En construcción | Toma la próxima tarea, crea la rama, la implementa y la prueba |
| `/cambio <texto>` | En **cualquier** momento | Registra una modificación o idea y evalúa su impacto |
| `/decision <tema>` | Ante una elección importante | Crea un ADR con opciones y consecuencias |
| `/contexto` | Antes de hablar con Gemini/Claude web | Actualiza `contexto-rapido.md` para que lo pegues |
| `/acta` | Después de una reunión con las IAs | Integra lo acordado en la memoria |
| `/estado` | Cuando te sientas perdido | Te explica en simple dónde estás y qué sigue |
| `/cerrar-sesion` | **Siempre al terminar el día** | Actualiza ESTADO, bitácora y hace commit + push |
| `/archivar` | Al terminar el proyecto | Retrospectiva, versión final y guía para retomarlo |

---

## 6. El ciclo diario (lo que realmente harás)

```
1. claude              → Claude Code lee ESTADO.md automáticamente
2. /estado             → (opcional) recordatorio de dónde vas
3. /siguiente  o  /fase
4. ¿Surgió una idea?   → /cambio "..."   (no interrumpes lo que haces)
5. ¿Hay que decidir algo grande? → /contexto → llevas el tema a Gemini y a Claude web
   → decides → /acta
6. /cerrar-sesion      → todo queda guardado en GitHub
```

---

## 7. Cómo nunca perder el contexto (la memoria en capas)

| Capa | Archivo | Tamaño | Cuándo se carga |
|---|---|---|---|
| 1. Reglas | `AGENTS.md` | Pequeño, casi fijo | Siempre, automático |
| 2. Estado | `memoria/ESTADO.md` | ≤ 1 página | Siempre, automático (hook de inicio) |
| 3. Documentos de fase | `docs/0X-*` | Medio | Cuando se trabaja esa fase |
| 4. Historia | bitácora, actas, ADRs | Crece sin límite | Solo cuando se necesita |
| 5. (Opcional) Búsqueda | NotebookLM con los docs del repo | Ilimitado | Consultas a todo el historial |

El secreto está en que las capas 1 y 2 **siempre se mantienen cortas**. Así ninguna IA se satura. La historia crece sin límite, pero solo se lee por partes. Los detalles están en `docs/guias/flujo-equipo-ia.md`.
