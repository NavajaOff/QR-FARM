## Estado actual
- El endpoint `GET /api/ganado/<int:id>` exige identificadores numéricos y delega en `GanadoService.obtener_ganado_detallado`, que solo busca por `id`.
- El escáner (`QrScanner.vue`) detecta payloads embebidos y muestra datos offline, pero la sincronización usa un único `resourceId`, lo que ocasiona 404 cuando el QR contiene un `codigo` alfanumérico.
- `fetchQrResource` no ofrece reintentos con identificadores alternativos y mapea cualquier 404 como "QR no reconocido".

## Estado final deseado
- El backend acepta identificadores numéricos o alfanuméricos en `/api/ganado/<identifier>` y `GanadoService.obtener_ganado_detallado` consulta primero por `id` y, si no existe, por `codigo_qr`.
- El frontend intenta sincronizar usando `id` y, ante un 404, reintenta automáticamente con `codigo` (cuando esté disponible) manteniendo los datos embebidos visibles.
- Los mensajes de error distinguen entre falta de registro y fallos de red, y la tarjeta se actualiza con datos completos cuando hay coincidencia.

## Archivos a modificar o crear
- `backend/app.py`
- `backend/src/services/animal_service.py`
- `frontend/src/services/qr.ts`
- `frontend/src/components/QrScanner.vue`

## Lista de tareas
1. Actualizar la ruta `/api/ganado/<identifier>` en `app.py` para permitir identificadores no numéricos y delegar en el servicio usando el nuevo parámetro.
2. Extender `GanadoService.obtener_ganado_detallado` para aceptar `Union[int, str]`, buscar por `id` y, en caso de no encontrar, consultar por `codigo_qr`.
3. Ajustar `fetchQrResource` para aceptar una lista de candidatos (`id`, `codigo`) y reintentar automáticamente cuando el primer intento arroje 404.
4. Propagar en `QrScanner.vue` los identificadores candidatos desde el payload embebido y actualizar los mensajes de sincronización manteniendo el modo offline cuando falle la API.

