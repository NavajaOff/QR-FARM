# Helper para auditoría
from typing import Optional, Tuple
from flask import g
from ..models.historial_cambio import TipoEntidad, TipoAccion


def obtener_usuario_y_tenant_actual() -> Tuple[Optional[int], Optional[int]]:
    """
    Obtiene el usuario_id y tenant_id del contexto actual.
    
    Returns:
        Tuple (usuario_id, tenant_id) o (None, None) si no hay contexto
    """
    usuario_id = None
    tenant_id = None
    
    try:
        current_user = getattr(g, 'current_user', None)
        if current_user and hasattr(current_user, 'id'):
            usuario_id = current_user.id
        
        # Intentar obtener tenant_id desde varias fuentes
        if hasattr(g, 'tenant_id') and g.tenant_id is not None:
            tenant_id = g.tenant_id
        elif current_user and hasattr(current_user, 'tenant_id') and current_user.tenant_id is not None:
            tenant_id = current_user.tenant_id
        elif hasattr(g, 'jwt_payload') and g.jwt_payload:
            tenant_id = g.jwt_payload.get('tenant_id')
    
    except Exception:
        pass
    
    return usuario_id, tenant_id
