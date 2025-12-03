#!/usr/bin/env python3
"""
Script de diagnóstico para verificar el aislamiento multi-tenant.
Ejecuta este script para verificar qué usuarios tienen qué tenant_id.
"""
import sys
import os
from pathlib import Path

# Agregar el directorio raíz del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

from src.database.db import get_connection

def diagnosticar_tenant():
    """Diagnostica el estado del aislamiento multi-tenant."""
    conn = get_connection()
    if not conn:
        print("[ERROR] No se pudo conectar a la base de datos")
        return
    
    cursor = conn.cursor(dictionary=True)
    
    print("=" * 80)
    print("DIAGNÓSTICO DE AISLAMIENTO MULTI-TENANT")
    print("=" * 80)
    print()
    
    # 1. Verificar estructura de tablas
    print("1. ESTRUCTURA DE TABLAS:")
    print("-" * 80)
    try:
        cursor.execute("DESCRIBE personas")
        columnas_personas = cursor.fetchall()
        print("Columnas en tabla 'personas':")
        for col in columnas_personas:
            if 'tenant_id' in col['Field']:
                print(f"  [OK] {col['Field']} ({col['Type']}) - {col['Null']}")
            else:
                print(f"       {col['Field']} ({col['Type']})")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print()
    try:
        cursor.execute("DESCRIBE usuarios")
        columnas_usuarios = cursor.fetchall()
        print("Columnas en tabla 'usuarios':")
        for col in columnas_usuarios:
            if 'tenant_id' in col['Field']:
                print(f"  [WARN] {col['Field']} ({col['Type']}) - {col['Null']} (REDUNDANTE)")
            else:
                print(f"         {col['Field']} ({col['Type']})")
    except Exception as e:
        print(f"  [ERROR] Error: {e}")
    
    print()
    print("2. USUARIOS Y SUS TENANT_ID:")
    print("-" * 80)
    
    # 2. Listar todos los usuarios con su tenant_id desde personas
    sql = """
        SELECT 
            u.id as usuario_id,
            p.id as persona_id,
            p.primer_nombre,
            p.primer_apellido,
            p.email,
            r.rol,
            p.tenant_id as tenant_id_personas,
            u.tenant_id as tenant_id_usuarios
        FROM usuarios u
        INNER JOIN personas p ON u.id_persona = p.id
        LEFT JOIN roles r ON u.id_rol = r.id
        ORDER BY u.id
    """
    
    cursor.execute(sql)
    usuarios = cursor.fetchall()
    
    print(f"Total de usuarios: {len(usuarios)}")
    print()
    print(f"{'ID':<5} {'Nombre':<30} {'Email':<35} {'Rol':<15} {'Tenant (P)':<12} {'Tenant (U)':<12} {'Estado':<10}")
    print("-" * 120)
    
    for usuario in usuarios:
        tenant_p = usuario.get('tenant_id_personas', 'NULL')
        tenant_u = usuario.get('tenant_id_usuarios', 'NULL')
        
        # Verificar si hay inconsistencia
        estado = "[OK]"
        if tenant_p != tenant_u and tenant_u != 'NULL':
            estado = "[INCONSISTENTE]"
        elif tenant_p == 'NULL' and usuario.get('rol') != 'super_admin':
            estado = "[SIN TENANT]"
        
        print(f"{usuario['usuario_id']:<5} "
              f"{usuario['primer_nombre']} {usuario['primer_apellido']:<25} "
              f"{usuario['email']:<35} "
              f"{usuario.get('rol', 'N/A'):<15} "
              f"{str(tenant_p):<12} "
              f"{str(tenant_u):<12} "
              f"{estado:<10}")
    
    print()
    print("3. VERIFICACIÓN POR TENANT:")
    print("-" * 80)
    
    # Agrupar por tenant_id
    cursor.execute("""
        SELECT 
            p.tenant_id,
            COUNT(*) as cantidad_usuarios
        FROM personas p
        INNER JOIN usuarios u ON p.id = u.id_persona
        WHERE p.tenant_id IS NOT NULL
        GROUP BY p.tenant_id
        ORDER BY p.tenant_id
    """)
    
    tenants = cursor.fetchall()
    for tenant in tenants:
        tenant_id = tenant['tenant_id']
        cantidad = tenant['cantidad_usuarios']
        
        print(f"Tenant ID {tenant_id}: {cantidad} usuarios")
        
        # Listar usuarios de este tenant
        cursor.execute("""
            SELECT 
                u.id,
                p.primer_nombre,
                p.primer_apellido,
                p.email
            FROM usuarios u
            INNER JOIN personas p ON u.id_persona = p.id
            WHERE p.tenant_id = %s
            ORDER BY u.id
        """, (tenant_id,))
        
        usuarios_tenant = cursor.fetchall()
        for u in usuarios_tenant:
            print(f"  - {u['id']}: {u['primer_nombre']} {u['primer_apellido']} ({u['email']})")
        print()
    
    # Usuarios sin tenant
    cursor.execute("""
        SELECT COUNT(*) as cantidad
        FROM personas p
        INNER JOIN usuarios u ON p.id = u.id_persona
        WHERE p.tenant_id IS NULL
    """)
    sin_tenant = cursor.fetchone()
    if sin_tenant['cantidad'] > 0:
        print(f"[WARN] Usuarios sin tenant_id: {sin_tenant['cantidad']}")
        cursor.execute("""
            SELECT 
                u.id,
                p.primer_nombre,
                p.primer_apellido,
                p.email,
                r.rol
            FROM usuarios u
            INNER JOIN personas p ON u.id_persona = p.id
            LEFT JOIN roles r ON u.id_rol = r.id
            WHERE p.tenant_id IS NULL
        """)
        usuarios_sin_tenant = cursor.fetchall()
        for u in usuarios_sin_tenant:
            print(f"  - {u['id']}: {u['primer_nombre']} {u['primer_apellido']} ({u['email']}) - Rol: {u.get('rol', 'N/A')}")
    
    print()
    print("=" * 80)
    print("RECOMENDACIONES:")
    print("=" * 80)
    print("1. Si hay usuarios sin tenant_id, ejecuta: backend/scripts/fix_tenant_isolation.sql")
    print("2. Si hay inconsistencias entre personas.tenant_id y usuarios.tenant_id, sincroniza los datos")
    print("3. Cierra sesión y vuelve a iniciar sesión para obtener un nuevo token JWT con tenant_id")
    print("=" * 80)
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    diagnosticar_tenant()

