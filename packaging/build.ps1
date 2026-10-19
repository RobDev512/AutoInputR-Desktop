$ErrorActionPreference = "Stop"

$PackagingDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $PackagingDirectory

Set-Location $ProjectRoot

Write-Host "Limpiando compilaciones anteriores..."

Remove-Item -Recurse -Force ".\build" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force ".\dist" -ErrorAction SilentlyContinue
Remove-Item -Force ".\TaskPilot.spec" -ErrorAction SilentlyContinue
Remove-Item -Force ".\TaskPilot.exe" -ErrorAction SilentlyContinue

Write-Host "Compilando TaskPilot..."

python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name "TaskPilot" `
    --icon ".\assets\branding\TaskPilotIcon.ico" `
    --add-data ".\assets\branding\TaskPilotLogo.png;assets\branding" `
    --add-data ".\assets\branding\TaskPilotLogoHorizontal.png;assets\branding" `
    --add-data ".\assets\branding\TaskPilotLogoTransparent.png;assets\branding" `
    --add-data ".\assets\branding\TaskPilotMono.png;assets\branding" `
    --add-data ".\assets\branding\TaskPilotIcon.png;assets\branding" `
    --add-data ".\assets\branding\TaskPilotIcon.ico;assets\branding" `
    --collect-data customtkinter `
    --collect-all cv2 `
    --collect-all mss `
    --collect-all numpy `
    --collect-all pydirectinput `
    --collect-all pynput `
    --collect-all pystray `
    TaskPilot.py

Write-Host "Copiando el ejecutable a la carpeta raiz..."

Copy-Item `
    -Force `
    ".\dist\TaskPilot.exe" `
    ".\TaskPilot.exe"

Write-Host ""
Write-Host "Compilacion terminada correctamente."
Write-Host "Ejecutable de PyInstaller:"
Write-Host "$ProjectRoot\dist\TaskPilot.exe"
Write-Host ""
Write-Host "Ejecutable para Inno Setup:"
Write-Host "$(Resolve-Path '.\TaskPilot.exe')"
