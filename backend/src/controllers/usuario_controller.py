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

            # Validar campos requeridos
            required_fields = ['primer_nombre', 'primer_apellido', 'email', 'password']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({
                        'status': 'error',
                        'message': f'El campo {field} es requerido'
                    }), 400

            # Verificar si el email ya existe
            if UsuarioService.buscar_por_email(data.get('email')):
                return jsonify({
                    'status': 'error',
                    'message': 'El email ya está registrado'
                }), 400

            # Crear persona y usuario desde los datos de registro
            persona, usuario = Usuario.from_registration_data(data)

            # Crear el usuario en la base de datos
            nuevo_usuario, mensaje = UsuarioService.registrar_usuario(persona, usuario)

            if nuevo_usuario:
                return jsonify({
                    'status': 'success',
                    'message': mensaje,
                    'data': nuevo_usuario.to_dict()
                }), 201
            else:
                return jsonify({
                    'status': 'error',
                    'message': mensaje
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
                    'email': usuario.persona.email if usuario.persona else email,
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
    def cambiar_estado_usuario(id):
        try:
            data = request.get_json()
            nuevo_estado = data.get('estado')

            if nuevo_estado not in ['activo', 'inactivo']:
                return jsonify({
                    'status': 'error',
                    'message': 'Estado inválido. Debe ser "activo" o "inactivo"'
                }), 400

            # Verificar que el usuario existe
            usuario_existente = UsuarioService.obtener_usuario(id)
            if not usuario_existente:
                return jsonify({
                    'status': 'error',
                    'message': 'Usuario no encontrado'
                }), 404

            # Actualizar estado
            from ..models.usuario import EstadoUsuario
            usuario_existente.estado = EstadoUsuario(nuevo_estado)

            if UsuarioService.actualizar_usuario(id, usuario_existente):
                return jsonify({
                    'status': 'success',
                    'message': f'Usuario {"activado" if nuevo_estado == "activo" else "desactivado"} exitosamente'
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Error al actualizar el estado del usuario'
                }), 400

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
            if 'email' in data and data['email'] != usuario_existente.persona.email:
                if UsuarioService.buscar_por_email(data['email']):
                    return jsonify({
                        'status': 'error',
                        'message': 'El email ya está registrado'
                    }), 400

            # Actualizar la contraseña si se proporciona una nueva
            if 'password' in data:
                usuario_existente.set_password(data['password'])

            # Actualizar estado si se proporciona
            if 'estado' in data:
                usuario_existente.estado = EstadoUsuario(data['estado'])

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
