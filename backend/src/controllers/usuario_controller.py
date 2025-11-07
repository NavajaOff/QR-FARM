# Controlador Usuario
from datetime import datetime, timedelta
import jwt
from flask import jsonify, request, current_app, g
from ..models.usuario import Usuario, EstadoUsuario
from ..services.usuario_service import UsuarioService
try:
    try:
        from ...app import emit_update
    except ImportError:
        def emit_update(event, data):
            print(f"WebSocket no disponible, evento omitido: {event}")
except ImportError:
    def emit_update(event, data):
        print(f"WebSocket no disponible, evento omitido: {event}")

class UsuarioController:
    @staticmethod
    def registrar_usuario():
        try:
            data = request.get_json()

            if not data:
                return jsonify({
                    'status': 'error',
                    'message': 'No se recibieron datos JSON válidos'
                }), 400

            required_fields = ['primer_nombre', 'primer_apellido', 'email', 'password']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({
                        'status': 'error',
                        'message': f'El campo {field} es requerido'
                    }), 400

            # Validar formato de email básico
            import re
            email = data.get('email', '').strip()
            if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
                return jsonify({
                    'status': 'error',
                    'message': 'El formato del email no es válido'
                }), 400

            # Validar longitud de contraseña
            password = data.get('password', '')
            if len(password) < 6:
                return jsonify({
                    'status': 'error',
                    'message': 'La contraseña debe tener al menos 6 caracteres'
                }), 400

            # Verificar si el email ya existe
            if UsuarioService.buscar_por_email(email):
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
            print(f"ERROR inesperado en registro: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'status': 'error',
                'message': f'Error interno del servidor: {str(e)}'
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
                # Generar token JWT con información del rol
                token = jwt.encode({
                    'user_id': usuario.id,
                    'email': usuario.persona.email if usuario.persona else email,
                    'role': usuario.rol.rol if usuario.rol else 'usuario',
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
            print(f"ERROR en login: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

    @staticmethod
    def obtener_todos_usuarios():
        try:
            usuarios = UsuarioService.obtener_todos_usuarios(incluir_inactivos=True)
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

            current_user = getattr(g, 'current_user', None)
            print(f"[USUARIO] Petición cambio estado realizada por user_id={getattr(current_user, 'id', None)}")

            if nuevo_estado not in ['activo', 'inactivo']:
                return jsonify({
                    'status': 'error',
                    'message': 'Estado inválido. Debe ser "activo" o "inactivo"'
                }), 400

            # Verificar que el usuario existe
            usuario_existente = UsuarioService.obtener_usuario(id, incluir_inactivos=True)
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
            usuario_existente = UsuarioService.obtener_usuario(id, incluir_inactivos=True)
            if not usuario_existente:
                return jsonify({
                    'status': 'error',
                    'message': 'Usuario no encontrado'
                }), 404

            # Validar campos requeridos
            required_fields = ['primer_nombre', 'primer_apellido', 'email']
            for field in required_fields:
                if field in data and not data[field]:
                    return jsonify({
                        'status': 'error',
                        'message': f'El campo {field} es requerido'
                    }), 400

            # Validar formato de email si se proporciona
            if 'email' in data:
                import re
                email = data['email'].strip()
                if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
                    return jsonify({
                        'status': 'error',
                        'message': 'El formato del email no es válido'
                    }), 400

                # Verificar que el email no exista para otro usuario
                if email != usuario_existente.persona.email:
                    if UsuarioService.buscar_por_email(email):
                        return jsonify({
                            'status': 'error',
                            'message': 'El email ya está registrado'
                        }), 400

            # Validar contraseña si se proporciona
            if 'password' in data:
                password = data['password']
                if len(password) < 6:
                    return jsonify({
                        'status': 'error',
                        'message': 'La contraseña debe tener al menos 6 caracteres'
                    }), 400

            # Actualizar datos de la persona
            if 'primer_nombre' in data:
                usuario_existente.persona.primer_nombre = data['primer_nombre']
            if 'segundo_nombre' in data:
                usuario_existente.persona.segundo_nombre = data['segundo_nombre']
            if 'primer_apellido' in data:
                usuario_existente.persona.primer_apellido = data['primer_apellido']
            if 'segundo_apellido' in data:
                usuario_existente.persona.segundo_apellido = data['segundo_apellido']
            if 'email' in data:
                usuario_existente.persona.email = data['email']
            if 'telefono' in data:
                usuario_existente.persona.telefono = data['telefono']

            # Actualizar datos del usuario
            if 'password' in data:
                usuario_existente.set_password(data['password'])
            if 'estado' in data:
                usuario_existente.estado = EstadoUsuario(data['estado'])
            if 'id_rol' in data:
                usuario_existente.id_rol = data['id_rol']
                # También actualizar el rol en la persona si existe
                if usuario_existente.persona:
                    usuario_existente.persona.id_rol = data['id_rol']

            # Intentar actualizar en la base de datos
            if UsuarioService.actualizar_usuario_completo(id, usuario_existente):
                # Emitir actualización en tiempo real para usuario actualizado
                try:
                    emit_update('usuario_updated', {
                        'id': id,
                        'data': usuario_existente.to_dict()
                    })
                except NameError:
                    print("WebSocket no disponible, omitiendo emisión")
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
                # Emitir actualización en tiempo real para usuario eliminado
                try:
                    emit_update('usuario_deleted', {
                        'id': id
                    })
                except NameError:
                    print("WebSocket no disponible, omitiendo emisión")
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
