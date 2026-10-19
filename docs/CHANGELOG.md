# Changelog

Los cambios relevantes de TaskPilot y de su etapa histórica como AutoInputR se documentan aquí.

## Unreleased

### Identidad y transición a TaskPilot

- Renombrado el proyecto de AutoInputR a **TaskPilot** para el ciclo de desarrollo v1.4.0.
- Nueva identidad visual con logo principal, logo horizontal, icono, versión transparente y versión monocromática.
- Renombrado el paquete Python de `autoinputr/` a `taskpilot/`.
- Renombrado el punto de entrada a `TaskPilot.py` y la clase principal a `TaskPilot`.
- Actualizados scripts de PyInstaller e Inno Setup para la nueva marca.
- Añadida compatibilidad para copiar configuración y plantilla visual desde una instalación anterior de AutoInputR cuando sea necesario.
- Los Releases y tags hasta v1.3.0 conservan el nombre AutoInputR como parte del historial del proyecto.

### Documentación y producto

- Definido el producto como una herramienta de automatización visual y configurable para Windows, sin necesidad de escribir scripts.
- Añadido `PRODUCT.md` con propósito, público objetivo, principios, casos de uso y límites del proyecto.
- El uso en juegos queda como un caso secundario, no como la identidad principal del producto.
- README y ROADMAP alineados con la definición actual del producto.

### Estructura del repositorio

- Raíz simplificada: documentación en `docs/`, dependencias en `requirements/` y datos locales en `data/`.
- Migración automática del `config.json` y `tracker_template.png` legados hacia `data/`.
- Arquitectura modular separada en core, módulos, servicios y diálogos.

## v1.3.0 — AutoInputR

### Añadido

- Selector de ventana objetivo.
- Identificación por título, proceso y clase de ventana.
- Pausa/reanudación automática según foco.
- Protección de Clicker, KeyPresser, Mover, Ruta y Rastreador.

Esta fue la última versión pública publicada bajo el nombre AutoInputR.

## v1.2.3.1 — AutoInputR

- Base estable previa a la incorporación de Ventana objetivo.
