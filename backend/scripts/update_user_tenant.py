#!/usr/bin/env python
"""
Script para actualizar el tenant_id de un usuario existente.
Uso: python scripts/update_user_tenant.py <email> <tenant_id>
"""
import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, backend_dir)

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    # Buscar .env en el directorio raíz del proyecto (un nivel arriba de backend)
    project_root = Path(backend_dir).parent
    env_path = project_root / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Archivo .env cargado desde: {env_path}")
    else:
        # Intentar cargar desde el directorio actual
        load_dotenv()
        print("⚠️  Archivo .env no encontrado en la raíz del proyecto, intentando cargar desde directorio actual")
except ImportError:
    print("⚠️  python-dotenv no está instalado, intentando sin cargar .env")

from src.database.db import get_connection

def update_user_tenant(email: str, tenant_id: int):
    """Actualiza el tenant_id de un usuario y su persona asociada."""
    conn = get_connection()
    if not conn:
        print("❌ Error: No se pudo conectar a la base de datos")
        return False
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Verificar que el usuario existe (el email está en la tabla personas)
        cursor.execute("""
            SELECT u.id, u.id_persona, p.id as persona_id
            FROM usuarios u
            INNER JOIN personas p ON u.id_persona = p.id
            WHERE p.email = %s
        """, (email,))
        usuario = cursor.fetchone()
        
        if not usuario:
            print(f"❌ Error: Usuario con email '{email}' no encontrado")
            return False
        
        # Verificar que el tenant existe
        cursor.execute("SELECT id FROM tenants WHERE id = %s AND estado = 'activo'", (tenant_id,))
        tenant = cursor.fetchone()
        
        if not tenant:
            print(f"❌ Error: Tenant con ID {tenant_id} no existe o está inactivo")
            return False
        
        # Actualizar tenant_id en usuarios
        cursor.execute(
            "UPDATE usuarios SET tenant_id = %s WHERE id = %s",
            (tenant_id, usuario['id'])
        )
        
        # Actualizar tenant_id en personas
        if usuario['id_persona']:
            cursor.execute(
                "UPDATE personas SET tenant_id = %s WHERE id = %s",
                (tenant_id, usuario['id_persona'])
            )
        
        conn.commit()
        print(f"✅ Usuario '{email}' actualizado con tenant_id = {tenant_id}")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error al actualizar usuario: {e}")
        return False
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Uso: python scripts/update_user_tenant.py <email> <tenant_id>")
        print("\nEjemplo:")
        print("  python scripts/update_user_tenant.py violeta@gmail.com 1")
        sys.exit(1)
    
    email = sys.argv[1]
    try:
        tenant_id = int(sys.argv[2])
    except ValueError:
        print(f"❌ Error: tenant_id debe ser un número entero")
        sys.exit(1)
    
    success = update_user_tenant(email, tenant_id)
    sys.exit(0 if success else 1)

