#!/usr/bin/env python3
"""
Script de configuración inicial de la base de datos
Ejecuta las migraciones para configurar la base de datos desde cero
"""

import sys
import os
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def setup_database():
    """Configurar la base de datos con migraciones"""
    print("🚀 Iniciando configuración de base de datos...")

    # Verificar que estamos en el directorio correcto
    if not (backend_dir / "src" / "database" / "migrations").exists():
        print("❌ Error: Directorio de migraciones no encontrado")
        return False

    # Ejecutar migraciones
    import subprocess

    migrations_dir = backend_dir / "src" / "database" / "migrations"
    cmd = ["alembic", "-c", str(migrations_dir / "alembic.ini"), "upgrade", "head"]

    print(f"📦 Ejecutando migraciones desde: {migrations_dir}")
    print(f"Comando: {' '.join(cmd)}")

    result = subprocess.run(cmd, cwd=str(migrations_dir))

    if result.returncode == 0:
        print("✅ Base de datos configurada exitosamente!")
        print("\n📋 Resumen:")
        print("- Migraciones aplicadas")
        print("- Datos iniciales insertados")
        print("- Usuario admin creado: admin@qrfarm.com / admin123")
        return True
    else:
        print("❌ Error al configurar la base de datos")
        return False

if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)