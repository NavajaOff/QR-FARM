# Solución Definitiva para Aislamiento Multi-Tenant

## Problema Resuelto

El sistema ahora tiene **aislamiento total por tenant** usando la tabla `personas` como fuente única de verdad para `tenant_id`.

## Cambios Implementados

### 1. JWT Token Incluye tenant_id
- El token JWT ahora incluye `tenant_id` desde `personas` al iniciar sesión
- El `tenant_id` se obtiene desde `personas.tenant_id`, NO desde `usuarios.tenant_id`

### 2. Filtrado Estricto en Todas las Consultas
- Todas las consultas SQL filtran por `p.tenant_id` (personas.tenant_id)
- Se agregó validación doble: filtro SQL + validación en código Python
- Los usuarios solo ven datos de su mismo `tenant_id`

### 3. Logs de Depuración
- Logs extensivos para rastrear el `tenant_id` en cada paso
- Logs muestran cuando un usuario es bloqueado por no coincidir el tenant_id

## Script SQL de Migración

Ejecuta el script `backend/scripts/fix_tenant_isolation.sql` para:
1. Asegurar que `personas` tiene columna `tenant_id`
2. Sincronizar datos existentes desde `usuarios` a `personas` (si aplica)
3. Crear índice para mejorar rendimiento
4. Verificar que no haya personas sin `tenant_id` (excepto super_admin)

## Pasos para Aplicar la Solución

1. **Ejecutar script SQL** (opcional, solo si necesitas migrar datos):
   ```bash
   mysql -u usuario -p nombre_base_datos < backend/scripts/fix_tenant_isolation.sql
   ```

2. **Reiniciar el servidor backend**:
   ```bash
   # Detener el servidor actual
   # Iniciar nuevamente
   python app.py
   ```

3. **Cerrar sesión y volver a iniciar sesión**:
   - Esto generará un nuevo token JWT con `tenant_id` incluido
   - Los tokens antiguos seguirán funcionando (con fallback a BD)

4. **Verificar el aislamiento**:
   - Inicia sesión como "Jose David" (tenant "default")
   - Debe ver solo usuarios con `tenant_id = "default"`
   - "Juan Castro" (otro tenant) NO debe aparecer
   - "Violeta" (creada por Jose David) SÍ debe aparecer

## Estructura de Datos

### Tabla `personas`
- `id` (PK)
- `tenant_id` (FK a tenants) ← **FUENTE ÚNICA DE VERDAD**
- `id_rol`
- `primer_nombre`, `segundo_nombre`, `primer_apellido`, `segundo_apellido`
- `email`, `telefono`
- `fecha_creacion`

### Tabla `usuarios`
- `id` (PK)
- `id_persona` (FK a personas)
- `id_rol`
- `contrasena`
- `estado`
- `tenant_id` (opcional, redundante, se puede eliminar)

## Validaciones Implementadas

1. **En `token_required`**: Obtiene `tenant_id` del token JWT o desde `personas`
2. **En `obtener_todos_usuarios`**: Filtra por `p.tenant_id` en SQL
3. **En `_crear_usuario_desde_resultado`**: Obtiene `tenant_id` desde `p.*` (personas)
4. **Validación doble**: Filtro SQL + validación en código Python
5. **Logs extensivos**: Rastrean `tenant_id` en cada paso crítico

## Troubleshooting

Si aún ves usuarios de otros tenants:

1. **Verifica los logs del backend**:
   - Busca `[TENANT]` y `[USUARIO_SERVICE]` en los logs
   - Verifica que el `tenant_id` se esté filtrando correctamente

2. **Verifica el token JWT**:
   - Decodifica el token en https://jwt.io
   - Verifica que incluya `tenant_id`

3. **Verifica la base de datos**:
   ```sql
   SELECT p.id, p.primer_nombre, p.email, p.tenant_id 
   FROM personas p 
   WHERE p.email = 'josedavidhernandeznavaja@gmail.com';
   ```

4. **Ejecuta el script SQL de migración** si es necesario

## Resultado Esperado

✅ **Jose David** (tenant "default") solo ve:
- Jose David (él mismo)
- Violeta (creada por él, mismo tenant)

❌ **Jose David** NO ve:
- Juan Castro (otro tenant)

✅ **Super Admin** puede ver todos los usuarios (con o sin filtro por `tenant_id` en query params)

