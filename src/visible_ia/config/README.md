# Capa 1 · Configuración

Nichos, planes, clientes y accesos. Nada del nicho se escribe en el código: vive aquí.

- `ajustes.py`: variables de entorno y secretos (antes `config.py`). `from visible_ia.config import get_settings` sigue funcionando.
- `rutas.py`: **el único lugar que sabe dónde están los archivos**. Ningún módulo sube carpetas con `parents[n]`; una prueba lo verifica.
- `nichos.py`: vocabulario del nicho (antes `nicho.py`, que queda como alias hasta el paso 8).
- `nichos/<nicho>/`: la configuración de cada nicho. Hoy solo `dental/` (Eminia):
  - `nicho.toml`: vocabulario y categorías.
  - `preguntas.csv`: plantillas de preguntas.
  - `recomendaciones.toml`: acciones del plan.
  - `semaforo.toml`: cortes del semáforo frente al líder.
  - `checklist.toml`: tareas de la puesta a punto.
  - `dominios.csv`: tipos de fuente por dominio.
- **Llegará después:** `clientes`, `pagos` y `planes` (cada plan es una combinación de módulos).
- Acta: `memoria/actas/2026-09-29-mapa-del-sistema.md`.
