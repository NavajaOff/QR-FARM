# Controlador Usuario
from datetime import datetime, timedelta
import jwt
from flask import jsonify, request, current_app
from ..models.usuario import Usuario
from ..services.usuario_service import UsuarioService

class UsuarioController:
    @staticmethod
    def registrar_usuario():
        try:
            data = request.get_json()
            
            # Verificar si el email ya existe
            if UsuarioService.buscar_por_email(data.get('email')):
                return jsonify({
                    'status': 'error',
                    'message': 'El email ya está registrado'
                }), 400
            
            # Verificar si el documento ya existe
            if UsuarioService.buscar_por_documento(
                data.get('tipo_documento'), 
                data.get('numero_documento')
            ):
                return jsonify({
                    'status': 'error',
                    'message': 'El número de documento ya está registrado'
                }), 400
            
            # Crear el usuario
            usuario = Usuario.from_dict(data)
            if 'password' in data:
                usuario.set_password(data['password'])
            
            nuevo_usuario = UsuarioService.crear_usuario(usuario)
            
            if nuevo_usuario:
                return jsonify({
                    'status': 'success',
                    'message': 'Usuario registrado exitosamente',
                    'data': nuevo_usuario.to_dict()
                }), 201
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Error al registrar el usuario'
                }), 400
                
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @staticmethod
    def login():
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            
            if not email or not password:
                return jsonify({
                    'status': 'error',
                    'message': 'Email y contraseña son requeridos'
                }), 400
            
            usuario = UsuarioService.autenticar_usuario(email, password)
            
            if usuario:
                # Generar token JWT
                token = jwt.encode({
                    'user_id': usuario.id,
                    'email': usuario.email,
                    'exp': datetime.utcnow() + timedelta(hours=24)
                }, current_app.config['SECRET_KEY'], algorithm='HS256')
                
                return jsonify({
                    'status': 'success',
                    'message': 'Login exitoso',
                    'token': token,
                    'user': usuario.to_dict()
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Credenciales inválidas'
                }), 401
                
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @staticmethod
    def obtener_usuario(id):
        try:
            usuario = UsuarioService.obtener_usuario(id)
            
            if usuario:
                return jsonify({
                    'status': 'success',
                    'data': usuario.to_dict()
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Usuario no encontrado'
                }), 404
                
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @staticmethod
    def obtener_todos_usuarios():
        try:
            usuarios = UsuarioService.obtener_todos_usuarios()
            return jsonify({
                'status': 'success',
                'data': [usuario.to_dict() for usuario in usuarios]
            }), 200
                
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @staticmethod
    def actualizar_usuario(id):
        try:
            data = request.get_json()
            
            # Verificar si el usuario existe
            usuario_existente = UsuarioService.obtener_usuario(id)
            if not usuario_existente:
                return jsonify({
                    'status': 'error',
                    'message': 'Usuario no encontrado'
                }), 404
            
            # Si se está actualizando el email, verificar que no exista
            if 'email' in data and data['email'] != usuario_existente.email:
                if UsuarioService.buscar_por_email(data['email']):
                    return jsonify({
                        'status': 'error',
                        'message': 'El email ya está registrado'
                    }), 400
            
            # Si se está actualizando el documento, verificar que no exista
            if ('tipo_documento' in data and 'numero_documento' in data and 
                (data['tipo_documento'] != usuario_existente.tipo_documento or 
                 data['numero_documento'] != usuario_existente.numero_documento)):
                if UsuarioService.buscar_por_documento(
                    data['tipo_documento'], 
                    data['numero_documento']
                ):
                    return jsonify({
                        'status': 'error',
                        'message': 'El número de documento ya está registrado'
                    }), 400
            
            # Actualizar la contraseña si se proporciona una nueva
            if 'password' in data:
                usuario_existente.set_password(data['password'])
                data.pop('password')  # Remover password del dict para no sobreescribir el hash
            
            # Actualizar los demás campos
            for key, value in data.items():
                setattr(usuario_existente, key, value)
            
            # Intentar actualizar en la base de datos
            if UsuarioService.actualizar_usuario(id, usuario_existente):
                return jsonify({
                    'status': 'success',
                    'message': 'Usuario actualizado exitosamente',
                    'data': usuario_existente.to_dict()
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Error al actualizar el usuario'
                }), 400
                
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @staticmethod
    def eliminar_usuario(id):
        try:
            if UsuarioService.eliminar_usuario(id):
                return jsonify({
                    'status': 'success',
                    'message': 'Usuario eliminado exitosamente'
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Usuario no encontrado'
                }), 404
                
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
