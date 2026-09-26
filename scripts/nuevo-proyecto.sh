#!/usr/bin/env bash
# Crea un proyecto nuevo a partir de esta plantilla.
# Uso:  bash scripts/nuevo-proyecto.sh <nombre-del-proyecto> [carpeta-destino]
# Ejemplo: bash scripts/nuevo-proyecto.sh mi-saas ~/proyectos
set -euo pipefail

NOMBRE="${1:-}"
DESTINO_BASE="${2:-$(pwd)/..}"

if [[ -z "$NOMBRE" ]]; then
  echo "Uso: bash scripts/nuevo-proyecto.sh <nombre-del-proyecto> [carpeta-destino]"
  exit 1
fi

PLANTILLA="$(cd "$(dirname "$0")/.." && pwd)"
DESTINO="$(cd "$DESTINO_BASE" && pwd)/$NOMBRE"
HOY="$(date +%Y-%m-%d)"

if [[ -e "$DESTINO" ]]; then
  echo "❌ Ya existe: $DESTINO"
  exit 1
fi

echo "📁 Copiando la plantilla a $DESTINO ..."
mkdir -p "$DESTINO"
# Copia todo excepto el historial Git de la plantilla
( cd "$PLANTILLA" && tar --exclude='./.git' -cf - . ) | ( cd "$DESTINO" && tar -xf - )

cd "$DESTINO"

# Personaliza ESTADO.md con el nombre y la fecha
sed -i.bak "s/_(nombre)_/$NOMBRE/; s/AAAA-MM-DD/$HOY/" memoria/ESTADO.md && rm -f memoria/ESTADO.md.bak

echo "🗂️  Iniciando Git (el 'álbum de fotos' del proyecto) ..."
git init -q -b main
git add -A
git commit -q -m "chore: proyecto creado desde la plantilla"

if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  read -r -p "¿Crear repositorio PRIVADO en GitHub y subirlo? [s/N] " RESP
  if [[ "${RESP:-N}" =~ ^[sS]$ ]]; then
    gh repo create "$NOMBRE" --private --source=. --remote=origin --push
    echo "☁️  Subido a GitHub."
  fi
else
  echo "ℹ️  GitHub CLI no está instalado o no has iniciado sesión (gh auth login). Puedes subir el repo más tarde."
fi

echo ""
echo "✅ Listo. Siguientes pasos:"
echo "   cd \"$DESTINO\""
echo "   claude"
echo "   /iniciar"
