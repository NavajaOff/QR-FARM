## Estado actual
- Variables sensibles posiblemente hardcodeadas en `backend/src`, especialmente en controladores y módulos de conexión.
- Nombres de constantes y mensajes que incluyen términos como “password” podrían generar falsas alarmas o malas prácticas.

## Estado final
- Variables sensibles extraídas a `os.getenv` sin credenciales en el código fuente.
- Mensajes o constantes de texto renombrados para evitar términos sensibles sin cambiar su significado.
- Revisión realizada en controladores y módulos de conexión de `backend/src`.

## Archivos a modificar
- `backend/src/controllers/usuario_controller.py`
- Archivos adicionales en `backend/src` donde se encuentren credenciales expuestas o términos a renombrar.

## Lista de tareas
1. Buscar términos sensibles (`password`, `secret`, `token`, `key`, etc.) en `backend/src`.
2. Auditar cada coincidencia para detectar credenciales hardcodeadas.
3. Extraer credenciales reales a variables de entorno con `os.getenv`.
4. Renombrar constantes de mensajes para evitar términos sensibles.
5. Verificar que controladores y módulos de conexión sigan el patrón seguro propuesto.

