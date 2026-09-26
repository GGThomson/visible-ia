# Crea un proyecto nuevo a partir de esta plantilla (versión para Windows / PowerShell).
# Uso:     powershell -ExecutionPolicy Bypass -File scripts\nuevo-proyecto.ps1 <nombre-del-proyecto> [carpeta-destino]
# Ejemplo: powershell -ExecutionPolicy Bypass -File scripts\nuevo-proyecto.ps1 mi-saas C:\Users\yo\Documents\Proyectos
# Si no indicas carpeta-destino, el proyecto se crea junto a la plantilla (en su carpeta padre).
param(
  [Parameter(Position = 0)] [string]$Nombre,
  [Parameter(Position = 1)] [string]$DestinoBase
)
$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($Nombre)) {
  Write-Host "Uso: powershell -ExecutionPolicy Bypass -File scripts\nuevo-proyecto.ps1 <nombre-del-proyecto> [carpeta-destino]"
  exit 1
}

$Plantilla = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
if ([string]::IsNullOrWhiteSpace($DestinoBase)) { $DestinoBase = Split-Path $Plantilla -Parent }
$Destino = Join-Path (Resolve-Path $DestinoBase).Path $Nombre
$Hoy = Get-Date -Format 'yyyy-MM-dd'

if (Test-Path $Destino) {
  Write-Host "❌ Ya existe: $Destino"
  exit 1
}

Write-Host "📁 Copiando la plantilla a $Destino ..."
New-Item -ItemType Directory -Path $Destino | Out-Null
# Copia todo excepto el historial Git de la plantilla
Get-ChildItem -Path $Plantilla -Force | Where-Object { $_.Name -ne '.git' } |
  ForEach-Object { Copy-Item -Path $_.FullName -Destination $Destino -Recurse -Force }

Set-Location $Destino

# Personaliza ESTADO.md con el nombre y la fecha (se guarda en UTF-8 sin BOM, como el original)
$Estado = Join-Path $Destino 'memoria\ESTADO.md'
$Texto = [IO.File]::ReadAllText($Estado, [Text.Encoding]::UTF8)
$Texto = $Texto.Replace('_(nombre)_', $Nombre).Replace('AAAA-MM-DD', $Hoy)
[IO.File]::WriteAllText($Estado, $Texto, (New-Object Text.UTF8Encoding $false))

Write-Host "🗂️  Iniciando Git (el 'álbum de fotos' del proyecto) ..."
git init -q -b main
if ($LASTEXITCODE -ne 0) { throw "Falló git init" }
git add -A
git commit -q -m "chore: proyecto creado desde la plantilla"
if ($LASTEXITCODE -ne 0) { throw "Falló git commit" }

$GhListo = $false
if (Get-Command gh -ErrorAction SilentlyContinue) {
  gh auth status *> $null
  $GhListo = ($LASTEXITCODE -eq 0)
}

if ($GhListo) {
  $Resp = Read-Host "¿Crear repositorio PRIVADO en GitHub y subirlo? [s/N]"
  if ($Resp -match '^[sS]$') {
    gh repo create $Nombre --private --source=. --remote=origin --push
    if ($LASTEXITCODE -eq 0) { Write-Host "☁️  Subido a GitHub." }
    else { Write-Host "⚠️  No se pudo crear o subir el repositorio. Revisa el mensaje de arriba." }
  }
} else {
  Write-Host "ℹ️  GitHub CLI no está instalado o no has iniciado sesión (gh auth login). Puedes subir el repo más tarde."
}

Write-Host ""
Write-Host "✅ Listo. Siguientes pasos:"
Write-Host "   cd `"$Destino`""
Write-Host "   claude"
Write-Host "   /iniciar"
