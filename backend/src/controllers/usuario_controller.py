"""Controlador Usuario."""
from datetime import datetime, timedelta
import re
import jwt
from flask import jsonify, request, current_app, g
from ..models.usuario import Usuario, EstadoUsuario
from ..services.usuario_service import UsuarioService

EMAIL_REGEX = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
EMAIL_INVALID_MSG = 'El formato del email no es válido'
EMAIL_REGISTERED_MSG = 'El email ya está registrado'
USER_NOT_FOUND_MSG = 'Usuario no encontrado'
try:
    try:
        from ...app import emit_update
    except ImportError:
        def emit_update(event):
            print(f"WebSocket no disponible, evento omitido: {event}")
except ImportError:
    def emit_update(event):
        print(f"WebSocket no disponible, evento omitido: {event}")

class UsuarioController:
    # Error message constants
    MSG_INVALID_EMAIL_FORMAT = 'El formato del email no es válido'
    MSG_USER_NOT_FOUND = 'Usuario no encontrado'
    MSG_EMAIL_ALREADY_REGISTERED = 'El email ya está registrado'
    MSG_PASSWORD_TOO_SHORT = 'La contraseña debe tener al menos 6 caracteres'
    MSG_NOT_AUTHENTICATED = 'No autenticado'
    MSG_FIELD_REQUIRED = 'El campo {field} es requerido'
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
                        'message': MSG_FIELD_REQUIRED.format(field=field)
                    }), 400

            # Validar formato de email básico
            email = data.get('email', '').strip()
            if not _validar_email(email):
                return jsonify({
                    'status': 'error',
                    'message': MSG_INVALID_EMAIL_FORMAT
                }), 400

            # Validar longitud de contraseña
            password = data.get('password', '')
            if len(password) < 6:
                return jsonify({
                    'status': 'error',
                    'message': MSG_PASSWORD_TOO_SHORT
                }), 400

            # Verificar si el email ya existe
            if UsuarioService.buscar_por_email(email):
                return jsonify({
                    'status': 'error',
                    'message': MSG_EMAIL_ALREADY_REGISTERED
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
                    'message': MSG_USER_NOT_FOUND
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
                    'message': MSG_USER_NOT_FOUND
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
    def obtener_perfil_actual():
        try:
            usuario = _obtener_usuario_actual()
            if not usuario:
                return jsonify({
                    'status': 'error',
                    'message': MSG_NOT_AUTHENTICATED
                }), 401

            persona = usuario.persona.to_dict() if usuario.persona else {}
            data = {
                'nombre_completo': persona.get('nombre_completo') or '',
                'email': persona.get('email') or '',
                'telefono': persona.get('telefono'),
                'fecha_creacion': persona.get('fecha_creacion')
            }

            return jsonify({
                'status': 'success',
                'data': data
            }), 200

        except Exception as e:
            return _respuesta_error(str(e), 500)

    @staticmethod
    def actualizar_perfil_actual():
        try:
            usuario = _obtener_usuario_actual()
            if not usuario:
                return jsonify({
                    'status': 'error',
                    'message': MSG_NOT_AUTHENTICATED
                }), 401

            data = request.get_json() or {}

            nombre_completo = (data.get('nombre_completo') or '').strip()
            email = (data.get('email') or '').strip()
            telefono = data.get('telefono')

            if not nombre_completo or not email:
                return jsonify({
                    'status': 'error',
                    'message': 'Nombre completo y email son obligatorios'
                }), 400

            import re
            if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
                return jsonify({
                    'status': 'error',
                    'message': MSG_INVALID_EMAIL_FORMAT
                }), 400

            partes = nombre_completo.split()
            primer_nombre = partes[0]
            primer_apellido = partes[-1] if len(partes) > 1 else (usuario.persona.primer_apellido if usuario.persona else '')
            segundo_nombre = ' '.join(partes[1:-1]) if len(partes) > 2 else (partes[1] if len(partes) == 2 else usuario.persona.segundo_nombre if usuario.persona else None)
            segundo_apellido = usuario.persona.segundo_apellido if usuario.persona else None

            persona = usuario.persona
            if persona:
                persona.primer_nombre = primer_nombre
                persona.primer_apellido = primer_apellido
                persona.segundo_nombre = segundo_nombre
                persona.segundo_apellido = segundo_apellido
                persona.email = email
                persona.telefono = telefono
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Perfil de persona no encontrado'
                }), 404

            usuario.persona = persona

            if UsuarioService.actualizar_usuario_completo(usuario.id, usuario):
                actualizado = UsuarioService.obtener_usuario(usuario.id, incluir_inactivos=True)
                g.current_user = actualizado
                persona_dict = actualizado.persona.to_dict() if actualizado and actualizado.persona else {}
                return jsonify({
                    'status': 'success',
                    'message': 'Perfil actualizado exitosamente',
                    'data': {
                        'nombre_completo': persona_dict.get('nombre_completo') or '',
                        'email': persona_dict.get('email') or '',
                        'telefono': persona_dict.get('telefono'),
                        'fecha_creacion': persona_dict.get('fecha_creacion')
                    }
                }), 200

            return jsonify({
                'status': 'error',
                'message': 'No se pudo actualizar el perfil'
            }), 400

        except Exception as e:
            return _respuesta_error(str(e), 500)

    @staticmethod
    def actualizar_usuario(id):
        try:
            data = request.get_json()
            print(f"[USUARIO][PUT] Datos recibidos para id={id}: {data}")

            if not data:
                return UsuarioController._error("No se recibieron datos para actualizar", 400)

            usuario = UsuarioService.obtener_usuario(id, incluir_inactivos=True)
            if not usuario:
                return UsuarioController._error(MSG_USER_NOT_FOUND, 404)

            # Validaciones
            error = UsuarioController._validar_campos(data, usuario)
            if error:
                return error

            # Actualizaciones
            UsuarioController._actualizar_datos_persona(usuario, data)
            UsuarioController._actualizar_datos_usuario(usuario, data)

            # Persistencia
            if UsuarioService.actualizar_usuario_completo(id, usuario):
                UsuarioController._emitir_actualizacion(id, usuario)
                return jsonify({
                    'status': 'success',
                    'message': 'Usuario actualizado exitosamente',
                    'data': usuario.to_dict()
                }), 200

            return UsuarioController._error(
                'No se pudo actualizar el usuario. Verificar datos enviados.', 400
            )

        except Exception as e:
            print(f"[USUARIO][PUT] Error inesperado: {e}")
            return UsuarioController._error(str(e), 500)

    # --------------------------
    # Métodos auxiliares privados
    # --------------------------

    @staticmethod
    def _error(message, status):
        return jsonify({'status': 'error', 'message': message}), status

    @staticmethod
    def _validar_campos(data, usuario):
        required_fields = ['primer_nombre', 'primer_apellido', 'email']

        for field in required_fields:
            if field in data and not data[field]:
                return UsuarioController._error(MSG_FIELD_REQUIRED.format(field=field), 400)

        if 'email' in data:
            email = data['email'].strip()
            if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
                return UsuarioController._error(MSG_INVALID_EMAIL_FORMAT, 400)
            if email != usuario.persona.email and UsuarioService.buscar_por_email(email):
                return UsuarioController._error(MSG_EMAIL_ALREADY_REGISTERED, 400)

        if 'password' in data and len(data['password']) < 6:
            return UsuarioController._error(MSG_PASSWORD_TOO_SHORT, 400)

        if 'id_rol' in data:
            try:
                int(data['id_rol'])
            except (TypeError, ValueError):
                return UsuarioController._error('El id_rol debe ser numérico', 400)

        return None

    @staticmethod
    def _actualizar_datos_persona(usuario, data):
        persona = usuario.persona
        campos = [
            'primer_nombre', 'segundo_nombre', 'primer_apellido',
            'segundo_apellido', 'email', 'telefono'
        ]
        for campo in campos:
            if campo in data:
                valor = data[campo] or None
                setattr(persona, campo, valor)

        if 'id_rol' in data:
            persona.id_rol = int(data['id_rol'])

    @staticmethod
    def _actualizar_datos_usuario(usuario, data):
        if 'password' in data:
            usuario.set_password(data['password'])
        if 'estado' in data:
            usuario.estado = EstadoUsuario(data['estado'])
        if 'id_rol' in data:
            usuario.id_rol = int(data['id_rol'])

    @staticmethod
    def _emitir_actualizacion(id, usuario):
        try:
            emit_update('usuario_updated', {'id': id, 'data': usuario.to_dict()})
        except NameError:
            print("WebSocket no disponible, omitiendo emisión")

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
                    'message': MSG_USER_NOT_FOUND
                }), 404
                
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
