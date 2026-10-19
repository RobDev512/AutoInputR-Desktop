# Roadmap de AutoInputR

Este roadmap organiza mejoras funcionales y trabajo técnico previsto. Las versiones futuras son una guía y pueden cambiar de orden según pruebas, estabilidad y prioridad.

## v1.2.3.1 — Base estable de automatización

**Estado: Aplicado**

- Clicker, KeyPresser, Mover, Ruta y Rastreador funcionales.
- Configuración persistente y hotkeys globales.
- Bandeja del sistema y empaquetado para Windows.

## v1.3.0 — Ventana objetivo y base modular

**Estado: Aplicado**

- Selector de ventana objetivo por título, proceso y clase.
- Pausa al perder el foco y reanudación automática opcional.
- Integración con los cinco módulos principales.
- Refactor técnico posterior a la publicación: paquete `autoinputr/`, módulos funcionales, servicios Win32/entrada/visión, configuración y diálogos separados.
- Punto de entrada reducido en `AutoInputR.py`.

## v1.4.0 — Perfiles y portabilidad

**Estado: Siguiente**

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

## Backlog técnico permanente

- Mantener compatibilidad con `config.json` entre versiones.
- Añadir pruebas automatizadas cuando se separen nuevas responsabilidades.
- Reducir dependencias directas entre interfaz, automatización y servicios del sistema.
- Revisar rendimiento de loops y uso de CPU.
- Mantener soporte coherente entre PyAutoGUI y PyDirectInput.
- Revisar compatibilidad de empaquetado antes de cada Release.

## Flujo de entrega

**Implementar → probar desde Python → estabilizar → documentar → compilar → crear instalador → publicar Release.**
