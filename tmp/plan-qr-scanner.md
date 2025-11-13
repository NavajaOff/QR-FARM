## Estado actual
- `QrScanner.vue` ya decodifica QR, consulta `/api/ganado/{id}` y muestra `GanadoDetailCard.vue`.
- `QRService.generar_codigo_qr` embebe un JSON con información básica, pero el frontend aún no consume estos datos sin conexión.
- La documentación y pruebas no cubren escenarios offline.

## Estado final deseado
- QR embebe un payload `qr-farm.v1` consistente (datos esenciales + URL) manteniendo compatibilidad con códigos antiguos.
- El escáner reconoce payloads embebidos: si no hay conexión, muestra la tarjeta con esa información; si la hay, sincroniza con la API y actualiza.
- La UI avisa cuando se muestran datos offline y permite refrescar al reconectar.
- Documentación y pruebas abarcan los flujos online/offline.

## Archivos a modificar o crear
- `backend/src/services/qr_service.py`
- `frontend/src/components/QrScanner.vue`
- `frontend/src/components/GanadoDetailCard.vue`
- `frontend/src/services/qr.ts`
- `frontend/README.md`
- (Opcional) composable/utilidad para detectar conectividad o cachear payloads.

## Lista de tareas
1. Revisar y ajustar la estructura del payload embebido en `QRService` garantizando compatibilidad.
2. Extender `QrScanner.vue` para diferenciar QR con JSON embebido de los que contienen solo ID/URL y manejar estados offline/online.
3. Actualizar `frontend/src/services/qr.ts` para transformar payloads embebidos a `GanadoResource` y decidir cuándo consultar la API.
4. Añadir indicadores en `GanadoDetailCard.vue` cuando la información provenga del QR y se esté mostrando en modo offline, con opción para refrescar.
5. Documentar los flujos y pruebas recomendadas (escaneo web, móvil offline/online) en `frontend/README.md`.
