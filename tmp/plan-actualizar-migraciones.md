# Plan: Actualizar migraciones según el dump

## Estado actual
- Las migraciones en `backend/src/database/migrations/versions` ya crean las tablas, pero mantienen registros de prueba para `ganado`, `potrero`, `personas` y `usuarios`, y `estado_ganado` incluye el estado `dado_de_baja`.
- 006_implementar_esquema... aplica transformaciones dinámicas, pero no refleja exactamente la estructura y datos del dump oficial.

## Estado deseado
- Las migraciones deben reflejar la estructura del dump compartido, usando la misma configuración de columnas y relaciones.
- No debe haber inserciones automáticas para `ganado`, `potrero`, `personas` ni `usuarios`.
- `estado_ganado` conservará todos los estados salvo `dado_de_baja` (id 4) y se documentará ese cambio.

## Archivos a modificar
- `backend/src/database/migrations/versions/001_inicial.py`
- `backend/src/database/migrations/versions/003_refactorizar_estados_baja.py`

## Tareas
1. Alinear la migración inicial con el esquema del dump y eliminar cualquier inserción de datos no deseados.
2. Ajustar la migración de refactorización de estados para evitar reinserciones de `dado_de_baja`.
3. Revisar la migración del esquema ERD para que la tabla `potrero` refleje exactamente la estructura mostrada en el administrador de bases de datos (sin la columna antigua `estado`, con fechas auto-gestionadas, etc.).
4. Confirmar que las demás referencias al estado `dado_de_baja` se eliminan o documentan para evitar inconsistencias futuras.

