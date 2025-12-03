-- Script para asegurar aislamiento multi-tenant correcto
-- IMPORTANTE: tenant_id debe estar SOLO en la tabla personas, NO en usuarios

-- 1. Verificar que personas tiene tenant_id
-- Si no existe, agregarlo
ALTER TABLE personas 
ADD COLUMN IF NOT EXISTS tenant_id INT NULL;

-- 2. Sincronizar tenant_id desde usuarios a personas (si existe en usuarios)
-- Esto es para migración de datos existentes
UPDATE personas p
INNER JOIN usuarios u ON p.id = u.id_persona
SET p.tenant_id = u.tenant_id
WHERE p.tenant_id IS NULL AND u.tenant_id IS NOT NULL;

-- 3. Asegurar que todas las personas tengan tenant_id (excepto super_admin)
-- Asignar tenant_id 'default' si no tiene uno
UPDATE personas p
INNER JOIN usuarios u ON p.id = u.id_persona
INNER JOIN roles r ON u.id_rol = r.id
SET p.tenant_id = (SELECT id FROM tenants WHERE codigo_tenant = 'default' LIMIT 1)
WHERE p.tenant_id IS NULL 
  AND LOWER(TRIM(r.rol)) != 'super_admin';

-- 4. Crear índice para mejorar rendimiento de consultas filtradas por tenant_id
CREATE INDEX IF NOT EXISTS idx_personas_tenant_id ON personas(tenant_id);

-- 5. Verificar que no haya personas sin tenant_id (excepto super_admin)
-- Esto es solo para reporte, no modifica datos
SELECT 
    p.id,
    p.primer_nombre,
    p.primer_apellido,
    p.email,
    r.rol,
    p.tenant_id
FROM personas p
LEFT JOIN usuarios u ON p.id = u.id_persona
LEFT JOIN roles r ON u.id_rol = r.id
WHERE p.tenant_id IS NULL 
  AND (r.rol IS NULL OR LOWER(TRIM(r.rol)) != 'super_admin');

-- NOTA: Si la tabla usuarios tiene columna tenant_id, se puede eliminar después de migrar:
-- ALTER TABLE usuarios DROP COLUMN IF EXISTS tenant_id;

