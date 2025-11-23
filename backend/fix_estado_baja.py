#!/usr/bin/env python3
"""
Script para corregir el estado_baja de animales existentes.
Este script asegura que todos los animales existentes tengan estado_baja = 'activo'
si el campo es NULL o no existe.
"""
import sys
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.database.db import get_connection

def fix_estado_baja():
    """Corrige el estado_baja de todos los animales existentes."""
    conn = None
    try:
        conn = get_connection()
        if conn is None:
            print("[ERROR] No se pudo conectar a la base de datos. Verifique las variables de entorno.")
            return False
        cursor = conn.cursor()
        
        print("Corrigiendo estado_baja de animales existentes...")
        
        # Actualizar todos los registros donde estado_baja es NULL o vacío a 'activo'
        cursor.execute("""
            UPDATE ganado 
            SET estado_baja = 'activo' 
            WHERE estado_baja IS NULL OR estado_baja = ''
        """)
        rows_updated_1 = cursor.rowcount
        
        # Corregir valores inválidos (que no sean 'activo' ni 'dado_de_baja')
        cursor.execute("""
            UPDATE ganado 
            SET estado_baja = 'activo',
                causa_baja = NULL,
                fecha_baja = NULL,
                observaciones_baja = NULL
            WHERE estado_baja NOT IN ('activo', 'dado_de_baja')
               OR (estado_baja IS NULL)
        """)
        rows_updated_2 = cursor.rowcount
        
        conn.commit()
        
        print(f"[OK] Actualizados {rows_updated_1 + rows_updated_2} registros")
        print("[OK] Correccion completada exitosamente")
        
        # Verificar el resultado
        cursor.execute("SELECT COUNT(*) FROM ganado WHERE estado_baja IS NULL OR estado_baja = ''")
        null_count = cursor.fetchone()[0]
        
        if null_count > 0:
            print(f"[ADVERTENCIA] Aun hay {null_count} registros con estado_baja NULL o vacio")
        else:
            print("[OK] Todos los registros tienen estado_baja valido")
        
        cursor.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Error al corregir estado_baja: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    success = fix_estado_baja()
    sys.exit(0 if success else 1)

