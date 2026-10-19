# Checklist de Release de AutoInputR

## Código

- [ ] `APP_VERSION` tiene la versión correcta.
- [ ] `packaging/AutoInputR.iss` usa la misma versión.
- [ ] No existen restos de funciones experimentales canceladas.
- [ ] `config.json` mantiene compatibilidad o existe una migración explícita.

## Pruebas

- [ ] `python -m compileall -q .\AutoInputR.py .\autoinputr` termina sin errores.
- [ ] `python -m unittest discover -s .\tests -v` termina correctamente.
- [ ] Clicker probado.
- [ ] KeyPresser probado.
- [ ] Mover probado.
- [ ] Ruta y grabadores probados.
- [ ] Rastreador probado.
- [ ] Ventana objetivo probada con cambio de foco y reanudación.
- [ ] Configuración persiste después de cerrar/reabrir.
- [ ] Bandeja del sistema y cierre probados.

## Empaquetado

- [ ] PyInstaller termina correctamente.
- [ ] Ejecutable generado inicia sin consola y carga iconos.
- [ ] Inno Setup compila el instalador.
- [ ] Instalación limpia probada.
- [ ] Desinstalación probada.

## Documentación y publicación

- [ ] README actualizado.
- [ ] CHANGELOG actualizado.
- [ ] ROADMAP actualizado si corresponde.
- [ ] Release de GitHub creado.
- [ ] Instalador adjunto al Release.
- [ ] SHA-256 calculado y verificado.
- [ ] Enlaces de descarga revisados.
