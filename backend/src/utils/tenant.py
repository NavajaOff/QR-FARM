"""Utilidades para manejo de tenant en requests."""
from functools import wraps
from flask import g, jsonify, request
from typing import Optional, Callable, Any


def get_current_tenant_id(allow_query_param: bool = True) -> Optional[int]:
    """
    Obtiene el tenant_id del usuario actual.
    
    Args:
        allow_query_param: Si es True, permite obtener tenant_id desde query params
                          (útil para super admin que quiere filtrar por tenant específico)
    
    Returns:
        Optional[int]: El tenant_id o None si no se puede determinar
    """
    # Primero verificar si hay tenant_id en query params (para super admin)
    if allow_query_param:
        tenant_id_param = request.args.get('tenant_id')
        if tenant_id_param:
            try:
                tenant_id = int(tenant_id_param)
                # Validar que el usuario es super admin antes de permitir query param
                if hasattr(g, 'current_user') and g.current_user:
                    if hasattr(g.current_user, 'rol') and g.current_user.rol:
                        rol_nombre = None
                        if hasattr(g.current_user.rol, 'nombre_rol'):
                            rol_nombre = g.current_user.rol.nombre_rol
                        elif hasattr(g.current_user.rol, 'rol'):
                            rol_nombre = g.current_user.rol.rol
                        
                        if rol_nombre == 'super_admin':
                            return tenant_id
            except (ValueError, TypeError):
                # Si tenant_id no es un número válido, continuar con el flujo normal
                pass
    
    if not hasattr(g, 'current_user') or not g.current_user:
        return None
    
    # Super admin no tiene tenant_id por defecto (pero puede usar query param)
    if hasattr(g.current_user, 'rol') and g.current_user.rol:
        if hasattr(g.current_user.rol, 'nombre_rol'):
            if g.current_user.rol.nombre_rol == 'super_admin':
                return None
    
    # Obtener tenant_id del usuario
    if hasattr(g.current_user, 'tenant_id'):
        return g.current_user.tenant_id
    
    # Intentar obtener de g.tenant_id
    if hasattr(g, 'tenant_id'):
        return g.tenant_id
    
    return None


def tenant_required(f: Callable) -> Callable:
    """
    Decorator que requiere tenant válido.
    
    Para super_admin: requiere que se pase tenant_id como query param explícitamente.
    Para otros usuarios: usa el tenant_id del usuario.
    """
    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        tenant_id = get_current_tenant_id()
        
        # Verificar si es super_admin
        is_super_admin = False
        if hasattr(g, 'current_user') and g.current_user:
            if hasattr(g.current_user, 'rol') and g.current_user.rol:
                rol_nombre = None
                if hasattr(g.current_user.rol, 'nombre_rol'):
                    rol_nombre = g.current_user.rol.nombre_rol
                elif hasattr(g.current_user.rol, 'rol'):
                    rol_nombre = g.current_user.rol.rol
                
                if rol_nombre == 'super_admin':
                    is_super_admin = True
        
        # Si es super admin y no hay tenant_id, requiere que se pase explícitamente
        if tenant_id is None:
            if is_super_admin:
                # Verificar si hay tenant_id en query params
                tenant_id_param = request.args.get('tenant_id')
                if not tenant_id_param:
                    return jsonify({
                        'status': 'error',
                        'code': 'tenant_required_for_super_admin',
                        'message': 'El super administrador debe seleccionar un tenant explícitamente para acceder a los datos. Proporcione tenant_id como query parameter.'
                    }), 403
                else:
                    # Si hay tenant_id en query params pero no se validó antes, hay un error
                    return jsonify({
                        'status': 'error',
                        'code': 'invalid_tenant_id',
                        'message': 'El tenant_id proporcionado no es válido o no existe'
                    }), 400
            else:
                # Usuario normal sin tenant_id
                return jsonify({
                    'status': 'error',
                    'code': 'tenant_required',
                    'message': 'Tenant requerido para esta operación'
                }), 403
        
        return f(*args, **kwargs)
    
    return decorated


def super_admin_required(f: Callable) -> Callable:
    """Decorator que requiere rol super_admin."""
    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        if not hasattr(g, 'current_user') or not g.current_user:
            return jsonify({
                'status': 'error',
                'code': 'unauthorized',
                'message': 'No autorizado'
            }), 401
        
        if not hasattr(g.current_user, 'rol') or not g.current_user.rol:
            return jsonify({
                'status': 'error',
                'code': 'insufficient_permissions',
                'message': 'Permisos insuficientes'
            }), 403
        
        rol_nombre = None
        if hasattr(g.current_user.rol, 'nombre_rol'):
            rol_nombre = g.current_user.rol.nombre_rol
        elif hasattr(g.current_user.rol, 'rol'):
            rol_nombre = g.current_user.rol.rol
        
        if rol_nombre != 'super_admin':
            return jsonify({
                'status': 'error',
                'code': 'insufficient_permissions',
                'message': 'Se requiere rol super_admin'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated

