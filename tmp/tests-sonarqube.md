## Estado actual
- El proyecto no cuenta con pruebas automatizadas y SonarQube reporta 0 % de cobertura para el código reciente.

## Estado final
- Carpeta de pruebas creada siguiendo la convención `backend/tests`.
- Suites de pytest que cubran funciones críticas modificadas recientemente sin acceder a recursos externos (DB, red).
- Ejecución de las pruebas genera cobertura suficiente para SonarQube (>80 % sobre el código nuevo).

## Archivos a modificar
- `backend/requirements.txt`
- `backend/tests/test_config.py`
- `backend/tests/test_reporte_service.py`
- `frontend/tests/test_dashboard_random.js`

## Lista de tareas
1. Añadir dependencias de pruebas (pytest, pytest-cov) al entorno backend.
2. Crear estructura `backend/tests` con fixtures mínimos y pruebas para los helpers `_require_env` y generación de PDF.
3. Añadir pruebas ligeras para el generador aleatorio del dashboard en el frontend (usando Vitest o Jest según stack).
4. Documentar comandos para ejecutar las suites de pruebas con cobertura.

