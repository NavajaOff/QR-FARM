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
        auth_header = request.headers.get('Authorization', '').strip()
        print(f"[AUTH] Header Authorization recibido: '{auth_header}'")

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

        current_user = UsuarioService.obtener_usuario(user_id, incluir_inactivos=True)

        estado_obj = getattr(current_user, 'estado', None) if current_user else None
        estado_valor = None
        if estado_obj is not None:
            estado_valor = getattr(estado_obj, 'value', estado_obj)

        print(f"[AUTH] Usuario actual: id={getattr(current_user, 'id', None)}, estado={estado_valor}")

        if not current_user:
            return _unauthorized('user_not_found', 'Token inválido o usuario no encontrado')

        if estado_valor != 'activo':
            return _unauthorized('user_inactive', 'Usuario inactivo o sin autorización')

        g.current_user = current_user
        g.jwt_payload = payload

        return f(*args, **kwargs)

    return decorated