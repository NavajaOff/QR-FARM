# Plan - Restricción fecha nacimiento ganado

- **Estado actual:** El formulario de registro de ganado no impide seleccionar fechas posteriores y el backend no valida que la fecha de nacimiento esté en el pasado.
- **Estado deseado:** El input de fecha usa la fecha actual como máximo permitido y el backend rechaza cualquier fecha de nacimiento futura tanto en creación como en actualización del ganado.
- **Archivos a modificar:** `frontend/src/assets/js/gestionar_animales.js`, `backend/src/controllers/animal_controller.py`
- **Tareas**
  - Añadir un helper que calcule la fecha de hoy en formato `YYYY-MM-DD` y usarlo para fijar el atributo `max` del input de fecha en el modal de creación de animales.
  - Extender el controlador de animales con una verificación reusable que compare la fecha enviada con la fecha del sistema y lanzarla en creación/actualización.

