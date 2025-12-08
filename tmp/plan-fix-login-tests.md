# Plan: Fix Login Loading Tests

- Estado actual: `Login.spec.js` falla en dos pruebas porque `loading` vuelve a `false` antes de validarse debido a que el mock de `authService.login` resuelve/rechaza inmediatamente.
- Estado final: las pruebas controlan cuándo se resuelve/rechaza la promesa para verificar el estado `loading` mientras la operación aún está pendiente y luego validar resultados (sessionStorage, Swal, redirección, limpieza).
- Archivos a modificar: `frontend/src/views/public/Login.spec.js`
- Tareas:
  1. Agregar un helper `createDeferred` para controlar manualmente la resolución/rechazo de la promesa del login.
  2. Reescribir el test de flujo exitoso para usar el helper y esperar el estado `loading` antes de resolver, luego verificar side effects después.
  3. Reescribir el test de loading en caso de error para mantener `loading` activo hasta que el mock falle y confirmar que se restablece.

