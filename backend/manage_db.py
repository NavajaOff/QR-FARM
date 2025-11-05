#!/usr/bin/env python3
"""
Script para gestionar migraciones de base de datos
Uso: python manage_db.py <comando>

Comandos disponibles:
- init: Inicializar migraciones (solo primera vez)
- migrate: Crear nueva migración basada en cambios del modelo
- upgrade: Aplicar todas las migraciones pendientes
- downgrade: Revertir la última migración
- current: Mostrar migración actual
- history: Mostrar historial de migraciones
- stamp <revision>: Marcar una revisión específica como aplicada
"""

import sys
import os
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def run_alembic_command(command_args):
    """Ejecutar comando de Alembic"""
    import subprocess

    # Cambiar al directorio de migraciones
    migrations_dir = backend_dir / "src" / "database" / "migrations"

    # Construir comando
    cmd = ["alembic", "-c", str(migrations_dir / "alembic.ini")] + command_args

    print(f"Ejecutando: {' '.join(cmd)}")
    print(f"Directorio: {migrations_dir}")

    # Ejecutar comando
    result = subprocess.run(cmd, cwd=str(migrations_dir))

    return result.returncode

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "init":
        print("Inicializando migraciones...")
        run_alembic_command(["init", "src/database/migrations"])

    elif command == "migrate":
        message = sys.argv[2] if len(sys.argv) > 2 else "auto migration"
        print(f"Creando migración: {message}")
        run_alembic_command(["revision", "--autogenerate", "-m", message])

    elif command == "upgrade":
        print("Aplicando migraciones...")
        run_alembic_command(["upgrade", "head"])

    elif command == "downgrade":
        revision = sys.argv[2] if len(sys.argv) > 2 else "-1"
        print(f"Revirtiendo migración: {revision}")
        run_alembic_command(["downgrade", revision])

    elif command == "current":
        print("Migración actual:")
        run_alembic_command(["current"])

    elif command == "history":
        print("Historial de migraciones:")
        run_alembic_command(["history"])

    elif command == "stamp":
        if len(sys.argv) < 3:
            print("Error: Debe especificar la revisión para stamp")
            sys.exit(1)
        revision = sys.argv[2]
        print(f"Marcando revisión {revision} como aplicada...")
        run_alembic_command(["stamp", revision])

    else:
        print(f"Comando desconocido: {command}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()