# Migración: Implementación del Esquema Completo según ERD

## Descripción

Esta migración (`006_esquema_erd`) implementa el esquema completo de la base de datos según el diagrama ERD proporcionado, asegurando que todas las tablas, campos, relaciones y constraints estén correctamente definidos.

## Cambios Implementados

### Tablas Nuevas
- **estado_potrero**: Tabla para estados de potrero con `id` y `nombre_estado` (UNIQUE)
- **historial_potreros**: Tabla para historial de potreros con campos de fechas según ERD

### Tablas Eliminadas
- **historial_potrero** (singular): Esta tabla es eliminada y reemplazada por `historial_potreros` (plural) según el ERD

### Tablas Actualizadas

#### roles
- Agregado campo `nivel` (Enum: 'global', 'tenant')
- Agregado campo `permisos` (JSON)

#### personas
- Asegura que `tenant_id` existe con FK a `tenants`
- Crea constraints UNIQUE en `email` y `telefono`

#### potrero
- Agregado `id_estado_potrero` con FK a `estado_potrero`
- Agregado `area` (Numeric 10,2)
- Agregado `fecha_creacion` y `fecha_actualizacion`
- Asegura que `tenant_id` existe

#### ganado
- Asegura que `tenant_id` existe con FK a `tenants`

#### vacunacion
- Elimina campos que no están en el ERD: `nombre_animal`, `fecha_inicio`, `fecha_fin`
- Asegura que `responsable` tiene FK a `personas`
- Asegura que `tenant_id` existe

#### qr
- Asegura que `tenant_id` existe con FK a `tenants`

#### usuarios
- Asegura que `tenant_id` existe con FK a `tenants`

### Migración de Datos

Si existe la tabla `historial_potrero` (singular), la migración:
1. Crea la tabla `historial_potreros` (plural) según el ERD si no existe
2. Migra los datos desde `historial_potrero` agrupando por `id_potrero`
3. Convierte eventos de tipo 'uso' y 'limpieza' a los campos correspondientes
4. **Elimina la tabla `historial_potrero`** después de migrar los datos

**Importante**: La tabla `historial_potrero` (singular) será eliminada permanentemente. Asegúrate de tener un backup si necesitas conservar los datos originales.

## Cómo Ejecutar la Migración

### Opción 1: Usando el Script PowerShell (Windows)

```powershell
cd backend
.\run-migrations.ps1
```

### Opción 2: Usando el Script Bash (Linux/Mac)

```bash
cd backend
chmod +x run-migrations.sh
./run-migrations.sh
```

### Opción 3: Manualmente con Alembic

```bash
cd backend
alembic -c alembic.ini upgrade head
```

### Opción 4: Desde Cero (Crear Base de Datos Nueva)

Si no tienes una base de datos local y quieres crearla desde cero:

1. **Crear la base de datos:**
   ```sql
   CREATE DATABASE gestion_ganadera CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. **Configurar variables de entorno** (crear archivo `.env` en la raíz del proyecto):
   ```
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=
   DB_NAME=gestion_ganadera
   DB_PORT=3306
   ```

3. **Ejecutar todas las migraciones:**
   ```powershell
   cd backend
   .\run-migrations.ps1
   ```

## Verificación

Después de ejecutar la migración, puedes verificar que todo esté correcto:

```bash
# Ver el estado actual de las migraciones
cd backend
alembic -c alembic.ini current

# Ver el historial de migraciones
alembic -c alembic.ini history

# Ver las tablas creadas (desde MySQL)
mysql -u root -p gestion_ganadera -e "SHOW TABLES;"
```

## Estructura Final según ERD

La migración asegura que la base de datos tenga la siguiente estructura:

- ✅ `tenants` - Multi-tenancy
- ✅ `roles` - Con nivel y permisos
- ✅ `personas` - Con tenant_id y UNIQUE en email/telefono
- ✅ `usuarios` - Con tenant_id
- ✅ `estado_ganado` - Estados del ganado
- ✅ `ganado` - Con tenant_id
- ✅ `estado_potrero` - Estados del potrero (NUEVO)
- ✅ `tipo_pasto` - Tipos de pasto
- ✅ `potrero` - Con id_estado_potrero, area, fechas
- ✅ `historial_potreros` - Historial con fechas (NUEVO/ACTUALIZADO)
- ✅ `qr` - Con tenant_id
- ✅ `tipo_vacuna` - Tipos de vacuna
- ✅ `vacunacion` - Con tenant_id, sin campos obsoletos

## Notas Importantes

1. **No destructiva**: La migración es cuidadosa y no elimina datos existentes
2. **Idempotente**: Puede ejecutarse múltiples veces sin causar errores
3. **Compatibilidad**: Mantiene compatibilidad con el código existente
4. **Migración de datos**: Si existe `historial_potrero`, los datos se migran automáticamente a `historial_potreros`

## Rollback

Si necesitas revertir la migración:

```bash
cd backend
alembic -c alembic.ini downgrade -1
```

**Nota**: Algunos cambios estructurales no pueden revertirse completamente sin pérdida de datos. Usa con precaución.

## Solución de Problemas

### Error: "Table already exists"
- La migración verifica si las tablas existen antes de crearlas
- Si persiste, verifica que no haya conflictos de nombres

### Error: "Duplicate entry for key"
- Puede ocurrir al crear constraints UNIQUE si hay datos duplicados
- Revisa los datos en `personas.email` y `personas.telefono`

### Error: "Foreign key constraint fails"
- Verifica que todas las tablas referenciadas existan
- Asegúrate de que los datos existentes tengan referencias válidas

## Soporte

Si encuentras problemas, verifica:
1. Que MySQL esté corriendo
2. Que las credenciales en `.env` sean correctas
3. Que la base de datos exista
4. Que no haya migraciones pendientes anteriores

