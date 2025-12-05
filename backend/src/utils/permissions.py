"""Sistema de permisos para validación de acceso."""
from functools import wraps
from flask import g, jsonify
from typing import Callable, Any, List


PERMISOS = {
    # Permisos de ganado
    'ver_ganado': ['tenant_admin', 'usuario'],  # NO super_admin
    'crear_ganado': ['tenant_admin'],  # Solo admin, NO super_admin ni usuario
    'editar_ganado': ['tenant_admin'],  # Solo admin, NO super_admin ni usuario
    'eliminar_ganado': ['tenant_admin'],  # Solo admin, NO super_admin ni usuario
    
    # Permisos de potreros
    'ver_potreros': ['tenant_admin', 'usuario'],  # NO super_admin
    'crear_potreros': ['tenant_admin'],  # Solo admin, NO super_admin ni usuario
    'editar_potreros': ['tenant_admin'],  # Solo admin, NO super_admin ni usuario
    'eliminar_potreros': ['tenant_admin'],  # Solo admin, NO super_admin ni usuario
    
    # Permisos de vacunaciones
    'ver_vacunaciones': ['tenant_admin', 'usuario'],  # NO super_admin
    'crear_vacunaciones': ['tenant_admin', 'usuario'],  # Admin y usuario pueden registrar
    'editar_vacunaciones': ['tenant_admin'],  # Solo admin puede editar
    'eliminar_vacunaciones': ['tenant_admin'],  # Solo admin puede eliminar
    
    # Permisos de usuarios
    'gestionar_usuarios': ['super_admin', 'tenant_admin'],  # Super admin y admin pueden gestionar usuarios
    'crear_usuarios': ['super_admin', 'tenant_admin'],  # Super admin crea admins, admin crea usuarios
    'editar_usuarios': ['super_admin', 'tenant_admin'],
    'eliminar_usuarios': ['super_admin', 'tenant_admin'],
    
    # Permisos de tenants (solo super_admin)
    'gestionar_tenants': ['super_admin'],
    'crear_tenants': ['super_admin'],
    'editar_tenants': ['super_admin'],
    'eliminar_tenants': ['super_admin'],
    
    # Permisos de QR scanner
    'escanear_qr': ['tenant_admin', 'usuario'],  # Admin y usuario pueden escanear, NO super_admin
    
    # Permisos de reportes
    'ver_reportes': ['tenant_admin'],  # Solo admin puede ver reportes, NO super_admin ni usuario
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
    # Super admin NO tiene acceso automático a todo
    # Solo tiene acceso a permisos explícitamente definidos para super_admin
    # Mapear "admin" a "tenant_admin" para compatibilidad
    rol_original = rol_nombre
    if rol_nombre == 'admin' or rol_nombre == 'administrador':
        rol_nombre = 'tenant_admin'
        print(f"[PERMISSIONS] Rol mapeado: '{rol_original}' -> '{rol_nombre}'")
    
    roles_permitidos = PERMISOS.get(permission, [])
    print(f"[PERMISSIONS] Permiso '{permission}' requiere roles: {roles_permitidos}, usuario tiene rol: '{rol_nombre}'")
    
    # Si el permiso no está definido, denegar acceso
    if not roles_permitidos:
        error_response = (jsonify({
            'status': 'error',
            'code': 'insufficient_permissions',
            'message': f'Permiso no definido: {permission}'
        }), 403)
        return False, error_response
    
    # Verificar si el rol está en los roles permitidos
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
            print(f"[PERMISSIONS] Validando permiso '{permission}' para usuario id={getattr(usuario, 'id', None)} con rol='{rol_nombre}'")
            
            if not rol_nombre:
                print(f"[PERMISSIONS] ERROR: Usuario sin rol asignado")
                return jsonify({
                    'status': 'error',
                    'code': 'no_role',
                    'message': 'Usuario sin rol asignado'
                }), 403
            
            tiene_permiso, error_response = _validar_permiso(rol_nombre, permission)
            print(f"[PERMISSIONS] Resultado validación: tiene_permiso={tiene_permiso}")
            
            if not tiene_permiso:
                # error_response es una tupla (jsonify_response, status_code) cuando no hay permiso
                if error_response and isinstance(error_response, tuple):
                    response_obj = error_response[0]
                    status_code = error_response[1]
                    # Manejar tanto objetos Response como diccionarios
                    if hasattr(response_obj, 'get_json'):
                        try:
                            response_data = response_obj.get_json()
                        except Exception:
                            response_data = str(response_obj)
                    elif isinstance(response_obj, dict):
                        response_data = response_obj
                    else:
                        response_data = str(response_obj)
                    print(f"[PERMISSIONS] DENEGADO: {status_code} - {response_data}")
                    return error_response[0], error_response[1]
                return error_response
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator

