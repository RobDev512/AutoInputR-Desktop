# Definición de producto de TaskPilot

## Identidad

**TaskPilot — Automatización visual y configurable para Windows, sin necesidad de escribir scripts.**

TaskPilot es una aplicación de escritorio para Windows orientada a automatizar interacciones repetitivas con interfaces gráficas. Permite combinar clicks, pulsaciones de teclado, movimientos del cursor, rutas grabadas y acciones basadas en detección visual desde una interfaz gráfica, sin exigir al usuario escribir código.

## Continuidad

TaskPilot continúa el desarrollo iniciado bajo el nombre **AutoInputR**. AutoInputR identifica la etapa histórica hasta v1.3.0; TaskPilot adopta la nueva identidad a partir del ciclo de desarrollo v1.4.0. El cambio de nombre no reinicia el proyecto ni elimina su historial.

## Propósito

El propósito de TaskPilot es reducir la fricción entre una tarea repetitiva y una automatización funcional. La idea central es que una persona pueda pasar de “quiero que la computadora repita esto” a una rutina configurable desde la propia aplicación.

TaskPilot no pretende reemplazar plataformas empresariales de RPA ni convertirse de inmediato en un sistema de automatización universal. Su enfoque es mantener una herramienta local, comprensible y extensible para automatizaciones de escritorio de complejidad baja o media.

## Tipo de proyecto

TaskPilot es un **proyecto personal de software y automatización con enfoque de portafolio**, con potencial para evolucionar hacia una herramienta general de automatización de escritorio.

Su valor no depende de un único escenario de uso. El proyecto también sirve para desarrollar y demostrar trabajo con interfaces de escritorio, automatización de entrada, hotkeys globales, Win32, visión artificial, grabación y reproducción de acciones, persistencia, empaquetado y arquitectura modular.

## Usuarios objetivo

TaskPilot está pensado principalmente para:

- Usuarios que quieran automatizar tareas repetitivas sencillas en aplicaciones de Windows.
- Estudiantes y desarrolladores que experimenten con automatización de escritorio.
- Testers que necesiten repetir interacciones de interfaz de forma consistente.
- Usuarios avanzados que quieran construir pequeñas rutinas sin mantener scripts propios.
- Jugadores, de forma secundaria, únicamente en contextos donde la automatización esté permitida por las reglas del juego o servicio.

## Casos de uso

- Repetir clicks o pulsaciones con intervalos configurables.
- Automatizar pequeños flujos en programas que no ofrecen una API adecuada.
- Reproducir secuencias de interacción para pruebas o demostraciones.
- Mantener rutinas condicionadas por una ventana objetivo.
- Detectar elementos visuales en pantalla y reaccionar ante ellos.
- Experimentar con automatización visual y reconocimiento por plantilla.
- Automatizar tareas personales repetitivas de bajo riesgo.

## Cómo encajan los módulos actuales

| Componente | Papel dentro del producto |
| --- | --- |
| Clicker | Automatización de clicks repetitivos |
| KeyPresser | Automatización de entrada de teclado |
| Mover | Automatización de movimiento y actividad del cursor |
| Ruta | Grabación y reproducción de interacción |
| Rastreador | Automatización basada en detección visual |
| Ventana objetivo | Contexto, seguridad y control de ejecución |

## Principios de producto

1. **Sin scripts obligatorios.** Las funciones principales deben poder configurarse desde la interfaz.
2. **Control del usuario.** Toda automatización debe ser fácil de iniciar, detener y entender.
3. **Ejecución contextual.** Siempre que sea posible, las acciones deben limitarse a la ventana o contexto elegido por el usuario.
4. **Configuración reutilizable.** Las automatizaciones deberían poder guardarse, recuperarse y progresivamente compartirse mediante perfiles.
5. **Crecimiento modular.** Las nuevas funciones deben integrarse sin volver a concentrar toda la lógica en una única clase o archivo.
6. **Seguridad antes que velocidad.** Simulación, diagnósticos, límites y recuperación de errores tienen prioridad sobre automatizaciones opacas o difíciles de detener.
7. **Uso responsable.** TaskPilot no debe presentarse como una herramienta para evadir reglas, restricciones o sistemas de protección de terceros.

## Lo que TaskPilot no pretende ser por ahora

- Una plataforma empresarial completa de RPA.
- Un sustituto de Power Automate, UiPath u otras suites corporativas.
- Una herramienta de automatización web basada en DOM o APIs de navegador.
- Un sistema diseñado para evadir mecanismos anti-cheat, restricciones de servicios o controles de acceso.
- Un motor de macros que requiera programación para sus funciones esenciales.

## Dirección futura

La evolución del proyecto debería priorizar perfiles e importación/exportación, macros y secuencias unificadas, condiciones visuales y temporales, coordenadas relativas y multimonitor, simulación y diagnóstico, y finalmente un editor visual más expresivo.

El detalle de versiones y prioridades se mantiene en [ROADMAP.md](ROADMAP.md).
