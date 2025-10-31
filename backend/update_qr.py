#!/usr/bin/env python3
"""
Script para asignar códigos QR a animales existentes.
"""

import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.db import get_connection
from src.services.qr_service import QRService

def asignar_qr_a_animales_existentes():
    """Asigna códigos QR a todos los animales que no los tengan."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Obtener animales que no tienen QR
        cursor.execute("""
            SELECT g.id, g.nombre
            FROM ganado g
            LEFT JOIN qr q ON g.id = q.id_ganado
            WHERE q.id_ganado IS NULL
        """)

        animales_sin_qr = cursor.fetchall()

        print(f"Encontrados {len(animales_sin_qr)} animales sin QR")

        for animal in animales_sin_qr:
            print(f"Asignando QR al animal {animal['id']}: {animal['nombre']}")
            success = QRService.crear_qr_ganado(animal['id'])
            if success:
                print(f"✓ QR asignado correctamente")
            else:
                print(f"✗ Error asignando QR")

        conn.close()
        print("Proceso completado")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asignar_qr_a_animales_existentes()