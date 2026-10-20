# Roadmap de TaskPilot

TaskPilot continúa el proyecto anteriormente conocido como **AutoInputR**. Las versiones hasta v1.3.0 conservan su nombre histórico; el rebranding y la nueva identidad comienzan durante v1.4.0.

TaskPilot se desarrolla como una herramienta de **automatización visual y configurable para Windows, sin necesidad de escribir scripts**.

La definición de producto y los criterios para nuevas funciones se encuentran en [PRODUCT.md](PRODUCT.md).

## v1.2.3.1 — AutoInputR: base estable de automatización

**Estado: Aplicado**

- Clicker, KeyPresser, Mover, Ruta y Rastreador funcionales.
- Configuración persistente y hotkeys globales.
- Bandeja del sistema y empaquetado para Windows.

## v1.3.0 — AutoInputR: ventana objetivo y base modular

**Estado: Aplicado**

- Selector de ventana objetivo por título, proceso y clase.
- Pausa al perder el foco y reanudación automática opcional.
- Integración con los cinco módulos principales.
- Refactor técnico posterior a la publicación hacia el paquete modular `autoinputr/`.
- Definición del producto como herramienta general de automatización de escritorio.
- Última versión pública publicada bajo el nombre AutoInputR.

## v1.4.0 — TaskPilot: rebranding, perfiles y portabilidad

**Estado: En desarrollo**

- Cambio de nombre de AutoInputR a TaskPilot.
- Nueva identidad visual y recursos de marca.
- Paquete Python `taskpilot/` y launcher `TaskPilot.py`.
- Compatibilidad de migración desde configuraciones de AutoInputR.
- Perfiles de configuración.
- Importar y exportar perfiles.
- Combinaciones de hotkeys.
- Detección y visualización de conflictos de hotkeys.

## v1.4.1 — Rutas, coordenadas y pantallas

**Estado: Pendiente**

- Editor avanzado de rutas.
- Coordenadas relativas.
- Mejor soporte para varios monitores y DPI.
- Herramientas de ajuste y revisión de puntos grabados.

## v1.4.2 — Diagnóstico y seguridad

**Estado: Pendiente**

- Modo simulación / dry-run.
- Logs de ejecución configurables.
- Panel básico de rendimiento.
- Mensajes de diagnóstico más claros.

## v1.5.0 — Núcleo de macros

**Estado: Pendiente**

- Grabador unificado.
- Secuencias de acciones.
- Integración de Clicker, KeyPresser, Mover, Ruta y Rastreador dentro de macros.

## v1.5.1 — Automatización condicional

**Estado: Pendiente**

- Condiciones visuales.
- Programación por horario o temporizador.
- Múltiples objetivos del Rastreador.
- Múltiples zonas de trabajo.

## v1.6.0 — Experiencia de escritorio

**Estado: Pendiente**

- Actualizador.
- Modo compacto.
- Personalización visual adicional.
- Mejoras de accesibilidad y organización de la interfaz.

## v2.0.0 — Automation Studio

**Estado: Visión**

- Editor visual de macros.
- Variables y contadores.
- Recuperación ante errores durante automatizaciones largas.
- Sistema extensible de acciones y plugins.

## Criterios para priorizar funciones

- Resolver una interacción repetitiva real de escritorio.
- Poder configurarse sin exigir código al usuario.
- Ser reutilizable en más de una aplicación o escenario.
- Mantener controles claros para iniciar, detener, simular o diagnosticar la automatización.
- Encajar en la arquitectura modular actual sin volver a concentrar responsabilidades.

Las funciones diseñadas únicamente alrededor de un juego o aplicación concreta tendrán menor prioridad salvo que puedan generalizarse como capacidad reutilizable.

## Backlog técnico permanente

- Mantener compatibilidad de configuración entre versiones y durante el rebranding.
- Añadir pruebas automatizadas cuando se separen nuevas responsabilidades.
- Reducir dependencias directas entre interfaz, automatización y servicios del sistema.
- Revisar rendimiento de loops y uso de CPU.
- Mantener soporte coherente entre PyAutoGUI y PyDirectInput.
- Revisar compatibilidad de empaquetado antes de cada Release.

## Flujo de entrega

**Implementar → probar desde Python → estabilizar → documentar → compilar → crear instalador → publicar Release.**
