# Definición de producto de AutoInputR

## Identidad

**AutoInputR — Automatización visual y configurable para Windows, sin necesidad de escribir scripts.**

AutoInputR es una aplicación de escritorio para Windows orientada a automatizar interacciones repetitivas con interfaces gráficas. Permite combinar clicks, pulsaciones de teclado, movimientos del cursor, rutas grabadas y acciones basadas en detección visual desde una interfaz gráfica, sin exigir al usuario escribir código.

## Propósito

El propósito de AutoInputR es reducir la fricción entre una tarea repetitiva y una automatización funcional. La idea central es que una persona pueda pasar de “quiero que la computadora repita esto” a una rutina configurable desde la propia aplicación.

AutoInputR no pretende reemplazar plataformas empresariales de RPA ni convertirse de inmediato en un sistema de automatización universal. Su enfoque es mantener una herramienta local, comprensible y extensible para automatizaciones de escritorio de complejidad baja o media.

## Tipo de proyecto

AutoInputR es un **proyecto personal de software y automatización con enfoque de portafolio**, con potencial para evolucionar hacia una herramienta general de automatización de escritorio.

Su valor no depende de un único escenario de uso. El proyecto también sirve para desarrollar y demostrar trabajo con interfaces de escritorio, automatización de entrada, hotkeys globales, Win32, visión artificial, grabación y reproducción de acciones, persistencia, empaquetado y arquitectura modular.

## Usuarios objetivo

AutoInputR está pensado principalmente para:

- Usuarios que quieran automatizar tareas repetitivas sencillas en aplicaciones de Windows.
- Estudiantes y desarrolladores que experimenten con automatización de escritorio.
- Testers que necesiten repetir interacciones de interfaz de forma consistente.
- Usuarios avanzados que quieran construir pequeñas rutinas sin mantener scripts propios.
- Jugadores, de forma secundaria, únicamente en contextos donde la automatización esté permitida por las reglas del juego o servicio.

## Casos de uso

Ejemplos de usos compatibles con la dirección del proyecto:

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

Las nuevas funciones deberían respetar estas reglas:

1. **Sin scripts obligatorios.** Las funciones principales deben poder configurarse desde la interfaz.
2. **Control del usuario.** Toda automatización debe ser fácil de iniciar, detener y entender.
3. **Ejecución contextual.** Siempre que sea posible, las acciones deben limitarse a la ventana o contexto elegido por el usuario.
4. **Configuración reutilizable.** Las automatizaciones deberían poder guardarse, recuperarse y, progresivamente, compartirse mediante perfiles.
5. **Crecimiento modular.** Las nuevas funciones deben integrarse sin volver a concentrar toda la lógica en una única clase o archivo.
6. **Seguridad antes que velocidad.** Simulación, diagnósticos, límites y recuperación de errores tienen prioridad sobre automatizaciones opacas o difíciles de detener.
7. **Uso responsable.** AutoInputR no debe presentarse como una herramienta para evadir reglas, restricciones o sistemas de protección de terceros.

## Lo que AutoInputR no pretende ser por ahora

- Una plataforma empresarial completa de RPA.
- Un sustituto de Power Automate, UiPath u otras suites corporativas.
- Una herramienta de automatización web basada en DOM o APIs de navegador.
- Un sistema diseñado para evadir mecanismos anti-cheat, restricciones de servicios o controles de acceso.
- Un motor de macros que requiera programación para sus funciones esenciales.

## Dirección futura

La evolución del proyecto debería priorizar:

- Perfiles e importación/exportación.
- Macros y secuencias unificadas.
- Condiciones visuales y temporales.
- Coordenadas relativas, multimonitor y mejor manejo de DPI.
- Simulación, logs y diagnóstico.
- Editor visual de automatizaciones.
- Variables, contadores y recuperación ante errores.
- Un sistema extensible de acciones cuando la base actual sea suficientemente estable.

El detalle de versiones y prioridades se mantiene en [ROADMAP.md](ROADMAP.md).

## Criterio para nuevas funciones

Antes de incorporar una función nueva conviene responder tres preguntas:

1. ¿Ayuda a automatizar una interacción repetitiva real?
2. ¿Puede integrarse de forma comprensible para alguien que no quiera escribir código?
3. ¿Encaja mejor como capacidad general de automatización que como solución para un único juego o aplicación?

Si la respuesta es sí, probablemente encaja con la dirección de AutoInputR.
