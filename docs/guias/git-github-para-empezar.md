# 🌱 Git y GitHub para empezar (explicado sin tecnicismos)

## La idea en una imagen
- **Git** es una "máquina del tiempo" que vive en tu computadora: guarda fotos (*commits*) de tu proyecto para que puedas volver a cualquier punto.
- **GitHub** es la nube donde subes esas fotos: respaldo, historial visible y colaboración.
- **Claude Code** hará casi todos los comandos por ti y te explicará cada uno. Esta guía es para que **entiendas** qué está pasando.

## Vocabulario mínimo
| Palabra | Qué es | Analogía |
|---|---|---|
| Repositorio (repo) | La carpeta del proyecto con su historial | Un álbum de fotos |
| Commit | Una foto guardada con una descripción | "Foto: login terminado" |
| Rama (branch) | Una línea de trabajo paralela | Un borrador aparte que no toca el original |
| `main` | La rama principal, siempre estable | El documento "oficial" |
| Merge | Unir una rama a otra | Pasar el borrador al oficial |
| Push / Pull | Subir / bajar cambios a GitHub | Sincronizar con la nube |
| Pull Request (PR) | Pedir revisar y unir una rama en GitHub | "Revisa mi borrador antes de oficializarlo" |
| Tag | Una etiqueta en un commit importante | "Versión 1.0" |
| `.gitignore` | Lista de archivos que Git no guarda | Cosas privadas que no van al álbum |

## Configuración inicial (una sola vez)
```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu@correo.com"
git config --global init.defaultBranch main
gh auth login          # conecta tu computadora con GitHub
```

## El flujo de este sistema
```
main ──●────────────●──────────●───► (siempre funciona)
        \          /  \        /
         ●──●──●──●    ●──●──●
     feat/F2-T01-login   fix/F2-T02-error
```
1. Cada tarea crea su rama desde `main`.
2. Se hacen commits pequeños en la rama.
3. Se sube la rama (`push`) y se abre un **PR**.
4. Revisas el PR en GitHub (o se lo pides a Gemini o Claude) y lo **fusionas** (*merge*).
5. `main` avanza y siempre queda estable.

## Comandos que verás a Claude Code usar
| Comando | Qué hace |
|---|---|
| `git status` | Muestra qué cambió y qué falta guardar |
| `git add -A` | Prepara todos los cambios para la foto |
| `git commit -m "feat: ..."` | Toma la foto con una descripción |
| `git checkout -b nombre` | Crea una rama nueva y te cambia a ella |
| `git checkout main` | Vuelve a la rama principal |
| `git pull` | Baja lo último de GitHub |
| `git push` | Sube tus commits a GitHub |
| `git log --oneline` | Lista de fotos (historial) |
| `git tag v1.0.0` | Etiqueta una versión |
| `gh pr create` | Crea un Pull Request |
| `gh pr merge` | Fusiona un Pull Request |

## Mensajes de commit (Conventional Commits)
```
feat(F2-T03): formulario de login      ← funcionalidad nueva
fix(F2-T05): corrige validación email  ← arreglo
docs: actualiza PRD                    ← documentación
refactor: simplifica servicio de pagos ← mejora interna sin cambiar el comportamiento
test: agrega pruebas de login          ← pruebas
chore: actualiza dependencias          ← mantenimiento
```

## Versiones (versionado semántico)
`vMAYOR.MENOR.PARCHE`, por ejemplo `v1.4.2`:
- **MAYOR**: cambios que rompen compatibilidad.
- **MENOR**: funcionalidades nuevas.
- **PARCHE**: arreglos.

## Reglas de seguridad
- Nunca subas contraseñas ni claves. Van en `.env`, que está en `.gitignore`. Comparte solo `.env.example`, sin los valores reales.
- Si subiste una clave por error, **cámbiala de inmediato** en el servicio correspondiente. Borrarla del historial no basta.
- Evita `git push --force` en `main`. Este proyecto lo bloquea para Claude Code.

## "¡Me equivoqué!" (rescates comunes)
| Situación | Pídele a Claude Code |
|---|---|
| Quiero deshacer cambios que no guardé | "Descarta los cambios sin commit de <archivo>" |
| El último commit estaba mal | "Corrige el último commit" |
| Quiero volver a como estaba ayer | "Muéstrame los commits de ayer y créame una rama desde ahí" |
| Una rama se volvió un desastre | "Abandona esta rama y vuelve a main" |

## Para aprender más
- Libro oficial gratuito en español: https://git-scm.com/book/es/v2
- GitHub Skills (cursos interactivos): https://skills.github.com/
