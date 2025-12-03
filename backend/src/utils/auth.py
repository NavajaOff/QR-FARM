from functools import wraps
from flask import request, jsonify, current_app, g
import jwt
from ..services.usuario_service import UsuarioService


def _unauthorized(code: str, message: str):
    print(f"[AUTH] 401 - code={code} message={message}")
    return jsonify({
        'status': 'error',
        'code': code,
        'message': message
    }), 401


def _validar_header_autorizacion(auth_header):
    """Valida el header de autorización."""
    if not auth_header:
        return None, _unauthorized('missing_authorization_header', 'Autorización requerida: encabezado Authorization ausente')
    
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None, _unauthorized('invalid_authorization_format', 'Formato del encabezado Authorization inválido. Use "Bearer <token>"')
    
    return parts[1], None


def _decodificar_token(token):
    """Decodifica el token JWT."""
    try:
        payload = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
        print(f"[AUTH] Payload decodificado: {payload}")
        return payload, None
    except jwt.ExpiredSignatureError:
        return None, _unauthorized('token_expired', 'Token expirado')
    except jwt.InvalidTokenError:
        return None, _unauthorized('invalid_token', 'Token inválido')


def _validar_usuario_activo(current_user, user_id):
    """Valida que el usuario exista y esté activo."""
    if not current_user:
        print(f"[AUTH] ERROR: Usuario con id={user_id} no encontrado")
        return _unauthorized('user_not_found', 'Token inválido o usuario no encontrado')
    
    estado_obj = getattr(current_user, 'estado', None)
    estado_valor = getattr(estado_obj, 'value', estado_obj) if estado_obj is not None else None
    
    if estado_valor != 'activo':
        print(f"[AUTH] ERROR: Usuario con id={user_id} está inactivo (estado={estado_valor})")
        return _unauthorized('user_inactive', 'Usuario inactivo o sin autorización')
    
    return None


def _obtener_tenant_id_desde_bd(current_user):
    """Obtiene tenant_id desde la base de datos para tokens antiguos."""
    try:
        from ..database.db import get_connection
        conn = get_connection()
        if not conn:
            return None
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT tenant_id FROM personas WHERE id = %s", (current_user.id_persona,))
        result = cursor.fetchone()
        tenant_id = None
        if result and result.get('tenant_id') is not None:
            tenant_id = result['tenant_id']
            print(f"[AUTH] tenant_id obtenido desde personas (token antiguo): {tenant_id}")
        else:
            print(f"[AUTH] ADVERTENCIA: No se encontró tenant_id en personas para persona_id={current_user.id_persona}")
        cursor.close()
        conn.close()
        return tenant_id
    except Exception as e:
        print(f"[AUTH] Error obteniendo tenant_id desde personas: {e}")
        return None


def _obtener_tenant_id_completo(payload, current_user):
    """Obtiene tenant_id desde múltiples fuentes."""
    tenant_id = payload.get('tenant_id')
    if tenant_id is not None:
        return tenant_id
    
    if current_user and hasattr(current_user, 'tenant_id') and current_user.tenant_id is not None:
        return current_user.tenant_id
    
    if current_user and hasattr(current_user, 'id_persona'):
        return _obtener_tenant_id_desde_bd(current_user)
    
    return None


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        print(f"[AUTH] 🔐 token_required ejecutándose para: {request.path} ({request.method})")
        auth_header = request.headers.get('Authorization', '').strip()
        print(f"[AUTH] Header Authorization recibido: '{auth_header[:50] if auth_header else 'VACÍO'}...'")

        token, error = _validar_header_autorizacion(auth_header)
        if error:
            return error

        print(f"[AUTH] Token extraído: {token[:20]}... (longitud {len(token)})")
        
        payload, error = _decodificar_token(token)
        if error:
            return error

        user_id = payload.get('user_id')
        if user_id is None:
            return _unauthorized('token_missing_user_id', 'Token inválido: no contiene user_id')

        current_user = UsuarioService.obtener_usuario(user_id, incluir_inactivos=True, tenant_id_override=None)
        print(f"[AUTH] Usuario actual: id={getattr(current_user, 'id', None)}, estado={getattr(getattr(current_user, 'estado', None), 'value', None) if current_user else None}")

        error = _validar_usuario_activo(current_user, user_id)
        if error:
            return error

        tenant_id = _obtener_tenant_id_completo(payload, current_user)
        print(f"[AUTH] tenant_id obtenido del token JWT: {tenant_id}")

        if tenant_id is not None:
            current_user.tenant_id = tenant_id
            payload['tenant_id'] = tenant_id
            print(f"[AUTH] tenant_id asignado a current_user: {tenant_id}")
        else:
            print(f"[AUTH] ADVERTENCIA: Usuario {current_user.id} no tiene tenant_id asignado")
        
        g.current_user = current_user
        g.jwt_payload = payload
        g.tenant_id = tenant_id
        
        print(f"[AUTH] Usuario autenticado: id={current_user.id}, role={payload.get('role')}, tenant_id={tenant_id} (desde personas)")
        print(f"[AUTH] DEBUG - g.tenant_id asignado: {g.tenant_id}, g.jwt_payload['tenant_id']: {g.jwt_payload.get('tenant_id')}")

        return f(*args, **kwargs)

    return decorated