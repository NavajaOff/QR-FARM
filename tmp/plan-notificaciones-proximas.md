# Plan: Notificaciones de limpieza y vacunación

## Estado actual
- No existe un mecanismo de notificaciones para fechas próximas de limpieza o vacunación.
- Ni el backend ni el frontend exponen información centralizada sobre los próximos eventos.

## Estado final
- El backend expone un endpoint `/api/notificaciones/proximas` que combina eventos de limpieza y vacunación próximos.
- El frontend muestra un botón de campana en `AdminLayout` con las notificaciones recientes y el número de alertas.
- Se reutiliza el selector de tenant para filtrar automáticamente los resultados según el contexto.

## Archivos a modificar
- `backend/src/services/notification_service.py`
- `backend/src/controllers/notification_controller.py`
- `backend/src/routes/notification_routes.py`
- `backend/app.py`
- `backend/tests/test_notification_service.py`
- `frontend/src/services/api.js`
- `frontend/src/layouts/AdminLayout.vue`

## Lista de tareas
1. Crear el servicio de notificaciones que consulte fechas próximas en `historial_potreros` y `vacunacion`.
2. Añadir controlador y ruta que exponga los datos en formato JSON con contexto multi-tenant.
3. Registrar la nueva ruta en `app.py`.
4. Escribir pruebas unitarias del servicio que verifiquen datos combinados y manejo de errores.
5. Extender `api.js` con la nueva ruta.
6. Mostrar las notificaciones en la cabecera del layout administrativo con el número de alertas y un listado.

