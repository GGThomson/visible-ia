# Acta 2026-09-29 · Mapa del sistema del motor GEO

- **Participantes:** Director, Claude web (diseño), Claude Code (propuesta de reorganización del repo)
- **Tema:** mapa del sistema en 3 capas y 7 módulos; cómo reorganizar el repo sin cambiar lo que hace
- **Contexto usado:** diseño del 29/09 en https://claude.ai/artifact/MQih4kBtCShy8ajLdGQVMa y [ADR-007](../../docs/decisiones/ADR-007-motor-geo-empresa.md)

## Decisión del Director (29/09)
- **3 capas:**
  - **Configuración:** nichos, planes, clientes y accesos.
  - **Módulos:**
    1. Adquisición
    2. Motor GEO (medir + diagnosticar)
    3. Motor de mejoras
    4. Verificador
    5. Registro de acciones
    6. Aprendizaje
    7. Informes
  - **Operación:** calendario (GitHub Actions), bandeja de aprobación en el panel, panel y base de datos con costos.
- **Mejoras por nivel:**
  - **Automático:** consistencia de datos.
  - **Con OK del Director:**
    - Reseñas y perfil, por la API de Google Business Profile.
    - Páginas, por la API de WordPress.
    - Schema, por WordPress o GTM.
  - **Guiado:** Bing Places, directorios y menciones.
  - **Cliente:** pedir reseñas y aprobar los textos de salud.
- **Registro sin borrar.** Cada acción guarda:
  - brecha, acción, contenido, dónde se hizo y quién la aprobó;
  - prueba: captura, enlace y fecha;
  - estado: preparada, aprobada, publicada, verificada o caída;
  - efecto a las 4 y a las 8 semanas, frente a negocios sin la acción.
- **Informes:**
  - diagnóstico;
  - puesta a punto;
  - mensual: resultado, trabajo hecho con pruebas, efecto y plan;
  - alertas.
- **Planes:** cada plan es una combinación de módulos definida en la configuración.
- **Reorganización del repo:** por módulo y capa, sin empezar de cero y sin cambiar lo que hace hoy. Primero solo propuesta. No se mueve código hasta que el Director apruebe, y nada antes de que termine la corrida del 01/10.

## Tareas que salen de aquí
- [ ] Propuesta de reorganización de `src/` (estructura, tabla de archivos, orden de mudanza y riesgos). Presentada el 29/09, espera aprobación.
- [ ] Mudanza en PRs pequeños después de la corrida del 01/10, cada uno con las pruebas en verde.

## Preguntas que quedan abiertas (del Director)
- Acceso a la API de Google Business Profile (requiere aprobación de Google).
- WordPress como primer conector.
- Quién hace las mejoras del nivel Guiado.
- Cómo se aprueban los textos de salud.
