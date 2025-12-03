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


def _validar_usuario_autenticado():
    """Valida que haya un usuario autenticado."""
    if not hasattr(g, 'current_user') or not g.current_user:
        return None, jsonify({
            'status': 'error',
            'code': 'unauthorized',
            'message': 'No autorizado'
        }), 401
    return g.current_user, None, None

def _obtener_rol_usuario(usuario):
    """Obtiene el nombre del rol del usuario."""
    if not hasattr(usuario, 'rol') or not usuario.rol:
        return None
    if hasattr(usuario.rol, 'nombre_rol'):
        return usuario.rol.nombre_rol
    if hasattr(usuario.rol, 'rol'):
        return usuario.rol.rol
    return None

def _validar_permiso(rol_nombre, permission):
    """Valida si el rol tiene el permiso requerido.
    
    Returns:
        tuple: (tiene_permiso: bool, error_response: tuple | None)
        - Si tiene permiso: (True, None)
        - Si no tiene permiso: (False, (jsonify_response, status_code))
    """
    if rol_nombre == 'super_admin':
        return True, None
    
    # Mapear "admin" a "tenant_admin" para compatibilidad
    # El rol "admin" debe tener los mismos permisos que "tenant_admin"
    if rol_nombre == 'admin':
        rol_nombre = 'tenant_admin'
    
    roles_permitidos = PERMISOS.get(permission, [])
    if rol_nombre not in roles_permitidos:
        error_response = (jsonify({
            'status': 'error',
            'code': 'insufficient_permissions',
            'message': f'No tiene permiso para: {permission}'
        }), 403)
        return False, error_response
    return True, None

def permission_required(permission: str):
    """Decorator que valida permisos."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated(*args: Any, **kwargs: Any) -> Any:
            usuario, error_response, error_status = _validar_usuario_autenticado()
            if error_response:
                return error_response, error_status
            
            rol_nombre = _obtener_rol_usuario(usuario)
            if not rol_nombre:
                return jsonify({
                    'status': 'error',
                    'code': 'no_role',
                    'message': 'Usuario sin rol asignado'
                }), 403
            
            tiene_permiso, error_response = _validar_permiso(rol_nombre, permission)
            if not tiene_permiso:
                # error_response es una tupla (jsonify_response, status_code) cuando no hay permiso
                if error_response and isinstance(error_response, tuple):
                    return error_response[0], error_response[1]
                return error_response
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator

