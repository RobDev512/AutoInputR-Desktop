# Desarrollo de AutoInputR

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
python .\AutoInputR.py
```

## Validación mínima después de un cambio

```powershell
python -m compileall -q .\AutoInputR.py .\autoinputr
python -m unittest discover -s .\tests -v
```

Después abre la aplicación y prueba manualmente el módulo afectado. Si el cambio toca ventana objetivo o servicios compartidos, prueba también la interacción entre módulos.

## Reglas del refactor

- No cambiar comportamiento y arquitectura al mismo tiempo salvo que sea necesario.
- Mantener compatibilidad con `data/config.json` y conservar migración desde el `config.json` legado cuando corresponda.
- No reintroducir el experimento cancelado de Fusionador.
- No compilar instalador hasta que la ejecución desde Python sea estable.
- Mantener `AutoInputR.py` como punto de entrada pequeño.
- Colocar comportamiento específico del módulo en `autoinputr/modules/`.
- Colocar integraciones técnicas compartidas en `autoinputr/services/`.

## Empaquetado

Cuando la versión esté validada desde Python:

```powershell
powershell -ExecutionPolicy Bypass -File .\packaging\build.ps1
```

Después compila `packaging/AutoInputR.iss` con Inno Setup y sigue `RELEASE-CHECKLIST.md`.
