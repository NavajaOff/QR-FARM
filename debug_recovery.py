#!/usr/bin/env python3
"""Debug script for password recovery."""
import os
import sys
sys.path.append('backend')

from src.services.recovery_service import RecoveryService
from src.services.usuario_service import UsuarioService

# Simular variables de entorno
os.environ['ROOT_SUPER_ADMIN_EMAIL'] = 'superadmin@test.com'

def debug_recovery():
    """Debug password recovery flow."""
    # Cambia por el email real del admin que está probando
    admin_email = 'admin@qrfarm.com'  # Ajusta según tu setup

    try:
        usuario = UsuarioService.buscar_por_email(admin_email)
        if usuario:
            print(f'Usuario encontrado: {usuario.persona.email if usuario.persona else "sin persona"}')
            print(f'Rol: {usuario.rol.nombre_rol if usuario.rol else "sin rol"}')
            print(f'Tenant ID: {usuario.tenant_id}')

            rol_nombre = (usuario.rol.nombre_rol if usuario.rol else '').lower() if usuario.rol else ''
            tipo = 'admin' if rol_nombre in RecoveryService.ADMIN_ROLES else 'usuario'
            print(f'Tipo determinado: {tipo}')

            if tipo == 'admin':
                destinatario = os.getenv('ROOT_SUPER_ADMIN_EMAIL')
                print(f'Destinatario para admin: {destinatario}')
            else:
                print('Tipo usuario - buscaría admin del tenant')

            # Probar el flujo completo
            print('\nProbando request_password_recovery...')
            result = RecoveryService.request_password_recovery(admin_email)
            print(f'Resultado: {result}')

        else:
            print('Usuario no encontrado')
            print('Usuarios disponibles:')
            # Mostrar algunos usuarios para debug
            try:
                conn = UsuarioService._obtener_conexion()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT u.id, p.email, r.rol
                    FROM usuarios u
                    JOIN personas p ON u.id_persona = p.id
                    LEFT JOIN roles r ON u.id_rol = r.id
                    WHERE u.estado = 'activo'
                    LIMIT 5
                """)
                rows = cursor.fetchall()
                for row in rows:
                    print(f"  - {row['email']}: {row['rol']}")
                cursor.close()
                conn.close()
            except Exception as e:
                print(f'Error listando usuarios: {e}')

    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_recovery()

