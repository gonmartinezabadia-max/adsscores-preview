# Publicación y procedencia por export

Solo `feed-prueba-simulado.csv` y `review461.html` son fixtures byteexact de7083. Los archivos build-* NUNCA se copian desde fixtures.

## Build fuente

Asignar ADS_SCORES_RELEASE para cada build (por ejemplo ADS_SCORES_RELEASE=tiktok-test-rename-r4 npm run build). `postbuild` falla si falta o está vacía, no usa una release fija.

`prebuild` verifica los dos fixtures en public. `postbuild` verifica out y genera:
- build-source.json: release, fecha, hash de inventario fuente y export, commit BASE si existe.
- build-files.json: SHA256 de cada archivo publicado excepto estos cuatro metadatos, .git y .github. Incluye chunks retenidos.
- build-inputs.json: inventario de fuente observado; excluye artefactos de build, node_modules y metadatos generados.
- build-commit.txt: puntero al hash del inventario fuente. Ya no simula que el commit base identifica el árbol modificado.

No se infiere el backend: gateway se despliega por separado. Este inventario acredita bytes observados, no es una firma ni prueba de reproducibilidad del compilador.

## Publicar

En checkout limpio gh-pages, con export ya revisado y metadatos válidos:

```
python3 .github/publication/publish.py --export /ruta/export --source /ruta/fuente/web --release IDENTIDAD_RELEASE --expected-head SHA_REMOTO_VERIFICADO --message 'Descripción' --push
```

El publicador propaga provenance_mode desde el build-source.json del export, o rechaza un modo desconocido. Nunca convierte retrospectivo en postbuild. Se verifica procedencia ANTES de rsync, se conservan .github y chunks anteriores, se regeneran los metadatos sobre el árbol final (incluidos chunks retenidos) y se verifica antes de enviar. Solo entonces se comprueba HEAD remoto y se publica. No usar rsync suelto.

El hook postbuild debe generar sobre el export original. No copiar build-* de una entrega previa. Ante HTML/chunk añadido, eliminado o alterado, verify aborta. No usar generate para encubrir cambios no revisados.

## Reparación retrospectiva de hoy

No se recompila ni altera HTML/JS de la UI ya servida. Se inventaría el export existente como `retrospective_existing_export`, release tiktok-test-rename-r4. La fuente inventariada es el árbol local observado al reparar; NO prueba que cada byte de ese árbol fuese entrada del compilador anterior. El commit base ce4f917 es solo base y NO se presenta como source_commit limpio. El inventario export sí verifica exactamente los HTML/chunks servidos. La auditoría compara todos los bytes publicados, no solo el chunk de Aprobaciones.

Verificación: `python3 .github/publication/provenance.py verify .`, pruebas `test_provenance.py` y `test_required_assets.py`. CI opcional sigue sin permiso workflow; no se afirma gate automático remoto ni branch protection. El script de publicación es el gate operativo.
