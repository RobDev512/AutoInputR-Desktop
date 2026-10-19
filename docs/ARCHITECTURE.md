# Arquitectura de AutoInputR

## Objetivo

La arquitectura separa responsabilidades sin cambiar el comportamiento público de AutoInputR v1.3.0. La aplicación sigue coordinándose desde una única clase `AutoInputR`, pero sus funciones se distribuyen mediante mixins especializados.

## Punto de entrada

`AutoInputR.py` es deliberadamente pequeño. Importa `AutoInputR` desde `autoinputr.app`, crea la instancia y ejecuta `mainloop()`.

## `autoinputr/app.py`

Contiene la clase principal, el estado compartido, la construcción general de la ventana, carga de recursos, persistencia coordinada y creación de threads. Su responsabilidad es coordinar; la lógica específica vive en otros archivos.

## Core

- `core/resources.py`: nombre, versión, directorios y rutas de recursos.
- `core/config.py`: almacenamiento JSON.
- `core/target_window.py`: reglas y estado de la ventana objetivo.
- `core/hotkeys.py`: listener global y hotkey principal del movimiento.

## Módulos

- `modules/clicker.py`: interfaz y ejecución del Clicker.
- `modules/keypresser.py`: interfaz y ejecución del KeyPresser.
- `modules/mover.py`: movimiento dentro de una zona.
- `modules/ruta.py`: grabación, HUD, reproducción y configuración de rutas.
- `modules/rastreador.py`: selección de área/objetivo y seguimiento visual.

Cada módulo puede usar servicios compartidos a través de la clase compuesta, por ejemplo `move_cursor_to`, `click_mouse`, `save_config` o `can_execute_for_target_window`.

## Servicios

- `services/input_backend.py`: abstracción actual de PyAutoGUI/PyDirectInput para movimiento y click.
- `services/windows.py`: Win32 de bajo nivel para ventanas y procesos.
- `services/vision.py`: captura/conversión y coincidencia de plantillas con OpenCV.
- `services/tray.py`: bandeja del sistema y ciclo de cierre.

## UI

- `ui/dialogs/window_selector.py`: diálogo de selección/configuración de ventana objetivo.
- `ui/dialogs/settings.py`: configuración general, Acerca de y operaciones relacionadas.

## Configuración

`data/config.json` almacena la configuración local y está ignorado por Git. Si existe un `config.json` legado en la raíz de ejecución, AutoInputR lo migra automáticamente a `data/` sin cambiar sus claves. `tracker_template.png` usa la misma estrategia de migración.

## Recursos

Los recursos visuales están en `assets/branding/`. `resources.py` resuelve tanto ejecución desde código fuente como ejecución empaquetada con PyInstaller.

## Empaquetado

`packaging/build.ps1` genera el ejecutable con PyInstaller. `packaging/AutoInputR.iss` genera el instalador con Inno Setup. La versión pública permanece en `APP_VERSION` y en el script de Inno Setup.
