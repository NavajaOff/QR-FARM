"""Controlador Usuario."""
from datetime import datetime, timedelta
import re
import jwt
from flask import jsonify, request, current_app, g
from ..models.usuario import Usuario, EstadoUsuario
from ..services.usuario_service import UsuarioService

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
        print(f"WebSocket no disponible, evento omitido: {event}")

class UsuarioController:
    # Error message constants
    MSG_INVALID_EMAIL_FORMAT = 'El formato del email no es válido'
    MSG_USER_NOT_FOUND = 'Usuario no encontrado'
    MSG_EMAIL_ALREADY_REGISTERED = 'El email ya está registrado'
    MSG_CLAVE_CORTA = 'La contraseña debe tener al menos 6 caracteres'
    MSG_NOT_AUTHENTICATED = 'No autenticado'
    MSG_FIELD_REQUIRED = 'El campo {field} es requerido'
    @staticmethod
    def registrar_usuario():
        """
        Registrar un nuevo usuario.
        Si el usuario actual es super admin, puede asignar tenant_id al nuevo usuario.
        """
        try:
            from flask import g
            from ..utils.tenant import get_current_tenant_id
            
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
                        'message': UsuarioController.MSG_FIELD_REQUIRED.format(field=field)
                    }), 400

            # Validar formato de email básico
            email = data.get('email', '').strip()
            if not _validar_email(email):
                return jsonify({
                    'status': 'error',
                    'message': UsuarioController.MSG_INVALID_EMAIL_FORMAT
                }), 400

            # Validar longitud de contraseña
            password = data.get('password', '')
            if len(password) < 6:
                return jsonify({
                    'status': 'error',
                    'message': UsuarioController.MSG_CLAVE_CORTA
                }), 400

            # Verificar si el email ya existe
            if UsuarioService.buscar_por_email(email):
                return jsonify({
                    'status': 'error',
                    'message': UsuarioController.MSG_EMAIL_ALREADY_REGISTERED
                }), 400

            # Verificar si hay token y cargar usuario si existe (para permitir super admin crear usuarios con tenant)
            es_super_admin = False
            tenant_id_override = None
            
            # Intentar obtener token del header (opcional)
            auth_header = request.headers.get('Authorization', '').strip()
            current_user = None
            
            if auth_header:
                try:
                    from flask import current_app
                    import jwt
                    parts = auth_header.split()
                    if len(parts) == 2 and parts[0].lower() == 'bearer':
                        token = parts[1]
                        payload = jwt.decode(
                            token,
                            current_app.config['SECRET_KEY'],
                            algorithms=['HS256']
                        )
                        user_id = payload.get('user_id')
                        if user_id:
                            current_user = UsuarioService.obtener_usuario(user_id, incluir_inactivos=True)
                except Exception:
                    # Si falla la autenticación, continuar como registro público
                    pass
            
            if current_user and hasattr(current_user, 'rol') and current_user.rol:
                rol_nombre = None
                if hasattr(current_user.rol, 'nombre_rol'):
                    rol_nombre = current_user.rol.nombre_rol
                elif hasattr(current_user.rol, 'rol'):
                    rol_nombre = current_user.rol.rol
                
                if rol_nombre == 'super_admin':
                    es_super_admin = True
                    # Permitir asignar tenant_id si viene en los datos
                    if 'tenant_id' in data and data['tenant_id']:
                        try:
                            tenant_id_override = int(data['tenant_id'])
                        except (ValueError, TypeError):
                            return jsonify({
                                'status': 'error',
                                'message': 'tenant_id debe ser un número válido'
                            }), 400

            # Crear persona y usuario desde los datos de registro
            persona, usuario = Usuario.from_registration_data(data)
            
            # Si hay id_rol en los datos, asignarlo (solo para super admin)
            if es_super_admin and 'id_rol' in data and data['id_rol']:
                try:
                    persona.id_rol = int(data['id_rol'])
                    usuario.id_rol = int(data['id_rol'])
                except (ValueError, TypeError):
                    pass

            # Crear el usuario en la base de datos
            # Si es super admin y hay tenant_id, usar crear_usuario, sino usar registrar_usuario
            if es_super_admin and tenant_id_override is not None:
                nuevo_usuario, mensaje = UsuarioService.crear_usuario(
                    persona, usuario, 
                    tenant_id_override=tenant_id_override, 
                    es_super_admin=True
                )
            else:
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
                    'role': usuario.rol.nombre_rol if usuario.rol else 'usuario',
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
                    'message': UsuarioController.MSG_USER_NOT_FOUND
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
            current_user = _obtener_usuario_actual()
            print(f"[USUARIO] obtener_todos_usuarios llamado por user_id={getattr(current_user, 'id', None)}")

            if not current_user:
                return jsonify({
                    'status': 'error',
                    'message': 'Usuario no autenticado'
                }), 401

            tenant_id = None
            es_super_admin = False

            # Obtener rol del usuario actual
            rol_nombre = None
            if hasattr(current_user, 'rol') and current_user.rol:
                if hasattr(current_user.rol, 'nombre_rol'):
                    rol_nombre = current_user.rol.nombre_rol
                elif hasattr(current_user.rol, 'rol'):
                    rol_nombre = current_user.rol.rol

            tenant_id = getattr(current_user, 'tenant_id', None)
            print(f"[USUARIO] Usuario actual: rol={rol_nombre}, tenant_id={tenant_id}")

            if rol_nombre == 'super_admin':
                es_super_admin = True
                print(f"[USUARIO] Usuario es SUPER_ADMIN")

                # Super admin puede filtrar por tenant_id usando query param
                tenant_id_param = request.args.get('tenant_id')
                if tenant_id_param:
                    try:
                        tenant_id = int(tenant_id_param)
                        print(f"[USUARIO] Super admin filtrando por tenant_id={tenant_id}")
                    except (ValueError, TypeError):
                        print(f"[USUARIO] WARNING: tenant_id inválido en query param: {tenant_id_param}")
                        tenant_id = None
            else:
                # Administradores normales SOLO pueden ver usuarios de su mismo tenant
                if not tenant_id:
                    print(f"[USUARIO] ERROR: Administrador sin tenant_id, no puede listar usuarios")
                    return jsonify({
                        'status': 'error',
                        'message': 'No se puede determinar el tenant del usuario'
                    }), 403
                print(f"[USUARIO] Administrador normal, filtrando por tenant_id={tenant_id}")

            # El servicio ahora maneja automáticamente la exclusión de super_admin para usuarios no privilegiados
            usuarios = UsuarioService.obtener_todos_usuarios(
                incluir_inactivos=True,
                tenant_id=tenant_id  # None para super_admin sin filtro, o tenant_id específico
            )

            print(f"[USUARIO] Total usuarios retornados: {len(usuarios)}")

            # Log roles and tenants of returned users
            for usuario in usuarios:
                u_rol = getattr(usuario, 'rol', None)
                u_rol_nombre = None
                if u_rol:
                    if hasattr(u_rol, 'nombre_rol'):
                        u_rol_nombre = u_rol.nombre_rol
                    elif hasattr(u_rol, 'rol'):
                        u_rol_nombre = u_rol.rol
                u_tenant = getattr(usuario, 'tenant_id', None)
                u_email = getattr(usuario.persona, 'email', None) if usuario.persona else None
                print(f"[USUARIO] Usuario retornado: id={usuario.id}, email={u_email}, rol={u_rol_nombre}, tenant_id={u_tenant}")

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
            print(f"[USUARIO] Cambiando estado del usuario id={id} a estado={nuevo_estado}")

            if nuevo_estado not in ['activo', 'inactivo']:
                print(f"[USUARIO] ERROR: Estado inválido: {nuevo_estado}")
                return jsonify({
                    'status': 'error',
                    'message': 'Estado inválido. Debe ser "activo" o "inactivo"'
                }), 400

            # Verificar que el usuario existe
            usuario_existente = UsuarioService.obtener_usuario(id, incluir_inactivos=True)
            if not usuario_existente:
                print(f"[USUARIO] ERROR: Usuario con id={id} no encontrado")
                return jsonify({
                    'status': 'error',
                    'message': UsuarioController.MSG_USER_NOT_FOUND
                }), 404

            print(f"[USUARIO] Usuario encontrado: id={usuario_existente.id}, estado_actual={usuario_existente.estado}")

            # Actualizar estado
            from ..models.usuario import EstadoUsuario
            usuario_existente.estado = EstadoUsuario(nuevo_estado)

            if UsuarioService.actualizar_usuario(id, usuario_existente):
                print(f"[USUARIO] Estado actualizado exitosamente")
                return jsonify({
                    'status': 'success',
                    'message': f'Usuario {"activado" if nuevo_estado == "activo" else "desactivado"} exitosamente'
                }), 200
            else:
                print(f"[USUARIO] ERROR: No se pudo actualizar el estado del usuario")
                return jsonify({
                    'status': 'error',
                    'message': 'Error al actualizar el estado del usuario'
                }), 400

        except Exception as e:
            print(f"[USUARIO] EXCEPCIÓN en cambiar_estado_usuario: {str(e)}")
            import traceback
            traceback.print_exc()
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
            return _respuesta_error(str(e), 500)

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
                return UsuarioController._error(UsuarioController.MSG_USER_NOT_FOUND, 404)

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
                return UsuarioController._error(UsuarioController.MSG_FIELD_REQUIRED.format(field=field), 400)

        if 'email' in data:
            email = data['email'].strip()
            if not _validar_email(email):
                return UsuarioController._error(UsuarioController.MSG_INVALID_EMAIL_FORMAT, 400)
            if email != usuario.persona.email and UsuarioService.buscar_por_email(email):
                return UsuarioController._error(UsuarioController.MSG_EMAIL_ALREADY_REGISTERED, 400)

        if 'password' in data and len(data['password']) < 6:
            return UsuarioController._error(UsuarioController.MSG_CLAVE_CORTA, 400)

        if 'id_rol' in data:
            try:
                rol_id = int(data['id_rol'])
                # BLOQUEO: No permitir asignar rol super_admin desde la API
                from ..database.db import get_connection
                conn = get_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT rol FROM roles WHERE id = %s", (rol_id,))
                rol = cursor.fetchone()
                cursor.close()
                conn.close()
                
                if rol and rol.get('rol') == 'super_admin':
                    return UsuarioController._error('No se puede asignar el rol super_admin. Este rol solo se crea desde variables de entorno.', 403)
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
                    'message': UsuarioController.MSG_USER_NOT_FOUND
                }), 404
                
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
