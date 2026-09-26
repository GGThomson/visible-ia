# 🏗️ Arquitectura (Fase 4)
<!-- CÓMO se construye. Cada elección importante debe tener un ADR en docs/decisiones/. -->

## Diagrama general
```mermaid
flowchart LR
  Usuario --> Frontend --> Backend --> BaseDeDatos[(Base de datos)]
  Backend --> ServiciosExternos[Servicios externos]
```

## Stack tecnológico
| Capa | Tecnología | Por qué (ADR) |
|---|---|---|
| Frontend | | |
| Backend | | |
| Base de datos | | |
| Autenticación | | |
| Hosting / despliegue | | |
| Pagos (si aplica) | | |
| Pruebas | | |

## Modelo de datos
| Entidad | Campos principales | Relaciones |
|---|---|---|

## Estructura de carpetas del código
```
src/
tests/
```

## Entornos
| Entorno | URL | Rama | Cómo se despliega |
|---|---|---|---|
| Local | localhost | cualquiera | — |
| Staging | | develop / main | |
| Producción | | tags `v*` | |

## Seguridad
- Manejo de secretos (`.env`, nunca en Git): 
- Autenticación y permisos: 
- Datos personales: 

## Costos estimados mensuales
| Servicio | Plan | Costo |
|---|---|---|
