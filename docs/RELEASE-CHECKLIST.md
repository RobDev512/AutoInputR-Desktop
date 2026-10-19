# Checklist de Release de TaskPilot

## Código

- [ ] `APP_NAME` es `TaskPilot`.
- [ ] `APP_VERSION` tiene la versión final correcta y no conserva `-dev`.
- [ ] `packaging/TaskPilot.iss` usa la misma versión numérica.
- [ ] No existen restos de funciones experimentales canceladas.
- [ ] `data/config.json` mantiene compatibilidad.
- [ ] La migración desde archivos locales legados sigue funcionando.
- [ ] La transición desde una instalación anterior de AutoInputR fue probada.

## Pruebas

- [ ] `python -m compileall -q .\TaskPilot.py .\taskpilot` termina sin errores.
- [ ] `python -m unittest discover -s .\tests -v` termina correctamente.
- [ ] Clicker probado.
- [ ] KeyPresser probado.
- [ ] Mover probado.
- [ ] Ruta y grabadores probados.
- [ ] Rastreador probado.
- [ ] Ventana objetivo probada con cambio de foco y reanudación.
- [ ] Configuración persiste después de cerrar/reabrir.
- [ ] Bandeja del sistema y cierre probados.
- [ ] Icono, título y Acerca de muestran TaskPilot.

## Empaquetado

- [ ] PyInstaller termina correctamente.
- [ ] `TaskPilot.exe` inicia sin consola y carga iconos.
- [ ] Inno Setup compila el instalador.
- [ ] Actualización desde AutoInputR v1.3.0 probada.
- [ ] Instalación limpia probada.
- [ ] Desinstalación probada.

## Documentación y publicación

- [ ] `docs/README.md` actualizado.
- [ ] `docs/CHANGELOG.md` actualizado.
- [ ] `docs/ROADMAP.md` actualizado.
- [ ] Hub actualizado con la marca TaskPilot.
- [ ] Release de GitHub creado.
- [ ] Instalador adjunto al Release.
- [ ] SHA-256 calculado y verificado.
- [ ] Enlaces de descarga revisados.
