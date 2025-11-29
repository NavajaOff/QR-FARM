"""Controlador Usuario."""
from datetime import datetime, timedelta
import logging
import re
import jwt
from flask import jsonify, request, current_app, g
from ..models.usuario import Usuario, EstadoUsuario
from ..services.usuario_service import UsuarioService

logger = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')

def _validar_email(email):
    return EMAIL_REGEX.match(email) is not None

def _obtener_usuario_actual():
    return getattr(g, 'current_user', None)

def _respuesta_error(message, status):
    return jsonify({'status': 'error', 'message': message}), status

def _validar_datos_perfil(data):
    nombre_completo = (data.get('nombre_completo') or '').strip()
    email = (data.get('email') or '').strip()
    telefono = data.get('telefono')

    if not nombre_completo or not email:
        return None, jsonify({
            'status': 'error',
            'message': 'Nombre completo y email son obligatorios'
        }), 400

    if not _validar_email(email):
        return None, jsonify({
            'status': 'error',
            'message': UsuarioController.MSG_INVALID_EMAIL_FORMAT
        }), 400

    return {'nombre_completo': nombre_completo, 'email': email, 'telefono': telefono}, None, None

def _parsear_nombre_completo(nombre_completo, usuario):
    partes = nombre_completo.split()
    primer_nombre = partes[0]

    if len(partes) > 1:
        primer_apellido = partes[-1]
    else:
        if usuario.persona:
            primer_apellido = usuario.persona.primer_apellido
        else:
            primer_apellido = ''

    if len(partes) > 2:
        segundo_nombre = ' '.join(partes[1:-1])
    elif len(partes) == 2:
        segundo_nombre = partes[1]
    else:
        if usuario.persona:
            segundo_nombre = usuario.persona.segundo_nombre
        else:
            segundo_nombre = None

    if usuario.persona:
        segundo_apellido = usuario.persona.segundo_apellido
    else:
        segundo_apellido = None

    return primer_nombre, segundo_nombre, primer_apellido, segundo_apellido

def _actualizar_persona_perfil(persona, primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, email, telefono):
    if not persona:
        return False
    persona.primer_nombre = primer_nombre
    persona.primer_apellido = primer_apellido
    persona.segundo_nombre = segundo_nombre
    persona.segundo_apellido = segundo_apellido
    persona.email = email
    persona.telefono = telefono
    return True

def _respuesta_actualizacion_exitosa(actualizado):
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
try:
    from ...app import emit_update
except ImportError:
    def emit_update(event, data=None):
        logger.debug("WebSocket no disponible, evento omitido: %s", event)

class UsuarioController:
    # Error message constants
    MSG_INVALID_EMAIL_FORMAT = 'El formato del email no es válido'
    MSG_USER_NOT_FOUND = 'Usuario no encontrado'
    MSG_EMAIL_ALREADY_REGISTERED = 'El email ya está registrado'
    MSG_CLAVE_CORTA = 'La contraseña debe tener al menos 6 caracteres'
    MSG_NOT_AUTHENTICATED = 'No autenticado'
    MSG_FIELD_REQUIRED = 'El campo {field} es requerido'
    
    @staticmethod
    def _validar_datos_registro(data):
        """Valida los datos de registro y retorna error si hay algún problema."""
        if not data:
            return None, 'No se recibieron datos JSON válidos', 400
        
        required_fields = ['primer_nombre', 'primer_apellido', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return None, UsuarioController.MSG_FIELD_REQUIRED.format(field=field), 400
        
        email = data.get('email', '').strip()
        if not _validar_email(email):
            return None, UsuarioController.MSG_INVALID_EMAIL_FORMAT, 400
        
        password = data.get('password', '')
        if len(password) < 6:
            return None, UsuarioController.MSG_CLAVE_CORTA, 400
        
        if UsuarioService.buscar_por_email(email):
            return None, UsuarioController.MSG_EMAIL_ALREADY_REGISTERED, 400
        
        return {'email': email, 'password': password}, None, None
    
    @staticmethod
    def _obtener_usuario_desde_token():
        """Obtiene el usuario actual desde el token JWT si existe."""
        auth_header = request.headers.get('Authorization', '').strip()
        if not auth_header:
            return None
        
        try:
            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != 'bearer':
                return None
            
            token = parts[1]
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            user_id = payload.get('user_id')
            if not user_id:
                return None
            
            return UsuarioService.obtener_usuario(user_id, incluir_inactivos=True)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
            logger.debug("Token inválido o expirado: %s", e)
            return None
        except Exception as e:
            logger.warning("Error al obtener usuario desde token: %s", e)
            return None
    
    @staticmethod
    def _obtener_nombre_rol(usuario):
        """Obtiene el nombre del rol de un usuario."""
        if not usuario or not hasattr(usuario, 'rol') or not usuario.rol:
            return None
        
        if hasattr(usuario.rol, 'nombre_rol'):
            return usuario.rol.nombre_rol
        
        if hasattr(usuario.rol, 'rol'):
            return usuario.rol.rol
        
        return None
    
    @staticmethod
    def _obtener_nombre_rol_por_id(rol_id):
        """Obtiene el nombre del rol por su ID."""
        try:
            from ..database.db import get_connection
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT rol FROM roles WHERE id = %s", (rol_id,))
            rol = cursor.fetchone()
            cursor.close()
            conn.close()
            
            return rol.get('rol') if rol else None
        except Exception as e:
            logger.warning("Error al obtener rol por ID: %s", e)
            return None
    
    @staticmethod
    def _es_super_admin(usuario):
        """Verifica si un usuario es super admin."""
        rol_nombre = UsuarioController._obtener_nombre_rol(usuario)
        return rol_nombre == 'super_admin'
    
    @staticmethod
    def _obtener_tenant_id_override(es_super_admin, data):
        """Obtiene y valida el tenant_id override de los datos si es super admin."""
        if not es_super_admin:
            return None, None
        
        if 'tenant_id' not in data or not data['tenant_id']:
            return None, None
        
        try:
            return int(data['tenant_id']), None
        except (ValueError, TypeError):
            return None, 'tenant_id debe ser un número válido'
    
    @staticmethod
    def _asignar_rol_si_es_super_admin(es_super_admin, data, persona, usuario):
        """Asigna el rol a persona y usuario si es super admin."""
        if not es_super_admin or 'id_rol' not in data or not data['id_rol']:
            return
        
        try:
            rol_id = int(data['id_rol'])
            persona.id_rol = rol_id
            usuario.id_rol = rol_id
        except (ValueError, TypeError):
            pass
    
    @staticmethod
    def _crear_usuario_en_bd(es_super_admin, tenant_id_override, persona, usuario):
        """Crea el usuario en la base de datos usando el servicio apropiado."""
        if es_super_admin and tenant_id_override is not None:
            return UsuarioService.crear_usuario(
                persona, usuario, 
                tenant_id_override=tenant_id_override, 
                es_super_admin=True
            )
        
        return UsuarioService.registrar_usuario(persona, usuario)
    
    @staticmethod
    def registrar_usuario():
        """
        Registrar un nuevo usuario.
        Si el usuario actual es super admin, puede asignar tenant_id al nuevo usuario.
        """
        try:
            data = request.get_json()
            datos_validos, error_msg, error_status = UsuarioController._validar_datos_registro(data)
            if datos_validos is None:
                return UsuarioController._error(error_msg, error_status)
            
            current_user = UsuarioController._obtener_usuario_desde_token()
            es_super_admin_flag = UsuarioController._es_super_admin(current_user)
            
            tenant_id_override, tenant_error = UsuarioController._obtener_tenant_id_override(es_super_admin_flag, data)
            if tenant_error:
                return UsuarioController._error(tenant_error, 400)
            
            persona, usuario = Usuario.from_registration_data(data)
            UsuarioController._asignar_rol_si_es_super_admin(es_super_admin_flag, data, persona, usuario)
            
            nuevo_usuario, mensaje = UsuarioController._crear_usuario_en_bd(
                es_super_admin_flag, tenant_id_override, persona, usuario
            )
            
            if nuevo_usuario:
                return jsonify({
                    'status': 'success',
                    'message': mensaje,
                    'data': nuevo_usuario.to_dict()
                }), 201
            
            return UsuarioController._error(mensaje, 400)

        except Exception as e:
            logger.error("Error inesperado en registro: %s", e, exc_info=True)
            return UsuarioController._error('Error interno del servidor', 500)

    @staticmethod
    def _validar_credenciales_login(data):
        """Valida que email y password estén presentes."""
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return None, jsonify({
                'status': 'error',
                'message': 'Email y contraseña son requeridos'
            }), 400
        return email, password, None

    @staticmethod
    def _generar_token_jwt(usuario, email):
        """Genera token JWT para el usuario autenticado."""
        email_token = usuario.persona.email if usuario.persona else email
        role_token = usuario.rol.nombre_rol if usuario.rol else 'usuario'
        payload = {
            'user_id': usuario.id,
            'email': email_token,
            'role': role_token,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def _respuesta_login_exitoso(usuario, token):
        """Retorna respuesta exitosa de login."""
        return jsonify({
            'status': 'success',
            'message': 'Login exitoso',
            'token': token,
            'user': usuario.to_dict()
        }), 200

    @staticmethod
    def login():
        try:
            data = request.get_json()
            email, password, error_response = UsuarioController._validar_credenciales_login(data)
            if error_response:
                return error_response

            usuario = UsuarioService.autenticar_usuario(email, password)
            if not usuario:
                return jsonify({
                    'status': 'error',
                    'message': 'Credenciales inválidas'
                }), 401

            token = UsuarioController._generar_token_jwt(usuario, email)
            return UsuarioController._respuesta_login_exitoso(usuario, token)

        except Exception:
            logger.error("Error en login", exc_info=True)
            return jsonify({
                'status': 'error',
                'message': 'Error al procesar la solicitud'
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
                    'message': UsuarioController.MSG_USER_NOT_FOUND
                }), 404

        except Exception as e:
            logger.error("Error en login: %s", e, exc_info=True)
            return jsonify({
                'status': 'error',
                'message': 'Error al procesar la solicitud'
            }), 500

    @staticmethod
    def _validar_autenticacion_para_listado():
        """Valida que haya un usuario autenticado y retorna error si no existe."""
        current_user = _obtener_usuario_actual()
        if not current_user:
            return None, jsonify({
                'status': 'error',
                'message': 'Usuario no autenticado'
            }), 401
        return current_user, None, None
    
    @staticmethod
    def _obtener_tenant_id_filtrado(current_user):
        """Obtiene el tenant_id según el tipo de usuario (super_admin o normal)."""
        tenant_id = getattr(current_user, 'tenant_id', None)
        
        if UsuarioController._es_super_admin(current_user):
            tenant_id_param = request.args.get('tenant_id')
            if tenant_id_param:
                try:
                    return int(tenant_id_param), None
                except (ValueError, TypeError):
                    return None, None
            return None, None
        
        if not tenant_id:
            return None, 'No se puede determinar el tenant del usuario'
        
        return tenant_id, None
    
    @staticmethod
    def obtener_todos_usuarios():
        try:
            current_user, error_response, error_status = UsuarioController._validar_autenticacion_para_listado()
            if error_response:
                return error_response, error_status
            
            tenant_id, tenant_error = UsuarioController._obtener_tenant_id_filtrado(current_user)
            if tenant_error:
                return jsonify({
                    'status': 'error',
                    'message': tenant_error
                }), 403
            
            usuarios = UsuarioService.obtener_todos_usuarios(
                incluir_inactivos=True,
                tenant_id=tenant_id
            )
            
            return jsonify({
                'status': 'success',
                'data': [usuario.to_dict() for usuario in usuarios]
            }), 200

        except Exception as e:
            logger.error("Error en obtener_todos_usuarios: %s", e, exc_info=True)
            return jsonify({
                'status': 'error',
                'message': 'Error al procesar la solicitud'
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

            usuario_existente = UsuarioService.obtener_usuario(id, incluir_inactivos=True)
            if not usuario_existente:
                return jsonify({
                    'status': 'error',
                    'message': UsuarioController.MSG_USER_NOT_FOUND
                }), 404

            from ..models.usuario import EstadoUsuario
            usuario_existente.estado = EstadoUsuario(nuevo_estado)

            if UsuarioService.actualizar_usuario(id, usuario_existente):
                mensaje = 'Usuario activado exitosamente' if nuevo_estado == 'activo' else 'Usuario desactivado exitosamente'
                return jsonify({
                    'status': 'success',
                    'message': mensaje
                }), 200
            
            return jsonify({
                'status': 'error',
                'message': 'Error al actualizar el estado del usuario'
            }), 400

        except Exception as e:
            logger.error("Error en cambiar_estado_usuario: %s", e, exc_info=True)
            return jsonify({
                'status': 'error',
                'message': 'Error al procesar la solicitud'
            }), 500

    @staticmethod
    def obtener_perfil_actual():
        try:
            usuario = _obtener_usuario_actual()
            if not usuario:
                return jsonify({
                    'status': 'error',
                    'message': UsuarioController.MSG_NOT_AUTHENTICATED
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
            logger.error("Error en obtener_perfil_actual: %s", e, exc_info=True)
            return _respuesta_error('Error al procesar la solicitud', 500)

    @staticmethod
    def actualizar_perfil_actual():
        try:
            usuario = _obtener_usuario_actual()
            if not usuario:
                return jsonify({
                    'status': 'error',
                    'message': UsuarioController.MSG_NOT_AUTHENTICATED
                }), 401

            data = request.get_json() or {}
            datos_validos, error_response, status = _validar_datos_perfil(data)
            if error_response:
                return error_response, status

            nombre_completo = datos_validos['nombre_completo']
            email = datos_validos['email']
            telefono = datos_validos['telefono']

            primer_nombre, segundo_nombre, primer_apellido, segundo_apellido = _parsear_nombre_completo(nombre_completo, usuario)

            if not _actualizar_persona_perfil(usuario.persona, primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, email, telefono):
                return jsonify({
                    'status': 'error',
                    'message': 'Perfil de persona no encontrado'
                }), 404

            if UsuarioService.actualizar_usuario_completo(usuario.id, usuario):
                actualizado = UsuarioService.obtener_usuario(usuario.id, incluir_inactivos=True)
                g.current_user = actualizado
                return _respuesta_actualizacion_exitosa(actualizado)

            return jsonify({
                'status': 'error',
                'message': 'No se pudo actualizar el perfil'
            }), 400

        except Exception as e:
            logger.error("Error en obtener_perfil_actual: %s", e, exc_info=True)
            return _respuesta_error('Error al procesar la solicitud', 500)

    @staticmethod
    def actualizar_usuario(id):
        try:
            data = request.get_json()

            if not data:
                return UsuarioController._error("No se recibieron datos para actualizar", 400)

            usuario = UsuarioService.obtener_usuario(id, incluir_inactivos=True)
            if not usuario:
                return UsuarioController._error(UsuarioController.MSG_USER_NOT_FOUND, 404)

            error = UsuarioController._validar_campos(data, usuario)
            if error:
                return error

            UsuarioController._actualizar_datos_persona(usuario, data)
            UsuarioController._actualizar_datos_usuario(usuario, data)

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
            logger.error("Error en actualizar_usuario: %s", e, exc_info=True)
            return UsuarioController._error('Error al procesar la solicitud', 500)

    # --------------------------
    # Métodos auxiliares privados
    # --------------------------

    @staticmethod
    def _error(message, status):
        return jsonify({'status': 'error', 'message': message}), status

    @staticmethod
    def _validar_campos_requeridos(data):
        """Valida que los campos requeridos no estén vacíos."""
        required_fields = ['primer_nombre', 'primer_apellido', 'email']
        for field in required_fields:
            if field in data and not data[field]:
                return UsuarioController._error(UsuarioController.MSG_FIELD_REQUIRED.format(field=field), 400)
        return None

    @staticmethod
    def _validar_email_en_actualizacion(data, usuario):
        """Valida el email en actualización de usuario."""
        if 'email' not in data:
            return None
        email = data['email'].strip()
        if not _validar_email(email):
            return UsuarioController._error(UsuarioController.MSG_INVALID_EMAIL_FORMAT, 400)
        if email != usuario.persona.email and UsuarioService.buscar_por_email(email):
            return UsuarioController._error(UsuarioController.MSG_EMAIL_ALREADY_REGISTERED, 400)
        return None

    @staticmethod
    def _validar_password_en_actualizacion(data):
        """Valida la contraseña en actualización."""
        if 'password' in data and len(data['password']) < 6:
            return UsuarioController._error(UsuarioController.MSG_CLAVE_CORTA, 400)
        return None

    @staticmethod
    def _validar_rol_en_actualizacion(data):
        """Valida el rol en actualización."""
        if 'id_rol' not in data:
            return None
        try:
            rol_id = int(data['id_rol'])
            rol_nombre = UsuarioController._obtener_nombre_rol_por_id(rol_id)
            if rol_nombre == 'super_admin':
                return UsuarioController._error('No se puede asignar el rol super_admin. Este rol solo se crea desde variables de entorno.', 403)
        except (TypeError, ValueError):
            return UsuarioController._error('El id_rol debe ser numérico', 400)
        return None

    @staticmethod
    def _validar_campos(data, usuario):
        """Valida todos los campos en actualización de usuario."""
        error = UsuarioController._validar_campos_requeridos(data)
        if error:
            return error
        
        error = UsuarioController._validar_email_en_actualizacion(data, usuario)
        if error:
            return error
        
        error = UsuarioController._validar_password_en_actualizacion(data)
        if error:
            return error
        
        error = UsuarioController._validar_rol_en_actualizacion(data)
        if error:
            return error
        
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
            logger.debug("WebSocket no disponible, omitiendo emisión")

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
                    logger.debug("WebSocket no disponible, omitiendo emisión")
                return jsonify({
                    'status': 'success',
                    'message': 'Usuario eliminado exitosamente'
                }), 200
            else:
                return jsonify({
                    'status': 'error',
                    'message': UsuarioController.MSG_USER_NOT_FOUND
                }), 404
                
        except Exception as e:
            logger.error("Error en eliminar_usuario: %s", e, exc_info=True)
            return jsonify({
                'status': 'error',
                'message': 'Error al procesar la solicitud'
            }), 500
