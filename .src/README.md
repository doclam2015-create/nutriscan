# Fuentes de los atajos

`camara-sin-firmar.shortcut` y `galeria-sin-firmar.shortcut` son los plist XML
editables. iOS 15 y posteriores exigen firma para importar un atajo, asi que los
publicados en la raiz estan firmados con:

    shortcuts sign --mode anyone --input .src/camara-sin-firmar.shortcut --output nutriscan-camara.shortcut

Tras editar un plist hay que volver a firmarlo; si se publica sin firma, iOS
rechaza la importacion en silencio o muestra el archivo como texto.
