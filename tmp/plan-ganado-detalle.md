# Plan: aumentar cobertura de `obtener_ganado_detallado`

- Estado actual: `GanadoService.obtener_ganado_detallado` muestra prints y construye el detalle completo, pero los tests nunca ejecutan el bloque que procesa las filas, llama a `_fetch_vacunas` y regresa el diccionario final, dejando parte del código sin cobertura (reportado ~48% en la sección nueva).
- Estado final: crear al menos una prueba que simule una fila válida desde la base de datos y verifique que se construyen los campos `propietario`, `potrero`, `vacunas` y que se cierra la conexión/cursor; así se ejecuta el bloque que se estaba omitiendo.
- Archivos a modificar: `backend/tests/test_animal_service.py`
- Tareas:
  1. Añadir un helper en el test que prepare conexión/cursor y datos simulados para la consulta que utiliza `obtener_ganado_detallado`.
  2. Escribir un test que llame al método con `tenant_id_override` y asegure que `_fetch_vacunas` es invocado y que el resultado contiene los datos esperados.
  3. Confirmar que el cursor y la conexión se cierran al terminar y que la función devuelve el diccionario completo.

