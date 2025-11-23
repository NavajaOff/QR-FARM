-- Script SQL para corregir el estado_baja de animales existentes
-- Este script asegura que todos los animales existentes tengan estado_baja = 'activo'
-- si el campo es NULL o no existe

-- Primero, verificar si la columna existe y si no, crearla
-- (Esto debería hacerse mediante la migración, pero por si acaso)

-- Actualizar todos los registros donde estado_baja es NULL a 'activo'
UPDATE ganado 
SET estado_baja = 'activo' 
WHERE estado_baja IS NULL OR estado_baja = '';

-- Verificar que todos los animales tengan estado_baja = 'activo' (excepto los que realmente están dados de baja)
-- Si hay animales que deberían estar activos pero tienen otro valor, corregirlos
UPDATE ganado 
SET estado_baja = 'activo',
    causa_baja = NULL,
    fecha_baja = NULL,
    observaciones_baja = NULL
WHERE estado_baja IS NULL 
   OR estado_baja = ''
   OR (estado_baja != 'dado_de_baja' AND estado_baja != 'activo');

