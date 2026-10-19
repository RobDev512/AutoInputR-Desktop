$ErrorActionPreference = "Stop"

$ScriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDirectory

Write-Host "Limpiando compilaciones anteriores..."

Remove-Item -Recurse -Force ".\build" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force ".\dist" -ErrorAction SilentlyContinue
Remove-Item -Force ".\AutoInputR_v1.2.spec" -ErrorAction SilentlyContinue
Remove-Item -Force "..\AutoInputR_v1.2.exe" -ErrorAction SilentlyContinue

Write-Host "Compilando AutoInputR..."

python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --name "AutoInputR_v1.2" `
    --icon "Logo2AIR.ico" `
    --add-data "LogoAIR.png;." `
    --add-data "Logo2AIR.png;." `
    --add-data "Logo2AIR.ico;." `
    --collect-data customtkinter `
    --collect-all cv2 `
    --collect-all mss `
    --collect-all numpy `
    --collect-all pydirectinput `
    --collect-all pynput `
    --collect-all pystray `
    AutoInputR.py

Write-Host "Copiando el ejecutable a la carpeta raiz..."

Copy-Item `
    -Force `
    ".\dist\AutoInputR_v1.2.exe" `
    "..\AutoInputR_v1.2.exe"

Write-Host ""
Write-Host "Compilacion terminada correctamente."
Write-Host "Ejecutable de PyInstaller:"
Write-Host "$ScriptDirectory\dist\AutoInputR_v1.2.exe"
Write-Host ""
Write-Host "Ejecutable para Inno Setup:"
Write-Host "$(Resolve-Path '..\AutoInputR_v1.2.exe')"