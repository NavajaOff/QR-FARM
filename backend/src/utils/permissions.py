"""Sistema de permisos para validación de acceso."""
from functools import wraps
from flask import g, jsonify
from typing import Callable, Any, List


PERMISOS = {
    'ver_ganado': ['super_admin', 'tenant_admin', 'usuario'],
    'crear_ganado': ['super_admin', 'tenant_admin'],
    'editar_ganado': ['super_admin', 'tenant_admin'],
    'eliminar_ganado': ['super_admin', 'tenant_admin'],
    'ver_potreros': ['super_admin', 'tenant_admin', 'usuario'],
    'crear_potreros': ['super_admin', 'tenant_admin'],
    'editar_potreros': ['super_admin', 'tenant_admin'],
    'eliminar_potreros': ['super_admin', 'tenant_admin'],
    'ver_vacunaciones': ['super_admin', 'tenant_admin', 'usuario'],
    'crear_vacunaciones': ['super_admin', 'tenant_admin'],
    'editar_vacunaciones': ['super_admin', 'tenant_admin'],
    'eliminar_vacunaciones': ['super_admin', 'tenant_admin'],
    'gestionar_usuarios': ['super_admin', 'tenant_admin'],
    'gestionar_tenants': ['super_admin']
}


def permission_required(permission: str):
    """Decorator que valida permisos."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args: Any, **kwargs: Any) -> Any:
            if not hasattr(g, 'current_user') or not g.current_user:
                return jsonify({
                    'status': 'error',
                    'code': 'unauthorized',
                    'message': 'No autorizado'
                }), 401
            
            # Obtener rol del usuario
            rol_nombre = None
            if hasattr(g.current_user, 'rol') and g.current_user.rol:
                if hasattr(g.current_user.rol, 'nombre_rol'):
                    rol_nombre = g.current_user.rol.nombre_rol
                elif hasattr(g.current_user.rol, 'rol'):
                    rol_nombre = g.current_user.rol.rol
            
            if not rol_nombre:
                return jsonify({
                    'status': 'error',
                    'code': 'no_role',
                    'message': 'Usuario sin rol asignado'
                }), 403
            
            # Super admin tiene todos los permisos
            if rol_nombre == 'super_admin':
                return f(*args, **kwargs)
            
            # Verificar permiso
            roles_permitidos = PERMISOS.get(permission, [])
            if rol_nombre not in roles_permitidos:
                return jsonify({
                    'status': 'error',
                    'code': 'insufficient_permissions',
                    'message': f'No tiene permiso para: {permission}'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator

