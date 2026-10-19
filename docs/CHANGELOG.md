# Changelog

Los cambios relevantes de AutoInputR se documentan aquí.

## Unreleased

### Documentación y producto

- Definido AutoInputR como una herramienta de automatización visual y configurable para Windows, sin necesidad de escribir scripts.
- Añadido `PRODUCT.md` con propósito, público objetivo, principios, casos de uso y límites del proyecto.
- El uso en juegos queda como un caso secundario, no como la identidad principal del producto.
- README y ROADMAP alineados con la nueva definición de producto.

### Estructura del repositorio

- Raíz del repositorio simplificada: documentación en `docs/`, dependencias en `requirements/` y datos locales en `data/`.
- Migración automática del `config.json` y `tracker_template.png` legados hacia `data/`.

### Cambiado

- Reorganización interna del proyecto sin cambiar la versión pública v1.3.0.
- `AutoInputR.py` quedó como punto de entrada mínimo.
- La ventana principal se movió a `autoinputr/app.py`.
- Clicker, KeyPresser, Mover, Ruta y Rastreador se separaron en módulos propios.
- La lógica de ventana objetivo se separó en `core/target_window.py`.
- Las hotkeys globales se separaron en `core/hotkeys.py`.
- La lectura/escritura de configuración se separó en `core/config.py`.
- Los recursos se centralizaron en `core/resources.py`.
- Win32, backend de entrada, visión y bandeja se separaron en `services/`.
- Los diálogos de configuración y ventana objetivo se separaron en `ui/dialogs/`.
- Logos y recursos de branding se organizaron en `assets/branding/`.
- Scripts de compilación e instalador se organizaron en `packaging/`.

### Documentación

- README actualizado para el repositorio `AutoInputR-Desktop`.
- Añadidos ROADMAP, definición de producto, documentación de arquitectura, desarrollo y checklist de Release.

## v1.3.0

### Añadido

- Selector de ventana objetivo.
- Identificación por título, proceso y clase de ventana.
- Pausa/reanudación automática según foco.
- Protección de Clicker, KeyPresser, Mover, Ruta y Rastreador.

## v1.2.3.1

- Base estable previa a la incorporación de Ventana objetivo.
