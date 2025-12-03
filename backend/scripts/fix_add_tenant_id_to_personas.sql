-- Script CRÍTICO: Agregar columna tenant_id a la tabla personas si no existe
-- Este script es necesario para que el aislamiento multi-tenant funcione

-- 1. Agregar columna tenant_id a personas si no existe
ALTER TABLE personas 
ADD COLUMN IF NOT EXISTS tenant_id INT NULL;

-- 2. Si la columna ya existe pero está vacía, sincronizar desde usuarios (si existe)
UPDATE personas p
INNER JOIN usuarios u ON p.id = u.id_persona
SET p.tenant_id = u.tenant_id
WHERE p.tenant_id IS NULL AND u.tenant_id IS NOT NULL;

-- 3. Asignar tenant_id 'default' a usuarios que no tienen tenant (excepto super_admin)
UPDATE personas p
INNER JOIN usuarios u ON p.id = u.id_persona
INNER JOIN roles r ON u.id_rol = r.id
SET p.tenant_id = (SELECT id FROM tenants WHERE codigo_tenant = 'default' LIMIT 1)
WHERE p.tenant_id IS NULL 
  AND (r.rol IS NULL OR LOWER(TRIM(r.rol)) != 'super_admin')
  AND EXISTS (SELECT 1 FROM tenants WHERE codigo_tenant = 'default');

-- 4. Crear índice para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_personas_tenant_id ON personas(tenant_id);

-- 5. Verificar resultado
SELECT 
    'Total personas' as descripcion,
    COUNT(*) as cantidad
FROM personas
UNION ALL
SELECT 
    'Personas con tenant_id' as descripcion,
    COUNT(*) as cantidad
FROM personas
WHERE tenant_id IS NOT NULL
UNION ALL
SELECT 
    'Personas sin tenant_id' as descripcion,
    COUNT(*) as cantidad
FROM personas
WHERE tenant_id IS NULL;

