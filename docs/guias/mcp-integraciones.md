# 🔌 Integraciones: MCP, Gemini y NotebookLM

> ⚠️ Estas herramientas cambian rápido. Los comandos que siguen corresponden a septiembre de 2026; verifica siempre en el repositorio oficial de cada una. Son **opcionales**: el sistema funciona completo solo con el nivel 1 (copiar y pegar).

## ¿Qué es MCP?
El **Model Context Protocol** es un estándar para conectar una IA con herramientas externas. Funciona como un "enchufe universal": instalas un *servidor MCP* y Claude Code gana nuevas capacidades, como hablar con Gemini o consultar NotebookLM.

- Ver los MCP instalados: comando `/mcp` dentro de Claude Code.
- Añadir uno: `claude mcp add <nombre> -- <comando>`.
- Ámbito: `-s user` (todos tus proyectos) o `-s project` (se guarda en `.mcp.json` dentro del repo, compartido).
- Cada MCP ocupa espacio de contexto con sus herramientas. **Actívalos solo cuando los uses.**

## Nota importante sobre Gemini CLI
En junio de 2026 Google **retiró Gemini CLI** para los usuarios de los planes gratis, Google AI Pro y Ultra. Su sucesora es **Antigravity CLI (`agy`)**. Si usas una API key de Google AI Studio o Vertex, las integraciones por API siguen funcionando.

---

## Nivel 3 · Gemini dentro de Claude Code

**Opción A: MCP por API key (la más estable).** Consigue una API key gratuita en Google AI Studio (https://aistudio.google.com/).
```bash
# Ejemplo con el servidor comunitario @rlabs-inc/gemini-mcp
claude mcp add gemini -s user -- env GEMINI_API_KEY=TU_CLAVE npx -y @rlabs-inc/gemini-mcp
```

**Opción B: MCP que usa tu CLI local** (`gemini-mcp-tool`, que ya soporta Antigravity CLI). Instala primero `agy` según la documentación de Google y luego sigue el README del repositorio https://github.com/jamubc/gemini-mcp-tool.

**Uso dentro de Claude Code:**
- "Pídele a Gemini que revise críticamente `docs/05-plan/roadmap.md` y dame sus riesgos."
- "Consulta a Gemini sobre las alternativas de base de datos para el ADR-003."

⚠️ Los servidores MCP comunitarios los mantienen terceros. Revisa el repo antes de instalar y **nunca** pongas tu API key dentro de un archivo que se sube a Git.

---

## Nivel 4 · NotebookLM como archivo consultable

NotebookLM responde **solo con base en las fuentes que le subes, con citas**. Eso lo hace ideal como memoria "de biblioteca" de proyectos grandes o archivados.

**Uso manual (sin MCP):**
1. Crea un cuaderno por proyecto en https://notebooklm.google.com
2. Sube `docs/` y `memoria/`, o conecta una carpeta de Google Drive sincronizada.
3. Pregunta cosas como "¿por qué elegimos Postgres?" o "¿qué cambios pidió el cliente en marzo?".

**Con MCP (Claude Code consulta el cuaderno):**
```bash
claude mcp add notebooklm -- npx notebooklm-mcp@latest
```
La primera vez te pedirá iniciar sesión con Google en el navegador. Repositorio: https://github.com/PleasePrompto/notebooklm-mcp

**Regla:** NotebookLM es una **copia de consulta**. La fuente de verdad sigue siendo el repositorio en GitHub. Resincroniza las fuentes al cerrar cada fase.

---

## Nivel 5 · Dos agentes sobre la misma carpeta
- Claude Code lee `CLAUDE.md` y Gemini/Antigravity lee `GEMINI.md`. Ambos importan `AGENTS.md`, así que comparten las mismas reglas.
- Úsalos **por turnos, no al mismo tiempo**, sobre los mismos archivos. Lo ideal es que Gemini revise y Claude Code ejecute.
- Revisión automática de PRs: existe *Gemini Code Assist* para GitHub, que comenta los Pull Requests.

## Archivo de ejemplo
`.mcp.json.example` muestra cómo quedaría una configuración de proyecto. Cópialo como `.mcp.json` solo si todo el equipo usará los mismos MCP y **sin claves dentro**; las claves van en variables de entorno.
