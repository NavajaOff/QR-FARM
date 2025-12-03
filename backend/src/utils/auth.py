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


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        print(f"[AUTH] 🔐 token_required ejecutándose para: {request.path} ({request.method})")
        auth_header = request.headers.get('Authorization', '').strip()
        print(f"[AUTH] Header Authorization recibido: '{auth_header[:50] if auth_header else 'VACÍO'}...'")

        if not auth_header:
            return _unauthorized('missing_authorization_header', 'Autorización requerida: encabezado Authorization ausente')

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return _unauthorized('invalid_authorization_format', 'Formato del encabezado Authorization inválido. Use "Bearer <token>"')

        token = parts[1]
        print(f"[AUTH] Token extraído: {token[:20]}... (longitud {len(token)})")

        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            print(f"[AUTH] Payload decodificado: {payload}")
        except jwt.ExpiredSignatureError:
            return _unauthorized('token_expired', 'Token expirado')
        except jwt.InvalidTokenError:
            return _unauthorized('invalid_token', 'Token inválido')

        user_id = payload.get('user_id')
        if user_id is None:
            return _unauthorized('token_missing_user_id', 'Token inválido: no contiene user_id')

        # Obtener tenant_id directamente del token (más eficiente que consultar BD)
        tenant_id = payload.get('tenant_id')
        print(f"[AUTH] tenant_id obtenido del token JWT: {tenant_id}")

        # Obtener usuario SIN filtrar por tenant (necesario para autenticación)
        current_user = UsuarioService.obtener_usuario(user_id, incluir_inactivos=True, tenant_id_override=None)

        estado_obj = getattr(current_user, 'estado', None) if current_user else None
        estado_valor = None
        if estado_obj is not None:
            estado_valor = getattr(estado_obj, 'value', estado_obj)

        print(f"[AUTH] Usuario actual: id={getattr(current_user, 'id', None)}, estado={estado_valor}")

        if not current_user:
            print(f"[AUTH] ERROR: Usuario con id={user_id} no encontrado")
            return _unauthorized('user_not_found', 'Token inválido o usuario no encontrado')

        if estado_valor != 'activo':
            print(f"[AUTH] ERROR: Usuario con id={user_id} está inactivo (estado={estado_valor})")
            return _unauthorized('user_inactive', 'Usuario inactivo o sin autorización')

        # Asignar tenant_id al current_user desde el token
        # IMPORTANTE: tenant_id está en personas (p.tenant_id), NO en usuarios (u.tenant_id)
        # Si el token no tiene tenant_id, intentar obtenerlo desde la BD desde personas (para tokens antiguos)
        if tenant_id is None:
            # PRIORIDAD 1: Desde el objeto usuario (ya cargado desde BD)
            if current_user and hasattr(current_user, 'tenant_id') and current_user.tenant_id is not None:
                tenant_id = current_user.tenant_id
                print(f"[AUTH] tenant_id obtenido del objeto usuario: {tenant_id}")
            # PRIORIDAD 2: Desde personas en la BD (para tokens antiguos)
            elif current_user and hasattr(current_user, 'id_persona'):
                try:
                    from ..database.db import get_connection
                    conn = get_connection()
                    if conn:
                        cursor = conn.cursor(dictionary=True)
                        # IMPORTANTE: tenant_id está en personas, no en usuarios
                        cursor.execute("SELECT tenant_id FROM personas WHERE id = %s", (current_user.id_persona,))
                        result = cursor.fetchone()
                        if result and result.get('tenant_id') is not None:
                            tenant_id = result['tenant_id']
                            print(f"[AUTH] tenant_id obtenido desde personas (token antiguo): {tenant_id}")
                        else:
                            print(f"[AUTH] ADVERTENCIA: No se encontró tenant_id en personas para persona_id={current_user.id_persona}")
                        cursor.close()
                        conn.close()
                except Exception as e:
                    print(f"[AUTH] Error obteniendo tenant_id desde personas: {e}")
        
        # Asegurar que current_user tiene tenant_id asignado
        if tenant_id is not None:
            current_user.tenant_id = tenant_id
            # Agregar tenant_id al payload para mantener consistencia
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