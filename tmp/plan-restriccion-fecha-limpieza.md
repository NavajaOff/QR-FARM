# Plan: Restricción de fecha de última limpieza

## Estado actual
- Los formularios que registran la última limpieza aceptan fechas futuras desde el UI.
- El backend recibe los datos sin verificar que la fecha no supere el día actual.
- La lógica del componente y del controlador ya existentes no contemplan esta regla adicional.

## Estado final
- El campo `ultima_limpieza` solo podrá seleccionar fechas hasta el día actual gracias al atributo `max` controlado por una cadena compatible con `<input type="date">`.
- El endpoint de creación/actualización de potreros rechazará solicitudes cuya `ultima_limpieza` esté en el futuro, devolviendo un error claro sin alterar la estructura existente.

## Archivos a modificar
- `frontend/src/assets/js/gestionar-potreros.js`
- `backend/src/controllers/potrero_controller.py`

## Tareas
1. Añadir una referencia a la fecha actual en formato YYYY-MM-DD y aplicar ese valor como `max` al campo de fecha en los formularios de crear y editar potrero.
2. Insertar la validación en el controlador para que la API rechace fechas futuras antes de delegar en el servicio.

