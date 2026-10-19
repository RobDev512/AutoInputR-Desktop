# Desarrollo de TaskPilot

## Preparación

Desde PowerShell en la raíz del repositorio:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r .\requirements\dev.txt
```

## Ejecutar desde Python

```powershell
python .\TaskPilot.py
```

## Validación mínima después de un cambio

```powershell
python -m compileall -q .\TaskPilot.py .\taskpilot
python -m unittest discover -s .\tests -v
```

Después abre la aplicación y prueba manualmente el módulo afectado. Si el cambio toca ventana objetivo o servicios compartidos, prueba también la interacción entre módulos.

## Reglas de desarrollo

- Mantener compatibilidad con `data/config.json` y con la migración desde AutoInputR cuando corresponda.
- No reintroducir el experimento cancelado de Fusionador.
- No compilar instalador hasta que la ejecución desde Python sea estable.
- Mantener `TaskPilot.py` como punto de entrada pequeño.
- Colocar comportamiento específico del módulo en `taskpilot/modules/`.
- Colocar integraciones técnicas compartidas en `taskpilot/services/`.
- Mantener los nombres históricos AutoInputR únicamente donde documenten versiones anteriores o compatibilidad.

## Empaquetado

Cuando la versión esté validada desde Python:

```powershell
powershell -ExecutionPolicy Bypass -File .\packaging\build.ps1
```

Después compila `packaging/TaskPilot.iss` con Inno Setup y sigue `RELEASE-CHECKLIST.md`.
