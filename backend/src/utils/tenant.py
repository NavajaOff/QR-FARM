"""Utilidades para manejo de tenant en requests."""
from functools import wraps
from flask import g, jsonify, request
from typing import Optional, Callable, Any


def _obtener_rol_nombre(usuario):
    """Obtiene el nombre del rol del usuario."""
    if not hasattr(usuario, 'rol') or not usuario.rol:
        return None
    if hasattr(usuario.rol, 'nombre_rol'):
        return usuario.rol.nombre_rol
    if hasattr(usuario.rol, 'rol'):
        return usuario.rol.rol
    return None

def _obtener_tenant_desde_query_param():
    """Obtiene tenant_id desde query params si el usuario es super admin."""
    tenant_id_param = request.args.get('tenant_id')
    if not tenant_id_param:
        return None
    try:
        tenant_id = int(tenant_id_param)
        if hasattr(g, 'current_user') and g.current_user:
            rol_nombre = _obtener_rol_nombre(g.current_user)
            if rol_nombre == 'super_admin':
                return tenant_id
    except (ValueError, TypeError):
        pass
    return None

def _obtener_tenant_del_usuario():
    """Obtiene tenant_id del usuario actual."""
    if not hasattr(g, 'current_user') or not g.current_user:
        return None
    rol_nombre = _obtener_rol_nombre(g.current_user)
    if rol_nombre == 'super_admin':
        return None
    if hasattr(g.current_user, 'tenant_id'):
        return g.current_user.tenant_id
    return None

def get_current_tenant_id(allow_query_param: bool = True, require_tenant: bool = False) -> Optional[int]:
    """
    Obtiene el tenant_id del usuario actual.
    
    Args:
        allow_query_param: Si es True, permite obtener tenant_id desde query params
                          (útil para super admin que quiere filtrar por tenant específico)
        require_tenant: Si es True, requiere que el super admin tenga un tenant seleccionado.
                       Si es False, permite que el super admin vea todos los datos (None).
    
    Returns:
        Optional[int]: El tenant_id, None si es super admin sin tenant (ver todos),
                      o None si no se puede determinar
    
    Nota:
        - Para super_admin: Si no hay tenant_id en query params, retorna None (ver todos)
        - Para usuarios normales: Siempre retorna su tenant_id asignado
    """
    # Verificar si es super admin
    is_super_admin = _es_super_admin_usuario()
    
    if is_super_admin:
        # Super admin puede tener tenant_id desde query params o None (ver todos)
        if allow_query_param:
            tenant_id = _obtener_tenant_desde_query_param()
            # Si hay tenant_id en query params, usarlo
            if tenant_id is not None:
                return tenant_id
            # Si no hay tenant_id y require_tenant es False, retornar None (ver todos)
            if not require_tenant:
                return None
        # Si require_tenant es True y no hay tenant_id, retornar None (se validará en el decorator)
        return None
    
    # Para usuarios normales, obtener su tenant_id
    tenant_id = _obtener_tenant_del_usuario()
    if tenant_id is not None:
        return tenant_id
    
    if hasattr(g, 'tenant_id'):
        return g.tenant_id
    
    return None


def _es_super_admin_usuario():
    """Verifica si el usuario actual es super admin."""
    if not hasattr(g, 'current_user') or not g.current_user:
        return False
    rol_nombre = _obtener_rol_nombre(g.current_user)
    return rol_nombre == 'super_admin'

def _validar_tenant_super_admin():
    """Valida tenant_id para super admin."""
    tenant_id_param = request.args.get('tenant_id')
    if not tenant_id_param:
        return jsonify({
            'status': 'error',
            'code': 'tenant_required_for_super_admin',
            'message': 'El super administrador debe seleccionar un tenant explícitamente para acceder a los datos. Proporcione tenant_id como query parameter.'
        }), 403
    return jsonify({
        'status': 'error',
        'code': 'invalid_tenant_id',
        'message': 'El tenant_id proporcionado no es válido o no existe'
    }), 400

def _validar_tenant_usuario_normal():
    """Valida tenant_id para usuario normal."""
    return jsonify({
        'status': 'error',
        'code': 'tenant_required',
        'message': 'Tenant requerido para esta operación'
    }), 403

def tenant_required(f: Callable) -> Callable:
    """
    Decorator que requiere tenant válido.
    
    Para super_admin: SIEMPRE permite acceso (con o sin tenant).
    Para otros usuarios: requiere tenant_id del usuario.
    
    Nota: El super admin puede trabajar sin tenant (ver todos) o con tenant (filtrar).
    """
    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        is_super_admin = _es_super_admin_usuario()
        
        # Super admin SIEMPRE puede acceder, con o sin tenant
        if is_super_admin:
            return f(*args, **kwargs)
        
        # Usuarios normales deben tener tenant_id
        tenant_id = get_current_tenant_id(require_tenant=True)
        if tenant_id is not None:
            return f(*args, **kwargs)
        
        return _validar_tenant_usuario_normal()
    
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

