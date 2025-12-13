"""Controlador Usuario."""
from datetime import datetime, timedelta, timezone
import logging
import re
import jwt
from flask import jsonify, request, current_app, g
from ..models.usuario import Usuario, EstadoUsuario
from ..services.usuario_service import UsuarioService
from ..services.recovery_service import RecoveryService
from ..utils.auth import token_required

logger = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
ERROR_PROCESAR_SOLICITUD = 'Error al procesar la solicitud'

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
    def emit_update(event, _data=None):
        logger.debug("WebSocket no disponible, evento omitido: %s", event)

class UsuarioController:
    # Error message constants
    MSG_INVALID_EMAIL_FORMAT = 'El formato del email no es válido'
    MSG_USER_NOT_FOUND = 'Usuario no encontrado'
    MSG_EMAIL_ALREADY_REGISTERED = 'El email ya está registrado'
    MSG_CLAVE_CORTA = 'La contraseña debe tener al menos 6 caracteres'
    MSG_NOT_AUTHENTICATED = 'No autenticado'
    MSG_FIELD_REQUIRED = 'El campo {field} es requerido'
    MSG_RECOVERY_EMAIL_REQUIRED = 'El email es obligatorio para recuperar la contraseña'
    MSG_RECOVERY_TOKEN_INVALID = 'Token de recuperación inválido o expirado'
    
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
    def request_password_recovery():
        data = request.get_json(silent=True) or {}
        email = (data.get('email') or '').strip()

        if not email:
            return _respuesta_error(UsuarioController.MSG_RECOVERY_EMAIL_REQUIRED, 400)

        try:
            result = RecoveryService.request_password_recovery(email)
            return jsonify({
                'status': 'success',
                'message': result.get('message', 'Solicitud de recuperación creada. El administrador revisará tu solicitud.'),
                'recovery_id': result.get('recovery_id')
            }), 200
        except ValueError as ve:
            return _respuesta_error(str(ve), 400)
        except Exception:
            logger.exception("Error al solicitar recuperación de contraseña")
            return _respuesta_error(ERROR_PROCESAR_SOLICITUD, 500)

    @staticmethod
    def confirm_password_recovery():
        data = request.get_json(silent=True) or {}
        token = (data.get('token') or '').strip()
        password = data.get('password')
        email = (data.get('email') or '').strip()

        try:
            RecoveryService.confirm_password_recovery(token, password, email)
            return jsonify({
                'status': 'success',
                'message': 'Contraseña actualizada correctamente.'
            }), 200
        except ValueError as ve:
            return _respuesta_error(str(ve), 400)
        except Exception:
            logger.exception("Error al confirmar recuperación de contraseña")
            return _respuesta_error(ERROR_PROCESAR_SOLICITUD, 500)

    @staticmethod
    @token_required
    def list_recovery_requests():
        """List pending password recovery requests for current admin."""
        try:
            from flask import g
            from ..utils.tenant import get_current_tenant_id, _obtener_rol_nombre
            
            current_user = getattr(g, 'current_user', None)
            if not current_user:
                return _respuesta_error('Usuario no autenticado', 401)
            
            rol_nombre = _obtener_rol_nombre(current_user)
            is_superadmin = rol_nombre == 'super_admin'
            tenant_id = None
            
            # Superadmin can see all admin requests or filter by tenant
            if is_superadmin:
                tenant_param = request.args.get('tenant_id')
                if tenant_param:
                    try:
                        tenant_id = int(tenant_param)
                    except (ValueError, TypeError):
                        pass
            else:
                # Regular admin sees only user requests from their tenant (excluding their own)
                tenant_id = get_current_tenant_id(require_tenant=True)
                if tenant_id is None:
                    return _respuesta_error('No se pudo determinar el tenant', 400)
            
            requests = RecoveryService.list_pending_requests(
                tenant_id=tenant_id,
                current_user_id=current_user.id,
                is_superadmin=is_superadmin
            )
            return jsonify({
                'status': 'success',
                'data': requests
            }), 200
        except Exception:
            logger.exception("Error al listar solicitudes de recuperación")
            return _respuesta_error(ERROR_PROCESAR_SOLICITUD, 500)

    @staticmethod
    @token_required
    def approve_recovery_request(recovery_id: int):
        """Approve a password recovery request."""
        try:
            from flask import g
            current_user = getattr(g, 'current_user', None)
            if not current_user:
                return _respuesta_error('Usuario no autenticado', 401)
            
            result = RecoveryService.approve_recovery_request(recovery_id, current_user.id)
            return jsonify({
                'status': 'success',
                'message': result.get('message'),
                'token': result.get('token')  # Include token for admin visibility
            }), 200
        except ValueError as ve:
            return _respuesta_error(str(ve), 400)
        except Exception:
            logger.exception("Error al aprobar solicitud de recuperación")
            return _respuesta_error(ERROR_PROCESAR_SOLICITUD, 500)

    @staticmethod
    @token_required
    def reject_recovery_request(recovery_id: int):
        """Reject a password recovery request."""
        try:
            from flask import g
            current_user = getattr(g, 'current_user', None)
            if not current_user:
                return _respuesta_error('Usuario no autenticado', 401)
            
            RecoveryService.reject_recovery_request(recovery_id, current_user.id)
            return jsonify({
                'status': 'success',
                'message': 'Solicitud rechazada correctamente.'
            }), 200
        except ValueError as ve:
            return _respuesta_error(str(ve), 400)
        except Exception:
            logger.exception("Error al rechazar solicitud de recuperación")
            return _respuesta_error(ERROR_PROCESAR_SOLICITUD, 500)
    
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
        # Si es super_admin y tiene tenant_id_override, usar crear_usuario
        if es_super_admin and tenant_id_override is not None:
            return UsuarioService.crear_usuario(
                persona, usuario, 
                tenant_id_override=tenant_id_override, 
                es_super_admin=True
            )
        
        # Si es super_admin pero no tiene tenant_id_override, obtener tenant_id del usuario actual
        if es_super_admin:
            current_user = UsuarioController._obtener_usuario_desde_token()
            tenant_id_del_usuario = None
            if current_user and hasattr(current_user, 'tenant_id'):
                tenant_id_del_usuario = current_user.tenant_id
            
            # Si el usuario actual tiene tenant_id, usarlo
            if tenant_id_del_usuario:
                return UsuarioService.crear_usuario(
                    persona, usuario,
                    tenant_id_override=tenant_id_del_usuario,
                    es_super_admin=True
                )
            # Si no tiene tenant_id, pasar None a registrar_usuario para que lo obtenga del contexto
            return UsuarioService.registrar_usuario(persona, usuario, tenant_id_override=None)
        
        # Para usuarios normales (tenant_admin), usar registrar_usuario que obtiene el tenant_id del contexto
        return UsuarioService.registrar_usuario(persona, usuario, tenant_id_override=None)
    
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
            
            # Si no es super_admin y tiene tenant_id, usar ese tenant_id automáticamente
            tenant_id_override, tenant_error = UsuarioController._obtener_tenant_id_override(es_super_admin_flag, data)
            if tenant_error:
                return UsuarioController._error(tenant_error, 400)
            
            # Si no es super_admin y no se especificó tenant_id, usar el tenant_id del usuario actual
            if not es_super_admin_flag and tenant_id_override is None:
                if current_user and hasattr(current_user, 'tenant_id') and current_user.tenant_id:
                    tenant_id_override = current_user.tenant_id
            
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
        
        # Obtener tenant_id del usuario - asegurar que está disponible
        tenant_id = getattr(usuario, 'tenant_id', None)
        
        # Si no tiene tenant_id en el objeto, obtenerlo desde la tabla personas (NO usuarios)
        if tenant_id is None and usuario and hasattr(usuario, 'id_persona'):
            try:
                from ..database.db import get_connection
                conn = get_connection()
                if conn:
                    cursor = conn.cursor(dictionary=True)
                    # Obtener tenant_id desde personas, no desde usuarios
                    cursor.execute("SELECT tenant_id FROM personas WHERE id = %s", (usuario.id_persona,))
                    result = cursor.fetchone()
                    if result and result.get('tenant_id') is not None:
                        tenant_id = result['tenant_id']
                        # Actualizar el objeto usuario con el tenant_id
                        usuario.tenant_id = tenant_id
                        logger.info(f"[LOGIN] tenant_id obtenido desde personas para usuario {usuario.id} (persona {usuario.id_persona}): {tenant_id}")
                    cursor.close()
                    conn.close()
            except Exception as e:
                logger.error(f"[LOGIN] Error obteniendo tenant_id desde personas: {e}")
        
        payload = {
            'user_id': usuario.id,
            'email': email_token,
            'role': role_token,
            'tenant_id': tenant_id,  # Incluir tenant_id en el token
            'exp': datetime.now(timezone.utc) + timedelta(hours=24)
        }
        
        logger.info(f"[LOGIN] Token JWT generado para usuario {usuario.id}: user_id={usuario.id}, role={role_token}, tenant_id={tenant_id}")
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
                'message': ERROR_PROCESAR_SOLICITUD
            }), 500

    @staticmethod
    def obtener_usuario(id):
        try:
            current_user = _obtener_usuario_actual()
            tenant_id = None
            if current_user and not UsuarioController._es_super_admin(current_user):
                tenant_id = getattr(current_user, 'tenant_id', None)
            
            usuario = UsuarioService.obtener_usuario(id, tenant_id_override=tenant_id)

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
            logger.error("Error en obtener_usuario: %s", e, exc_info=True)
            return jsonify({
                'status': 'error',
                'message': ERROR_PROCESAR_SOLICITUD
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
    def _obtener_tenant_id_desde_token():
        """Obtiene tenant_id desde g.tenant_id o g.jwt_payload."""
        tenant_id = None
        if hasattr(g, 'tenant_id') and g.tenant_id is not None:
            tenant_id = g.tenant_id
        elif hasattr(g, 'jwt_payload'):
            tenant_id = g.jwt_payload.get('tenant_id')
        return tenant_id
    
    @staticmethod
    def _obtener_tenant_id_desde_bd(current_user):
        """Obtiene tenant_id desde la base de datos para el usuario actual."""
        try:
            from ..database.db import get_connection
            conn = get_connection()
            if not conn:
                return None
            
            cursor = conn.cursor(dictionary=True)
            if not hasattr(current_user, 'id_persona') or current_user.id_persona is None:
                cursor.execute("SELECT id_persona FROM usuarios WHERE id = %s", (current_user.id,))
                usuario_result = cursor.fetchone()
                if usuario_result:
                    current_user.id_persona = usuario_result['id_persona']
            
            if hasattr(current_user, 'id_persona') and current_user.id_persona:
                cursor.execute("SELECT tenant_id FROM personas WHERE id = %s", (current_user.id_persona,))
                result = cursor.fetchone()
                if result and result.get('tenant_id') is not None:
                    tenant_id = result['tenant_id']
                    current_user.tenant_id = tenant_id
                    logger.info(f"[USUARIO_CONTROLLER] tenant_id obtenido desde personas para usuario {current_user.id} (persona_id={current_user.id_persona}): {tenant_id}")
                    cursor.close()
                    conn.close()
                    return tenant_id
            
            cursor.close()
            conn.close()
        except Exception as e:
            logger.error(f"[USUARIO_CONTROLLER] Error obteniendo tenant_id del usuario desde personas: {e}")
        return None
    
    @staticmethod
    def _obtener_tenant_id_super_admin():
        """Obtiene tenant_id para super admin desde query params."""
        tenant_id_param = request.args.get('tenant_id')
        if not tenant_id_param:
            logger.info("[USUARIO_CONTROLLER] Super admin sin tenant_id, verá todos los usuarios")
            return None, None
        
        try:
            tenant_id = int(tenant_id_param)
            logger.info(f"[USUARIO_CONTROLLER] Super admin filtrando por tenant_id: {tenant_id}")
            return tenant_id, None
        except (ValueError, TypeError):
            logger.warning(f"[USUARIO_CONTROLLER] tenant_id inválido en query params: {tenant_id_param}")
            return None, None
    
    @staticmethod
    def _obtener_tenant_id_filtrado(current_user):
        """
        Obtiene el tenant_id según el tipo de usuario (super_admin o normal).
        
        IMPORTANTE: tenant_id está en personas (p.tenant_id), NO en usuarios (u.tenant_id).
        Esta función asegura que el tenant_id se obtenga correctamente desde personas.
        """
        tenant_id_from_token = UsuarioController._obtener_tenant_id_desde_token()
        if tenant_id_from_token:
            current_user.tenant_id = tenant_id_from_token
        
        es_super_admin = UsuarioController._es_super_admin(current_user)
        if es_super_admin:
            return UsuarioController._obtener_tenant_id_super_admin()
        
        tenant_id = tenant_id_from_token or getattr(current_user, 'tenant_id', None)
        if tenant_id is None and hasattr(g, 'jwt_payload'):
            tenant_id = g.jwt_payload.get('tenant_id')
            if tenant_id:
                current_user.tenant_id = tenant_id
        
        if tenant_id is None and current_user:
            tenant_id = UsuarioController._obtener_tenant_id_desde_bd(current_user)
        
        if not tenant_id:
            user_id = getattr(current_user, 'id', 'unknown')
            persona_id = getattr(current_user, 'id_persona', 'unknown')
            logger.error(f"[USUARIO_CONTROLLER] CRÍTICO: No se puede determinar tenant_id para usuario {user_id} (persona_id={persona_id})")
            return None, 'No se puede determinar el tenant del usuario. Contacte al administrador.'
        
        logger.info(f"[USUARIO_CONTROLLER] tenant_id final para usuario {current_user.id}: {tenant_id} (desde personas)")
        return tenant_id, None
    
    @staticmethod
    def _obtener_tenant_id_para_listado(current_user):
        """Obtiene tenant_id para listado de usuarios."""
        es_super = UsuarioController._es_super_admin(current_user)
        if es_super:
            tenant_id_param = request.args.get('tenant_id')
            if tenant_id_param:
                try:
                    return int(tenant_id_param), None
                except (ValueError, TypeError):
                    logger.warning(f"[USUARIO_CONTROLLER] tenant_id inválido en query params: {tenant_id_param}")
            return None, None
        
        if hasattr(g, 'tenant_id') and g.tenant_id is not None:
            current_user.tenant_id = g.tenant_id
            return g.tenant_id, None
        
        if hasattr(g, 'jwt_payload') and g.jwt_payload.get('tenant_id'):
            tenant_id = g.jwt_payload.get('tenant_id')
            current_user.tenant_id = tenant_id
            g.tenant_id = tenant_id
            return tenant_id, None
        
        if hasattr(current_user, 'tenant_id') and current_user.tenant_id is not None:
            return current_user.tenant_id, None
        
        tenant_id, tenant_error = UsuarioController._obtener_tenant_id_filtrado(current_user)
        if tenant_error:
            return None, tenant_error
        if tenant_id is None:
            logger.error(f"[USUARIO_CONTROLLER] CRÍTICO: No se pudo obtener tenant_id para usuario {current_user.id}")
            return None, 'No se puede determinar el tenant del usuario. Por favor, cierre sesión y vuelva a iniciar sesión.'
        
        return tenant_id, None
    
    @staticmethod
    def _filtrar_usuarios_por_tenant(usuarios, tenant_id):
        """Filtra usuarios por tenant_id y retorna lista filtrada."""
        if tenant_id is None:
            return usuarios
        
        usuarios_filtrados = []
        for usuario in usuarios:
            if usuario.tenant_id == tenant_id:
                usuarios_filtrados.append(usuario)
            else:
                logger.warning(f"[USUARIO_CONTROLLER] Usuario {usuario.id} con tenant_id={usuario.tenant_id} no coincide con tenant_id esperado={tenant_id}, omitiendo")
                print(f"[USUARIO_CONTROLLER] BLOQUEADO: Usuario {usuario.id} (email={usuario.persona.email}) con tenant_id={usuario.tenant_id} != {tenant_id}")
        
        logger.info(f"[USUARIO_CONTROLLER] Después de validación adicional: {len(usuarios_filtrados)} usuarios del tenant {tenant_id}")
        return usuarios_filtrados
    
    @staticmethod
    def obtener_todos_usuarios():
        """
        Obtiene todos los usuarios con aislamiento multi-tenant estricto.
        
        IMPORTANTE: 
        - Super admin puede ver todos o filtrar por tenant_id en query params
        - Usuarios normales SOLO ven usuarios de su mismo tenant_id (desde personas)
        """
        print("[USUARIO_CONTROLLER] 🚀 obtener_todos_usuarios() INICIADO")
        try:
            current_user, error_response, error_status = UsuarioController._validar_autenticacion_para_listado()
            if error_response:
                return error_response, error_status
            
            tenant_id, tenant_error = UsuarioController._obtener_tenant_id_para_listado(current_user)
            if tenant_error:
                return jsonify({'status': 'error', 'message': tenant_error}), 403
            
            es_super = UsuarioController._es_super_admin(current_user)
            if not es_super and tenant_id is None:
                logger.error(f"[USUARIO_CONTROLLER] ERROR CRÍTICO: Usuario {current_user.id} no es super_admin pero tenant_id es None")
                return jsonify({
                    'status': 'error',
                    'message': 'No se puede determinar el tenant del usuario. Por favor, cierre sesión y vuelva a iniciar sesión.'
                }), 403
            
            # Superadmin solo ve admins (no usuarios normales)
            solo_admins = es_super
            usuarios = UsuarioService.obtener_todos_usuarios(incluir_inactivos=True, tenant_id=tenant_id, solo_admins=solo_admins)
            usuarios = UsuarioController._filtrar_usuarios_por_tenant(usuarios, tenant_id)
            
            return jsonify({
                'status': 'success',
                'data': [usuario.to_dict() for usuario in usuarios]
            }), 200

        except Exception as e:
            logger.error("Error en obtener_todos_usuarios: %s", e, exc_info=True)
            print(f"[USUARIO_CONTROLLER] ERROR: {e}")
            return jsonify({
                'status': 'error',
                'message': ERROR_PROCESAR_SOLICITUD
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

            current_user = _obtener_usuario_actual()
            tenant_id = None
            if current_user and not UsuarioController._es_super_admin(current_user):
                tenant_id = getattr(current_user, 'tenant_id', None)

            usuario_existente = UsuarioService.obtener_usuario(id, incluir_inactivos=True, tenant_id_override=tenant_id)
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
                'message': ERROR_PROCESAR_SOLICITUD
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
            return _respuesta_error(ERROR_PROCESAR_SOLICITUD, 500)

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
            return _respuesta_error(ERROR_PROCESAR_SOLICITUD, 500)

    @staticmethod
    def actualizar_usuario(id):
        try:
            data = request.get_json()

            if not data:
                return UsuarioController._error("No se recibieron datos para actualizar", 400)

            current_user = _obtener_usuario_actual()
            tenant_id = None
            if current_user and not UsuarioController._es_super_admin(current_user):
                tenant_id = getattr(current_user, 'tenant_id', None)

            usuario = UsuarioService.obtener_usuario(id, incluir_inactivos=True, tenant_id_override=tenant_id)
            if not usuario:
                return UsuarioController._error(UsuarioController.MSG_USER_NOT_FOUND, 404)

            error = UsuarioController._validar_campos(data, usuario)
            if error:
                return error

            UsuarioController._actualizar_datos_persona(usuario, data)
            UsuarioController._actualizar_datos_usuario(usuario, data)

            if UsuarioService.actualizar_usuario_completo(id, usuario, tenant_id_override=tenant_id):
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
            return UsuarioController._error(ERROR_PROCESAR_SOLICITUD, 500)

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
            current_user = _obtener_usuario_actual()
            tenant_id = None
            if current_user and not UsuarioController._es_super_admin(current_user):
                tenant_id = getattr(current_user, 'tenant_id', None)

            success, message = UsuarioService.eliminar_usuario(id, tenant_id_override=tenant_id)
            if success:
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
                    'message': message or UsuarioController.MSG_USER_NOT_FOUND
                }), 404
                
        except Exception as e:
            logger.error("Error en eliminar_usuario: %s", e, exc_info=True)
            return jsonify({
                'status': 'error',
                'message': ERROR_PROCESAR_SOLICITUD
            }), 500
