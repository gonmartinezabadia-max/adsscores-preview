# Publicación de Ads Scores preview

Los cuatro recursos en `required-assets/` son fixtures históricos, byte a byte del commit `7083c43edd74639618ef1659ca5da707c4751cda`.
`build-commit.txt` y `build-source.json` describen aquella entrega histórica, NO el commit actual de Pages. No regenerarlos para simular una procedencia distinta.

## Publicar un export revisado

Desde un checkout limpio de `gh-pages`:

```sh
python3 .github/publication/publish.py --export /ruta/al/export --expected-head COMMIT_REMOTO_VERIFICADO --message 'Descripción del cambio' --push
```

El script comprueba HEAD local/remoto, incorpora los recursos al export ANTES del rsync, conserva `.github` y los chunks estáticos previos, verifica los cuatro hashes y vuelve a comprobar concurrencia antes de enviar. Sin `--push` solo prepara el árbol para inspección. No usar el rsync suelto ni los helpers antiguos de una entrega.

El build fuente también debe incluir estos cuatro archivos en `web/public`, con los scripts `prebuild` y `postbuild` que verifican `public` y `out`. El paquete de corrección incluye este delta del origen.

El workflow `required-preview-resources.yml` queda preparado pero NO activo: GitHub rechazó su publicación porque la credencial no tiene permiso workflow. Las pruebas locales verifican que cada ausencia y cada alteración se rechazan. La barrera previa al envío es `publish.py`, no un branch protection ni un bloqueo del workflow implícito Pages. No se han cambiado los ajustes de Pages.

## Comprobar después del deploy

1. Esperar el workflow Pages del commit enviado.
2. Descargar los cuatro recursos desde la URL publicada y comparar SHA256 contra `required-assets/sha256.json`.
3. Abrir `/app/aprobaciones/` y verificar visualmente los flujos existentes.

La revisión documental `review461.html` está disponible como página aislada. El bridge/iframe histórico no forma parte del frontend 7083/r4 y no se ha reintroducido con esta corrección. No activar ni ejecutar campañas para probar archivos estáticos.
