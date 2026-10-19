# Arquitectura de TaskPilot

## Contexto

TaskPilot es la continuación de AutoInputR. La arquitectura modular fue introducida después de la publicación de AutoInputR v1.3.0 y se conserva como base para TaskPilot v1.4.0.

## Punto de entrada

`TaskPilot.py` es deliberadamente pequeño. Importa `TaskPilot` desde `taskpilot.app`, crea la instancia y ejecuta `mainloop()`.

## `taskpilot/app.py`

Contiene la clase principal `TaskPilot`, el estado compartido, la construcción general de la ventana, carga de recursos, persistencia coordinada y creación de threads. Su responsabilidad es coordinar; la lógica específica vive en otros archivos.

## Core

- `core/resources.py`: nombre, versión, directorios, recursos y migración desde AutoInputR.
- `core/config.py`: almacenamiento JSON.
- `core/target_window.py`: reglas y estado de la ventana objetivo.
- `core/hotkeys.py`: listener global y hotkey principal del movimiento.

## Módulos

- `modules/clicker.py`: interfaz y ejecución del Clicker.
- `modules/keypresser.py`: interfaz y ejecución del KeyPresser.
- `modules/mover.py`: movimiento dentro de una zona.
- `modules/ruta.py`: grabación, HUD, reproducción y configuración de rutas.
- `modules/rastreador.py`: selección de área/objetivo y seguimiento visual.

## Servicios

- `services/input_backend.py`: abstracción de PyAutoGUI/PyDirectInput.
- `services/windows.py`: Win32 de bajo nivel para ventanas y procesos.
- `services/vision.py`: captura/conversión y coincidencia de plantillas con OpenCV.
- `services/tray.py`: bandeja del sistema y ciclo de cierre.

## UI

- `ui/dialogs/window_selector.py`: selección/configuración de ventana objetivo.
- `ui/dialogs/settings.py`: configuración general, Acerca de y operaciones relacionadas.

## Configuración y compatibilidad

`data/config.json` almacena la configuración local y está ignorado por Git. Se conserva la migración desde `config.json` legado. Además, una instalación nueva de TaskPilot puede copiar `config.json` y `tracker_template.png` desde una instalación anterior de AutoInputR sin borrar los originales.

## Recursos

Los recursos visuales están en `assets/branding/` y se documentan en [BRANDING.md](BRANDING.md). `resources.py` resuelve ejecución desde código fuente y PyInstaller.

## Empaquetado

`packaging/build.ps1` genera `TaskPilot.exe` con PyInstaller. `packaging/TaskPilot.iss` genera el instalador con Inno Setup. Se conserva el `AppId` histórico para facilitar la continuidad de actualización desde AutoInputR.
