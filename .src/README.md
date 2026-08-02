# Fuentes de los atajos

`camara-sin-firmar.shortcut` y `galeria-sin-firmar.shortcut` son los plist XML
editables. Los publicados en la raiz son estos mismos, firmados:

    shortcuts sign --mode anyone --input .src/camara-sin-firmar.shortcut --output nutriscan-camara.shortcut

Desde iOS 15 Apple exige firma para importar un atajo y no se puede firmar en el
dispositivo: si se publica sin firmar, iOS no lo importa. Tras editar un plist
hay que volver a firmarlo.

## Identificadores y parametros verificados

| Accion | Identificador | Parametros | Salida |
|---|---|---|---|
| Tomar foto | `is.workflow.actions.takephoto` | `WFCameraCaptureDevice`, `WFCameraCaptureShowPreview`, `WFPhotoCount` | `Photo` |
| Seleccionar fotos | `is.workflow.actions.selectphoto` | `WFSelectMultiplePhotos` | `Photos` |
| Extraer texto | `is.workflow.actions.extracttextfromimage` | `imageFile` (iOS 26+), `WFImage` (anteriores) | `Text` |
| Codificar URL | `is.workflow.actions.urlencode` | `WFEncodeMode: Encode`, `WFInput` | `URL Encoded Text` |
| Abrir URL | `is.workflow.actions.openurl` | `WFInput` | — |

La accion de OCR se emite con los dos nombres de parametro de imagen a la vez:
ToolKit v78 usa `imageFile` y las versiones anteriores `WFImage`. El parametro
que el sistema no reconoce se ignora.
