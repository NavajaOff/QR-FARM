"""Utilidades para manejo de tenant en requests."""
from functools import wraps
from flask import g, jsonify
from typing import Optional, Callable, Any


def get_current_tenant_id() -> Optional[int]:
    """Obtiene el tenant_id del usuario actual."""
    if not hasattr(g, 'current_user') or not g.current_user:
        return None
    
    # Super admin no tiene tenant_id
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
    """Decorator que requiere tenant válido (excepto super_admin)."""
    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        tenant_id = get_current_tenant_id()
        
        # Super admin puede acceder sin tenant
        if tenant_id is None:
            # Verificar si es super_admin
            if hasattr(g, 'current_user') and g.current_user:
                if hasattr(g.current_user, 'rol') and g.current_user.rol:
                    if hasattr(g.current_user.rol, 'nombre_rol'):
                        if g.current_user.rol.nombre_rol == 'super_admin':
                            return f(*args, **kwargs)
            
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

