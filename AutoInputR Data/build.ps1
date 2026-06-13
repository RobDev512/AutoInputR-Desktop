$ErrorActionPreference = "Stop"

$ScriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDirectory

Write-Host "Limpiando compilaciones anteriores..."

Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
Remove-Item -Force AutoInputR_v1.2.spec -ErrorAction SilentlyContinue

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

Write-Host "Copiando el ejecutable a la carpeta del instalador..."

Copy-Item `
    -Force `
    ".\dist\AutoInputR_v1.2.exe" `
    "..\AutoInputR_v1.2.exe"

Write-Host ""
Write-Host "Compilacion terminada correctamente."
Write-Host "Ejecutable:"
Write-Host "..\AutoInputR_v1.2.exe"