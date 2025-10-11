from functools import wraps
from flask import request, jsonify, current_app
import jwt
from ..services.usuario_service import UsuarioService

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Buscar el token en los headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                token = auth_header
        
        if not token:
            return jsonify({
                'status': 'error',
                'message': 'Token es requerido'
            }), 401
        
        try:
            # Decodificar el token
            data = jwt.decode(
                token, 
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            
            # Obtener el usuario actual
            current_user = UsuarioService.obtener_usuario(data['user_id'])
            if not current_user:
                return jsonify({
                    'status': 'error',
                    'message': 'Token inválido o usuario no encontrado'
                }), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({
                'status': 'error',
                'message': 'Token expirado'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'status': 'error',
                'message': 'Token inválido'
            }), 401
        
        # Pasar el usuario actual a la función decorada
        return f(*args, **kwargs)
    
    return decorated