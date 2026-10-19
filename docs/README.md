# AutoInputR

**AutoInputR — Automatización visual y configurable para Windows, sin necesidad de escribir scripts.**

AutoInputR es una aplicación de escritorio para Windows orientada a automatizar interacciones repetitivas con interfaces gráficas. Permite configurar clicks, pulsaciones de teclado, movimientos del cursor, rutas grabadas y acciones basadas en detección visual desde una interfaz gráfica, sin exigir al usuario escribir código.

![AutoInputR](images/captura-principal.png)

## Propósito del proyecto

AutoInputR busca reducir la distancia entre una tarea repetitiva y una automatización funcional. Su enfoque es ofrecer una herramienta local, comprensible y extensible para automatizaciones de escritorio de complejidad baja o media.

El proyecto se desarrolla como **proyecto personal de software y automatización con enfoque de portafolio**, con potencial para evolucionar hacia una herramienta general de automatización de escritorio. Los juegos pueden ser uno de sus escenarios de uso, pero no constituyen el propósito principal del producto.

La definición completa de producto, usuarios objetivo, principios y límites se encuentra en [PRODUCT.md](PRODUCT.md).

## Versión actual

**AutoInputR v1.3.0**

La rama de desarrollo puede contener refactors internos posteriores a la publicación de v1.3.0 sin cambiar todavía la versión pública.

## Descargar AutoInputR

La versión oficial más reciente se encuentra en **Releases**:

[Descargar AutoInputR v1.3.0](https://github.com/RobDev512/AutoInputR-Desktop/releases/download/v1.3.0/AutoInputR_Setup_v1.3.0.exe)

## Características

### Clicker

- Clicks automáticos con intervalos configurables.
- Click simple o doble.
- Botón izquierdo, derecho o central.
- Posición actual del cursor o coordenadas fijas.
- Repetición limitada o indefinida.
- Modo Turbo.

### KeyPresser

- Repetición automática de una tecla seleccionada.
- Intervalos configurables.
- Repetición limitada o indefinida.
- Hotkeys globales.
- Modo Turbo.

### Mover

- Movimiento automático del cursor dentro de una zona seleccionada.
- Diferentes patrones de movimiento.
- Desplazamiento suave.
- Velocidad configurable.
- Clicks periódicos para evitar inactividad.

### Ruta

- Grabación de movimientos del cursor.
- Registro de clicks durante la grabación.
- Reproducción de rutas.
- Velocidad de reproducción configurable.
- Grabación mientras otra aplicación o juego permanece enfocado.
- HUD visual durante la grabación en juego.

### Rastreador

- Selección de una zona de búsqueda.
- Captura de una imagen objetivo.
- Rastreo visual mediante plantillas.
- Movimiento suave hacia el objetivo detectado.
- Coincidencia mínima configurable.
- Micro movimientos para activar elementos mediante hover.
- Clicks periódicos anti-AFK.

### Ventana objetivo

- Selector de ventana objetivo.
- Identificación por título, proceso y clase.
- Pausa automática al perder el foco.
- Reanudación automática al recuperarlo.
- Protección aplicada a Clicker, KeyPresser, Mover, Ruta y Rastreador.
- Persistencia de la selección entre ejecuciones.

### Funciones generales

- Hotkeys globales configurables.
- Configuración persistente.
- Opción para mantener la aplicación encima.
- Integración con la bandeja del sistema.
- Interfaz desarrollada con CustomTkinter.

## Casos de uso

AutoInputR está pensado para automatizaciones sencillas y locales, por ejemplo:

- Repetir interacciones de mouse o teclado.
- Reproducir secuencias para pruebas o demostraciones.
- Automatizar pequeños flujos en programas que no ofrecen una API adecuada.
- Ejecutar acciones condicionadas por una ventana objetivo.
- Experimentar con automatización visual y reconocimiento por plantilla.
- Crear rutinas personales repetitivas de bajo riesgo.

El uso en juegos es secundario y debe limitarse a contextos donde la automatización esté permitida por sus reglas o términos de servicio.

## Estructura del proyecto

El código se organiza como un paquete Python en `autoinputr/`:

```text
AutoInputR.py                 Punto de entrada

assets/                       Recursos visuales
docs/                         Documentación del proyecto
packaging/                    Compilación e instalador
requirements/                 Dependencias de ejecución y desarrollo
tests/                        Pruebas automáticas
data/                         Datos locales generados (ignorado por Git)

autoinputr/
├── app.py                    Ventana principal y coordinación
├── core/
│   ├── config.py             Lectura/escritura de configuración
│   ├── hotkeys.py            Listener y hotkey global principal
│   ├── resources.py          Rutas, versión y recursos
│   └── target_window.py      Reglas de ventana objetivo
├── modules/
│   ├── clicker.py
│   ├── keypresser.py
│   ├── mover.py
│   ├── ruta.py
│   └── rastreador.py
├── services/
│   ├── input_backend.py      PyAutoGUI/PyDirectInput
│   ├── tray.py               Bandeja y ciclo de cierre
│   ├── vision.py             Operaciones OpenCV del Rastreador
│   └── windows.py            Operaciones Win32
└── ui/
    └── dialogs/
        ├── settings.py
        └── window_selector.py
```

Consulta [ARCHITECTURE.md](ARCHITECTURE.md) para más detalle.

También puedes consultar [PRODUCT.md](PRODUCT.md), [ROADMAP.md](ROADMAP.md) y [CHANGELOG.md](CHANGELOG.md).

## Desarrollo

Instala las dependencias y ejecuta el punto de entrada:

```powershell
python -m pip install -r .\requirements\runtime.txt
python .\AutoInputR.py
```

Validación rápida:

```powershell
python -m compileall -q .\AutoInputR.py .\autoinputr
python -m unittest discover -s .\tests -v
```

Las instrucciones completas están en [DEVELOPMENT.md](DEVELOPMENT.md).

## Empaquetado

Los archivos de empaquetado se encuentran en `packaging/`:

```text
packaging/build.ps1
packaging/AutoInputR.iss
```

La secuencia recomendada es: implementar → probar desde Python → estabilizar → documentar → compilar → crear instalador → publicar Release.

## Uso responsable

AutoInputR es una herramienta de automatización general. El usuario es responsable de comprobar que su utilización esté permitida por las reglas, términos y condiciones de las aplicaciones, juegos o servicios donde la ejecute.

## Código fuente y derechos

El código fuente de este repositorio es públicamente visible. **Eso no implica una licencia de código abierto.** Mientras el repositorio no incluya una licencia que conceda permisos adicionales, se mantienen reservados los derechos correspondientes.

Se permite descargar, instalar y utilizar gratuitamente la versión oficial compilada de AutoInputR para uso personal. Sin autorización previa del autor, no se autoriza redistribuir versiones modificadas, comercializar AutoInputR, presentarlo como una creación propia ni reutilizar su identidad visual en productos derivados, salvo los derechos que otorgue expresamente la legislación aplicable.

AutoInputR se proporciona tal cual, sin garantías.

## Autor

Desarrollado por Robert.

Copyright © 2026 Robert. Todos los derechos reservados.
