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
        def emit_update(event, data):
            print(f"WebSocket no disponible, evento omitido: {event} -> {data}")
except ImportError:
    def emit_update(event, data):
        print(f"WebSocket no disponible, evento omitido: {event} -> {data}")


def _validar_email(email: str) -> bool:
    """Validar formato de email con regex precompilada."""
    return bool(EMAIL_REGEX.match(email))


def _obtener_componentes_nombre(nombre_completo: str, persona) -> tuple:
    """Obtener componentes del nombre completo."""
    partes = nombre_completo.split()
    primer_nombre = partes[0]

    if len(partes) > 1:
        primer_apellido = partes[-1]
    elif persona:
        primer_apellido = persona.primer_apellido or ''
    else:
        primer_apellido = ''

    if len(partes) > 2:
        segundo_nombre = ' '.join(partes[1:-1])
    elif len(partes) == 2:
        segundo_nombre = partes[1]
    elif persona:
        segundo_nombre = persona.segundo_nombre
    else:
        segundo_nombre = None

    segundo_apellido = persona.segundo_apellido if persona else None

    return primer_nombre, segundo_nombre, primer_apellido, segundo_apellido


def _validar_campos_requeridos(data, campos):
    """Validar que los campos requeridos tengan contenido."""
    for field in campos:
        if field in data and not data[field]:
            return field
    return None


def _validar_nuevo_email(email: str, usuario_existente):
    """Validar formato y unicidad del email."""
    if not _validar_email(email):
        return EMAIL_INVALID_MSG

    correo_actual = usuario_existente.persona.email if usuario_existente.persona else None
    if email != correo_actual and UsuarioService.buscar_por_email(email):
        return EMAIL_REGISTERED_MSG
    return None


def _obtener_usuario_actual():
    """Retornar el usuario autenticado actual."""
    return getattr(g, 'current_user', None)


def _respuesta_error(message: str, status_code: int):
    """Construir respuesta de error homogénea."""
    return jsonify({
        'status': 'error',
        'message': message
    }), status_code


def _respuesta_success(message: str, data: dict | None = None, status_code: int = 200):
    """Construir respuesta de éxito homogénea."""
    payload = {
        'status': 'success',
        'message': message
    }
    if data is not None:
        payload['data'] = data
    return jsonify(payload), status_code


def _procesar_actualizacion_perfil(usuario, data):
    """Procesar la actualización del perfil del usuario autenticado."""
    nombre_completo = (data.get('nombre_completo') or '').strip()
    email = (data.get('email') or '').strip()
    telefono = data.get('telefono')

    mensaje_error, status_error = _validar_datos_perfil(nombre_completo, email)
    if mensaje_error:
        return _respuesta_error(mensaje_error, status_error)

    mensaje_persona, persona_actualizada = _actualizar_perfil_persona(
        usuario,
        nombre_completo,
        email,
        telefono
    )
    if mensaje_persona:
        return _respuesta_error(mensaje_persona, 404)

    usuario.persona = persona_actualizada

    if not UsuarioService.actualizar_usuario_completo(usuario.id, usuario):
        return _respuesta_error('No se pudo actualizar el perfil', 400)

    actualizado = UsuarioService.obtener_usuario(usuario.id, incluir_inactivos=True)
    g.current_user = actualizado
    persona_dict = actualizado.persona.to_dict() if actualizado and actualizado.persona else {}
    data_response = {
        'nombre_completo': persona_dict.get('nombre_completo') or '',
        'email': persona_dict.get('email') or '',
        'telefono': persona_dict.get('telefono'),
        'fecha_creacion': persona_dict.get('fecha_creacion')
    }

    return _respuesta_success('Perfil actualizado exitosamente', data_response)


def _procesar_actualizacion_usuario(id_usuario, usuario_existente, data):
    """Procesar actualización completa de un usuario por ID."""
    required_fields = ['primer_nombre', 'primer_apellido', 'email']
    campo_faltante = _validar_campos_requeridos(data, required_fields)
    if campo_faltante:
        return _respuesta_error(f'El campo {campo_faltante} es requerido', 400)

    if 'email' in data:
        email = data['email'].strip()
        mensaje_email = _validar_nuevo_email(email, usuario_existente)
        if mensaje_email:
            return _respuesta_error(mensaje_email, 400)
        data['email'] = email

    if 'password' in data:
        password = data['password']
        if len(password) < 6:
            return _respuesta_error('La contraseña debe tener al menos 6 caracteres', 400)

    mensaje_persona = _actualizar_datos_persona(usuario_existente, data)
    if mensaje_persona:
        return _respuesta_error(mensaje_persona, 404)

    mensaje_usuario = _actualizar_datos_usuario(usuario_existente, data)
    if mensaje_usuario:
        return _respuesta_error(mensaje_usuario, 400)

    if UsuarioService.actualizar_usuario_completo(id_usuario, usuario_existente):
        try:
            emit_update('usuario_updated', {
                'id': id_usuario,
                'data': usuario_existente.to_dict()
            })
        except NameError:
            print("WebSocket no disponible, omitiendo emisión")

        return _respuesta_success(
            'Usuario actualizado exitosamente',
            usuario_existente.to_dict()
        )

    return _respuesta_error('No se pudo actualizar el usuario. Verificar datos enviados.', 400)


def _actualizar_datos_persona(usuario_existente, data):
    """Actualizar datos de la persona asociada al usuario."""
    persona = usuario_existente.persona
    if not persona:
        return 'Perfil de persona no encontrado'

    if 'primer_nombre' in data:
        persona.primer_nombre = data['primer_nombre']
    if 'segundo_nombre' in data:
        persona.segundo_nombre = data['segundo_nombre'] or None
    if 'primer_apellido' in data:
        persona.primer_apellido = data['primer_apellido']
    if 'segundo_apellido' in data:
        persona.segundo_apellido = data['segundo_apellido'] or None
    if 'email' in data:
        persona.email = data['email']
    if 'telefono' in data:
        persona.telefono = data['telefono'] or None

    return None


def _actualizar_datos_usuario(usuario_existente, data):
    """Actualizar datos del usuario (no persona)."""
    if 'password' in data:
        usuario_existente.set_password(data['password'])

    if 'estado' in data:
        usuario_existente.estado = EstadoUsuario(data['estado'])

    if 'id_rol' in data:
        try:
            nuevo_rol = int(data['id_rol'])
        except (TypeError, ValueError):
            return 'El id_rol debe ser numérico'
        usuario_existente.id_rol = nuevo_rol
        if usuario_existente.persona:
            usuario_existente.persona.id_rol = nuevo_rol

    return None


def _validar_datos_perfil(nombre_completo: str, email: str):
    """Validar campos obligatorios del perfil."""
    if not nombre_completo or not email:
        return 'Nombre completo y email son obligatorios', 400
    if not _validar_email(email):
        return EMAIL_INVALID_MSG, 400
    return None, None


def _actualizar_perfil_persona(usuario, nombre_completo, email, telefono):
    """Actualizar la información de la persona del usuario."""
    persona = usuario.persona
    if not persona:
        return 'Perfil de persona no encontrado', 404

    primer_nombre, segundo_nombre, primer_apellido, segundo_apellido = _obtener_componentes_nombre(
        nombre_completo,
        persona
    )

    persona.primer_nombre = primer_nombre
    persona.primer_apellido = primer_apellido
    persona.segundo_nombre = segundo_nombre
    persona.segundo_apellido = segundo_apellido
    persona.email = email
    persona.telefono = telefono

    return None, persona


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
            email = data.get('email', '').strip()
            if not _validar_email(email):
                return jsonify({
                    'status': 'error',
                    'message': EMAIL_INVALID_MSG
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
                    'message': EMAIL_REGISTERED_MSG
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
                    'message': USER_NOT_FOUND_MSG
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
                    'message': USER_NOT_FOUND_MSG
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
                return _respuesta_error('No autenticado', 401)

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
                return _respuesta_error('No autenticado', 401)

            data = request.get_json() or {}
            return _procesar_actualizacion_perfil(usuario, data)

        except Exception as e:
            return _respuesta_error(str(e), 500)

    @staticmethod
    def actualizar_usuario(id):
        try:
            data = request.get_json()
            print(f"[USUARIO][PUT] Datos recibidos para id={id}: {data}")

            if not data:
                return _respuesta_error('No se recibieron datos para actualizar', 400)

            # Verificar si el usuario existe
            usuario_existente = UsuarioService.obtener_usuario(id, incluir_inactivos=True)
            if not usuario_existente:
                return _respuesta_error(USER_NOT_FOUND_MSG, 404)

            return _procesar_actualizacion_usuario(id, usuario_existente, data)

        except Exception as e:
            print(f"[USUARIO][PUT] Error inesperado: {e}")
            return _respuesta_error(str(e), 500)

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
                    'message': USER_NOT_FOUND_MSG
                }), 404
                
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
