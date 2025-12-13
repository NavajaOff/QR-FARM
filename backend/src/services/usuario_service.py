# Servicio Usuario
from typing import List, Optional, Tuple
from datetime import datetime
import logging
from ..database.db import get_connection

logger = logging.getLogger(__name__)
from ..models.usuario import Usuario, Persona, Rol, EstadoUsuario
from ..models.cargo import Cargo

class UsuarioService:
    # Constantes para mensajes y queries
    EMAIL_DUPLICADO_MSG = "El email ya está registrado"
    QUERY_PERSONA_ID = "SELECT id_persona FROM usuarios WHERE id = %s"
    SQL_AND_TENANT_ID = " AND tenant_id = %s"
    @staticmethod
    def _obtener_tenant_id() -> Optional[int]:
        """Obtiene el tenant_id del contexto actual."""
        try:
            from ..utils.tenant import get_current_tenant_id
            return get_current_tenant_id()
        except Exception:
            return None

    @staticmethod
    def _determinar_si_es_super_admin():
        """
        Determina si el usuario actual es super admin.
        
        IMPORTANTE: Verifica el ROL real del usuario, no solo el tenant_id.
        Un usuario puede tener tenant_id=None temporalmente pero no ser super_admin.
        """
        try:
            from flask import g
            if not hasattr(g, 'current_user') or not g.current_user:
                return False
            
            # Verificar el rol real del usuario
            rol_nombre = None
            if hasattr(g.current_user, 'rol') and g.current_user.rol:
                if hasattr(g.current_user.rol, 'nombre_rol'):
                    rol_nombre = g.current_user.rol.nombre_rol
                elif hasattr(g.current_user.rol, 'rol'):
                    rol_nombre = g.current_user.rol.rol
            
            # Solo es super_admin si el rol es explícitamente 'super_admin'
            is_super = rol_nombre and rol_nombre.lower() == 'super_admin'
            print(f"[USUARIO_SERVICE] _determinar_si_es_super_admin: rol={rol_nombre}, is_super={is_super}")
            return is_super
        except Exception as e:
            print(f"[USUARIO_SERVICE] Error en _determinar_si_es_super_admin: {e}")
            return False

    @staticmethod
    def _construir_condiciones_sql(incluir_inactivos, tenant_id, excluir_super_admin, solo_admins=False):
        """Construye las condiciones SQL para la consulta.
        
        IMPORTANTE: tenant_id está en la tabla personas (p.tenant_id), NO en usuarios (u.tenant_id).
        
        Args:
            solo_admins: Si es True, solo mostrar usuarios con rol admin/administrador (para superadmin)
        """
        conditions = []
        params = []
        if not incluir_inactivos:
            conditions.append("u.estado = 'activo'")
        if tenant_id is not None:
            conditions.append("p.tenant_id = %s")
            params.append(tenant_id)
            print(f"[USUARIO_SERVICE] Filtro de tenant_id aplicado desde personas: {tenant_id}")
        if excluir_super_admin:
            conditions.append("(r.rol IS NULL OR LOWER(TRIM(r.rol)) != 'super_admin')")
        if solo_admins:
            # Solo mostrar admins/administradores (no usuarios normales)
            conditions.append("LOWER(TRIM(r.rol)) IN ('admin', 'administrador')")
        return conditions, params
    
    @staticmethod
    def _validar_y_agregar_tenant_id_sql(sql, params, tenant_id):
        """Valida y agrega filtro de tenant_id al SQL si es necesario."""
        if tenant_id is not None and "p.tenant_id = %s" not in sql:
            if "WHERE" in sql:
                sql += " AND p.tenant_id = %s"
            else:
                sql += " WHERE p.tenant_id = %s"
            if tenant_id not in params:
                params = params + (tenant_id,)
        return sql, params
    
    @staticmethod
    def _procesar_resultados_usuarios(results, tenant_id):
        """Procesa resultados de BD y filtra por tenant_id."""
        usuarios = []
        for result in results:
            usuario = UsuarioService._crear_usuario_desde_resultado(result)
            if not usuario:
                continue
            if tenant_id is not None and usuario.tenant_id != tenant_id:
                print(f"[USUARIO_SERVICE] BLOQUEADO: Usuario {usuario.id} tiene p.tenant_id={usuario.tenant_id} pero se esperaba {tenant_id}, OMITIENDO por seguridad")
                continue
            usuarios.append(usuario)
        return usuarios
    
    @staticmethod
    def _obtener_tenant_id_desde_g():
        """Obtiene tenant_id desde Flask g."""
        try:
            from flask import g
            if hasattr(g, 'tenant_id') and g.tenant_id is not None:
                return g.tenant_id
            if hasattr(g, 'jwt_payload') and g.jwt_payload.get('tenant_id'):
                return g.jwt_payload.get('tenant_id')
            if hasattr(g, 'current_user') and g.current_user:
                return getattr(g.current_user, 'tenant_id', None)
        except Exception:
            pass
        return None
    
    @staticmethod
    def _obtener_tenant_id_para_listado(tenant_id, es_super_admin):
        """Obtiene tenant_id para listado de usuarios."""
        if tenant_id is not None:
            return tenant_id
        if es_super_admin:
            return None
        return UsuarioService._obtener_tenant_id_desde_g()

    @staticmethod
    def _crear_usuario_desde_resultado(result):
        """Crea un objeto Usuario desde un resultado de BD."""
        rol_nombre = result.get('rol_nombre')
        if rol_nombre and rol_nombre.lower() == 'super_admin':
            return None

        rol = None
        if rol_nombre:
            rol = Rol(
                id=result['id_rol'],
                nombre_rol=rol_nombre
            )
        
        cargo = None
        if result.get('cargo_id_db'):
            cargo = Cargo(
                id=result['cargo_id_db'],
                nombre_cargo=result.get('nombre_cargo', ''),
                descripcion=result.get('cargo_descripcion')
            )
        
        # Obtener tenant_id desde personas (p.tenant_id)
        # Cuando se hace SELECT u.*, p.*, el tenant_id viene de personas
        tenant_id_persona = result.get('tenant_id')
        
        persona = Persona(
            id=result['id_persona'],
            id_rol=result['id_rol'],
            primer_nombre=result['primer_nombre'],
            segundo_nombre=result['segundo_nombre'],
            primer_apellido=result['primer_apellido'],
            segundo_apellido=result['segundo_apellido'],
            email=result['email'],
            telefono=result['telefono'],
            fecha_creacion=result['fecha_creacion'],
            tenant_id=tenant_id_persona,
            cargo_id=result.get('cargo_id'),
            cargo=cargo
        )
        
        return Usuario(
            id=result['id'],
            id_persona=result['id_persona'],
            id_rol=result['id_rol'],
            contrasena=result.get('contrasena'),
            estado=EstadoUsuario(result['estado']),
            persona=persona,
            rol=rol,
            tenant_id=tenant_id_persona
        )

    @staticmethod
    def obtener_rol(id: int) -> Optional[Rol]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            sql = "SELECT * FROM roles WHERE id = %s"
            cursor.execute(sql, (id,))
            
            result = cursor.fetchone()
            if result:
                return Rol.from_dict(result)
            return None
            
        except Exception as e:
            print(f"Error al obtener rol: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def _validar_rol_super_admin(cursor, persona, usuario):
        """Valida que no se intente crear un super_admin desde la API."""
        if not (persona.id_rol or usuario.id_rol):
            return None
        rol_id = persona.id_rol or usuario.id_rol
        cursor.execute("SELECT rol FROM roles WHERE id = %s", (rol_id,))
        rol = cursor.fetchone()
        if rol and rol.get('rol') == 'super_admin':
            return "No se puede crear usuarios super_admin desde la API. Use el script de inicialización."
        return None

    @staticmethod
    def _validar_tenant_override(cursor, tenant_id_override, es_super_admin):
        """Valida y obtiene el tenant_id final."""
        if tenant_id_override is None:
            from ..utils.tenant import get_current_tenant_id
            return get_current_tenant_id(), None
        
        if not es_super_admin:
            return None, "Solo el super administrador puede asignar tenant_id al crear usuarios"
        
        cursor.execute("SELECT id FROM tenants WHERE id = %s AND estado = 'activo'", (tenant_id_override,))
        tenant = cursor.fetchone()
        if not tenant:
            return None, f"El tenant con ID {tenant_id_override} no existe o está inactivo"
        
        return tenant_id_override, None

    @staticmethod
    def _verificar_email_existente(cursor, email):
        """Verifica si el email ya está registrado."""
        cursor.execute("SELECT id FROM personas WHERE email = %s", (email,))
        return cursor.fetchone() is not None

    @staticmethod
    def _insertar_persona(cursor, persona, tenant_id):
        """Inserta la persona en la base de datos."""
        sql_persona = """
            INSERT INTO personas (
                id_rol, primer_nombre, segundo_nombre, primer_apellido,
                segundo_apellido, email, telefono, fecha_creacion, tenant_id, cargo_id
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s
            )
        """
        values_persona = (
            persona.id_rol, persona.primer_nombre, persona.segundo_nombre,
            persona.primer_apellido, persona.segundo_apellido,
            persona.email, persona.telefono, tenant_id, persona.cargo_id
        )
        cursor.execute(sql_persona, values_persona)
        return cursor.lastrowid

    @staticmethod
    def _insertar_usuario(cursor, id_persona, usuario, tenant_id):
        """Inserta el usuario en la base de datos.
        
        IMPORTANTE: tenant_id está en personas, NO en usuarios.
        Si la tabla usuarios tiene columna tenant_id, se puede insertar para compatibilidad,
        pero el valor real y único está en personas.
        """
        # Intentar insertar tenant_id en usuarios si la columna existe (para compatibilidad)
        # Pero el valor real está en personas
        try:
            sql_usuario = """
                INSERT INTO usuarios (
                    id_persona, id_rol, contrasena, estado, tenant_id
                ) VALUES (
                    %s, %s, %s, %s, %s
                )
            """
            values_usuario = (
                id_persona, usuario.id_rol or 1, usuario.contrasena,
                usuario.estado.value, tenant_id
            )
        except Exception:
            # Si la columna tenant_id no existe en usuarios, insertar sin ella
            sql_usuario = """
                INSERT INTO usuarios (
                    id_persona, id_rol, contrasena, estado
                ) VALUES (
                    %s, %s, %s, %s
                )
            """
            values_usuario = (
                id_persona, usuario.id_rol or 1, usuario.contrasena,
                usuario.estado.value
            )
        cursor.execute(sql_usuario, values_usuario)
        return cursor.lastrowid

    @staticmethod
    def crear_usuario(persona: Persona, usuario: Usuario, tenant_id_override: Optional[int] = None, es_super_admin: bool = False) -> Tuple[Optional[Usuario], str]:
        """
        Crear un nuevo usuario.
        
        Args:
            persona: Objeto Persona con datos de la persona
            usuario: Objeto Usuario con datos del usuario
            tenant_id_override: ID del tenant a asignar (solo si es_super_admin es True)
            es_super_admin: Si True, permite asignar tenant_id_override
        
        Returns:
            Tuple con el usuario creado y mensaje, o (None, mensaje_error)
        """
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            error = UsuarioService._validar_rol_super_admin(cursor, persona, usuario)
            if error:
                return None, error

            tenant_id_final, error = UsuarioService._validar_tenant_override(cursor, tenant_id_override, es_super_admin)
            if error:
                return None, error

            if UsuarioService._verificar_email_existente(cursor, persona.email):
                return None, "El email ya está registrado"

            try:
                if hasattr(conn, 'in_transaction') and conn.in_transaction:
                    conn.rollback()
                conn.start_transaction()

                id_persona = UsuarioService._insertar_persona(cursor, persona, tenant_id_final)
                usuario_id = UsuarioService._insertar_usuario(cursor, id_persona, usuario, tenant_id_final)

                conn.commit()

                usuario.id = usuario_id
                usuario.id_persona = id_persona
                usuario.tenant_id = tenant_id_final
                persona.id = id_persona
                usuario.persona = persona

                return usuario, "Usuario creado exitosamente"

            except Exception as e:
                conn.rollback()
                raise e

        except Exception as e:
            print(f"Error al crear usuario: {e}")
            return None, str(e)
        finally:
            if 'conn' in locals():
                conn.close()
                
    @staticmethod
    def actualizar_usuario(id: int, persona: Persona, usuario: Usuario) -> Tuple[Optional[Usuario], str]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Verificar que el usuario existe
            cursor.execute(UsuarioService.QUERY_PERSONA_ID, (id,))
            result = cursor.fetchone()
            if not result:
                return None, "Usuario no encontrado"
                
            id_persona = result['id_persona']
            
            # Verificar si el email ya existe para otro usuario
            cursor.execute("SELECT id FROM personas WHERE email = %s AND id != %s",
                         (persona.email, id_persona))
            if cursor.fetchone():
                return None, UsuarioService.EMAIL_DUPLICADO_MSG

            # Verificar si el username ya existe para otro usuario
            if usuario.username:
                cursor.execute("SELECT id FROM usuarios WHERE username = %s AND id != %s", 
                             (usuario.username, id))
                if cursor.fetchone():
                    return None, "El nombre de usuario ya está registrado"

            try:
                original_autocommit = getattr(conn, 'autocommit', True)
                if original_autocommit:
                    conn.autocommit = False
                elif hasattr(conn, 'in_transaction') and conn.in_transaction:
                    conn.rollback()

                # Actualizar persona
                sql_persona = """
                    UPDATE personas SET
                        id_rol = %s,
                        primer_nombre = %s,
                        segundo_nombre = %s,
                        primer_apellido = %s,
                        segundo_apellido = %s,
                        email = %s,
                        telefono = %s,
                        cargo_id = %s
                    WHERE id = %s
                """
                
                values_persona = (
                    persona.id_rol, persona.primer_nombre, persona.segundo_nombre,
                    persona.primer_apellido, persona.segundo_apellido, 
                    persona.email, persona.telefono, persona.cargo_id, id_persona
                )
                
                cursor.execute(sql_persona, values_persona)
                
                # Actualizar usuario
                sql_usuario = """
                    UPDATE usuarios SET
                        id_rol = %s,
                        username = %s,
                        estado = %s,
                        updated_at = NOW()
                    WHERE id = %s
                """
                
                values_usuario = (
                    usuario.id_rol, usuario.username,
                    usuario.estado.value, id
                )
                
                cursor.execute(sql_usuario, values_usuario)
                
                # Si hay nueva contrasena, actualizarla
                if usuario.password_hash:
                    sql_password = """
                        UPDATE usuarios SET
                            password_hash = %s
                        WHERE id = %s
                    """
                    cursor.execute(sql_password, (usuario.password_hash, id))
                
                # Commit de la transacción
                conn.commit()
                
                usuario.id = id
                usuario.id_persona = id_persona
                persona.id = id_persona
                usuario.persona = persona
                
                return usuario, "Usuario actualizado exitosamente"

            except Exception as e:
                # Rollback en caso de error
                conn.rollback()
                raise e
            
        except Exception as e:
            print(f"Error al actualizar usuario: {e}")
            return None, str(e)
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def obtener_usuarios() -> List[Usuario]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            sql = """
                SELECT 
                    u.id as usuario_id,
                    u.id_persona,
                    u.id_rol as usuario_rol_id,
                    u.username,
                    u.estado,
                    u.created_at as usuario_created,
                    u.updated_at as usuario_updated,
                    p.*,
                    r.nombre as rol_nombre,
                    r.descripcion as rol_descripcion
                FROM usuarios u
                INNER JOIN personas p ON u.id_persona = p.id
                INNER JOIN roles r ON p.id_rol = r.id
                ORDER BY u.created_at DESC
            """
            
            cursor.execute(sql)
            results = cursor.fetchall()
            
            usuarios = []
            for row in results:
                rol = Rol(
                    id=row['id_rol'],
                    nombre_rol=row['rol_nombre'],
                    descripcion=row['rol_descripcion']
                )
                
                persona = Persona(
                    id=row['id'],
                    id_rol=row['id_rol'],
                    primer_nombre=row['primer_nombre'],
                    segundo_nombre=row['segundo_nombre'],
                    primer_apellido=row['primer_apellido'],
                    segundo_apellido=row['segundo_apellido'],
                    email=row['email'],
                    telefono=row['telefono'],
                    rol=rol
                )
                
                usuario = Usuario(
                    id=row['usuario_id'],
                    id_persona=row['id_persona'],
                    id_rol=row['usuario_rol_id'],
                    username=row['username'],
                    estado=EstadoUsuario(row['estado']),
                    persona=persona,
                    rol=rol
                )
                
                usuarios.append(usuario)
                
            return usuarios
            
        except Exception as e:
            print(f"Error al obtener usuarios: {e}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def obtener_usuario_por_id(id: int) -> Optional[Usuario]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            sql = """
                SELECT 
                    u.id as usuario_id,
                    u.id_persona,
                    u.id_rol as usuario_rol_id,
                    u.username,
                    u.estado,
                    u.created_at as usuario_created,
                    u.updated_at as usuario_updated,
                    p.*,
                    r.nombre as rol_nombre,
                    r.descripcion as rol_descripcion
                FROM usuarios u
                INNER JOIN personas p ON u.id_persona = p.id
                INNER JOIN roles r ON p.id_rol = r.id
                WHERE u.id = %s
            """
            
            cursor.execute(sql, (id,))
            result = cursor.fetchone()
            
            if result:
                rol = Rol(
                    id=result['id_rol'],
                    nombre_rol=result['rol_nombre'],
                    descripcion=result['rol_descripcion']
                )
                
                persona = Persona(
                    id=result['id'],
                    id_rol=result['id_rol'],
                    primer_nombre=result['primer_nombre'],
                    segundo_nombre=result['segundo_nombre'],
                    primer_apellido=result['primer_apellido'],
                    segundo_apellido=result['segundo_apellido'],
                    email=result['email'],
                    telefono=result['telefono'],
                    rol=rol
                )
                
                usuario = Usuario(
                    id=result['usuario_id'],
                    id_persona=result['id_persona'],
                    id_rol=result['usuario_rol_id'],
                    username=result['username'],
                    estado=EstadoUsuario(result['estado']),
                    persona=persona,
                    rol=rol
                )
                
                return usuario
                
            return None
            
        except Exception as e:
            print(f"Error al obtener usuario: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def obtener_usuario_por_username(username: str) -> Optional[Usuario]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            sql = """
                SELECT 
                    u.id as usuario_id,
                    u.id_persona,
                    u.id_rol as usuario_rol_id,
                    u.username,
                    u.password_hash,
                    u.estado,
                    u.created_at as usuario_created,
                    u.updated_at as usuario_updated,
                    p.*,
                    r.nombre as rol_nombre,
                    r.descripcion as rol_descripcion
                FROM usuarios u
                INNER JOIN personas p ON u.id_persona = p.id
                INNER JOIN roles r ON p.id_rol = r.id
                WHERE u.username = %s
            """
            
            cursor.execute(sql, (username,))
            result = cursor.fetchone()
            
            if result:
                rol = Rol(
                    id=result['id_rol'],
                    nombre_rol=result['rol_nombre'],
                    descripcion=result['rol_descripcion']
                )
                
                persona = Persona(
                    id=result['id'],
                    id_rol=result['id_rol'],
                    primer_nombre=result['primer_nombre'],
                    segundo_nombre=result['segundo_nombre'],
                    primer_apellido=result['primer_apellido'],
                    segundo_apellido=result['segundo_apellido'],
                    email=result['email'],
                    telefono=result['telefono'],
                    rol=rol
                )
                
                usuario = Usuario(
                    id=result['usuario_id'],
                    id_persona=result['id_persona'],
                    id_rol=result['usuario_rol_id'],
                    username=result['username'],
                    password_hash=result['password_hash'],
                    estado=EstadoUsuario(result['estado']),
                    persona=persona,
                    rol=rol
                )
                
                return usuario
                
            return None
            
        except Exception as e:
            print(f"Error al obtener usuario: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def eliminar_usuario(id: int, tenant_id_override: Optional[int] = None) -> Tuple[bool, str]:
        """
        Eliminar usuario por ID con validación de tenant.
        
        Args:
            id: ID del usuario
            tenant_id_override: Si se proporciona, valida que el usuario pertenezca a este tenant
        """
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            tenant_id = tenant_id_override if tenant_id_override is not None else UsuarioService._obtener_tenant_id()
            
            # Verificar que el usuario existe y obtener id_persona
            # IMPORTANTE: tenant_id está en personas, no en usuarios
            sql_check = "SELECT u.id_persona, p.tenant_id FROM usuarios u INNER JOIN personas p ON u.id_persona = p.id WHERE u.id = %s"
            cursor.execute(sql_check, (id,))
            result = cursor.fetchone()
            if not result:
                return False, "Usuario no encontrado"
            
            # Validar tenant_id si no es super_admin
            # IMPORTANTE: tenant_id viene de personas (p.tenant_id)
            if tenant_id is not None and result.get('tenant_id') != tenant_id:
                return False, "No tiene permisos para eliminar este usuario"
                
            id_persona = result['id_persona']
            
            try:
                # Iniciar transacción
                conn.start_transaction()
                
                # Eliminar usuario (con validación de tenant si aplica)
                sql_delete_usuario = "DELETE FROM usuarios WHERE id = %s"
                params_usuario = (id,)
                if tenant_id is not None:
                    sql_delete_usuario += UsuarioService.SQL_AND_TENANT_ID
                    params_usuario = (id, tenant_id)
                
                cursor.execute(sql_delete_usuario, params_usuario)
                
                # Eliminar persona
                cursor.execute("DELETE FROM personas WHERE id = %s", (id_persona,))
                
                # Commit de la transacción
                conn.commit()
                
                return True, "Usuario eliminado exitosamente"
                
            except Exception as e:
                # Rollback en caso de error
                conn.rollback()
                raise e
            
        except Exception as e:
            print(f"Error al eliminar usuario: {e}")
            return False, str(e)
        finally:
            if 'conn' in locals() and conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass
    @staticmethod
    def _validar_rol_super_admin_registro(cursor, persona, usuario):
        """Valida que no se intente crear super_admin desde registro público."""
        if not (persona.id_rol or usuario.id_rol):
            return None
        rol_id = persona.id_rol or usuario.id_rol
        cursor.execute("SELECT rol FROM roles WHERE id = %s", (rol_id,))
        rol = cursor.fetchone()
        if rol and rol.get('rol') == 'super_admin':
            return "No se puede crear usuarios super_admin desde el registro público."
        return None
    
    @staticmethod
    def _validar_email_duplicado(cursor, email):
        """Valida que el email no esté duplicado."""
        cursor.execute("SELECT id FROM personas WHERE email = %s", (email,))
        if cursor.fetchone():
            return UsuarioService.EMAIL_DUPLICADO_MSG
        return None
    
    @staticmethod
    def _obtener_tenant_id_desde_token_bd(cursor):
        """Obtiene tenant_id desde el token JWT decodificado."""
        try:
            from flask import request, current_app, g
            import jwt
            if hasattr(g, 'tenant_id') and g.tenant_id:
                return g.tenant_id
            
            auth_header = request.headers.get('Authorization', '').strip()
            if not auth_header:
                return None
            
            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != 'bearer':
                return None
            
            token = parts[1]
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload.get('user_id')
            if not user_id:
                return None
            
            cursor.execute("SELECT u.id_persona FROM usuarios u WHERE u.id = %s", (user_id,))
            usuario_result = cursor.fetchone()
            if not usuario_result or not usuario_result.get('id_persona'):
                return None
            
            id_persona = usuario_result['id_persona']
            cursor.execute("SELECT tenant_id FROM personas WHERE id = %s", (id_persona,))
            result = cursor.fetchone()
            if result and result.get('tenant_id'):
                return result['tenant_id']
        except Exception:
            pass
        return None
    
    @staticmethod
    def _obtener_tenant_id_registro(tenant_id_override, cursor):
        """Obtiene tenant_id para registro desde múltiples fuentes."""
        if tenant_id_override is not None:
            return tenant_id_override
        
        from ..utils.tenant import get_current_tenant_id
        tenant_id = get_current_tenant_id()
        if tenant_id is not None:
            return tenant_id
        
        return UsuarioService._obtener_tenant_id_desde_token_bd(cursor)
    
    @staticmethod
    def _insertar_persona_registro(cursor, persona, tenant_id):
        """Inserta persona en la BD y retorna el ID."""
        sql_persona = """
            INSERT INTO personas (
                id_rol, primer_nombre, segundo_nombre, primer_apellido,
                segundo_apellido, email, telefono, fecha_creacion, tenant_id, cargo_id
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s
            )
        """
        values_persona = (
            persona.id_rol, persona.primer_nombre, persona.segundo_nombre,
            persona.primer_apellido, persona.segundo_apellido,
            persona.email, persona.telefono, tenant_id, persona.cargo_id
        )
        cursor.execute(sql_persona, values_persona)
        return cursor.lastrowid
    
    @staticmethod
    def _insertar_usuario_registro(cursor, id_persona, usuario, tenant_id):
        """Inserta usuario en la BD y retorna el ID."""
        sql_usuario = """
            INSERT INTO usuarios (
                id_persona, id_rol, contrasena, estado, tenant_id
            ) VALUES (
                %s, %s, %s, %s, %s
            )
        """
        values_usuario = (
            id_persona, usuario.id_rol or 1, usuario.contrasena,
            usuario.estado.value, tenant_id
        )
        cursor.execute(sql_usuario, values_usuario)
        return cursor.lastrowid
    
    @staticmethod
    def registrar_usuario(persona: Persona, usuario: Usuario, tenant_id_override: Optional[int] = None) -> Tuple[Optional[Usuario], str]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            error = UsuarioService._validar_rol_super_admin_registro(cursor, persona, usuario)
            if error:
                return None, error

            error = UsuarioService._validar_email_duplicado(cursor, persona.email)
            if error:
                return None, error

            try:
                if hasattr(conn, 'in_transaction') and conn.in_transaction:
                    conn.rollback()
                conn.start_transaction()

                tenant_id = UsuarioService._obtener_tenant_id_registro(tenant_id_override, cursor)
                id_persona = UsuarioService._insertar_persona_registro(cursor, persona, tenant_id)
                id_usuario = UsuarioService._insertar_usuario_registro(cursor, id_persona, usuario, tenant_id)

                conn.commit()

                usuario.id = id_usuario
                usuario.id_persona = id_persona
                usuario.tenant_id = tenant_id
                persona.id = id_persona
                usuario.persona = persona

                return usuario, "Usuario registrado exitosamente"

            except Exception as e:
                conn.rollback()
                raise e

        except Exception as e:
            print(f"Error al registrar usuario: {e}")
            return None, str(e)
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def obtener_usuario(id: int, incluir_inactivos: bool = False, tenant_id_override: Optional[int] = None) -> Optional[Usuario]:
        """
        Obtener usuario por ID con validación de tenant.
        
        Args:
            id: ID del usuario
            incluir_inactivos: Incluir usuarios inactivos
            tenant_id_override: Si se proporciona, valida que el usuario pertenezca a este tenant
        """
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            # Si tenant_id_override es None, NO filtrar por tenant (útil para autenticación)
            # Solo filtrar si se proporciona explícitamente
            tenant_id = tenant_id_override

            sql = """
                SELECT u.*, p.*, r.rol as rol_nombre, 
                       c.id as cargo_id_db, c.nombre_cargo, c.descripcion as cargo_descripcion 
                FROM usuarios u
                INNER JOIN personas p ON u.id_persona = p.id
                LEFT JOIN roles r ON u.id_rol = r.id
                LEFT JOIN cargos c ON p.cargo_id = c.id
                WHERE u.id = %s
            """
            params = (id,)

            if not incluir_inactivos:
                sql += " AND u.estado = 'activo'"
            
            # Validar tenant_id SOLO si se proporciona explícitamente (tenant_id_override)
            # IMPORTANTE: tenant_id está en personas (p.tenant_id), NO en usuarios (u.tenant_id)
            # Esto permite obtener el usuario sin filtrar por tenant para autenticación
            if tenant_id is not None:
                sql += " AND p.tenant_id = %s"
                params = params + (tenant_id,)
                print(f"[USUARIO_SERVICE] obtener_usuario: Filtrando por p.tenant_id={tenant_id}")
            else:
                print("[USUARIO_SERVICE] obtener_usuario: NO filtrando por tenant_id (obteniendo usuario completo)")

            cursor.execute(sql, params)

            result = cursor.fetchone()
            if result:
                # Crear rol
                rol = None
                if result.get('rol_nombre'):
                    rol = Rol(
                        id=result['id_rol'],
                        nombre_rol=result['rol_nombre']
                    )

                # Crear cargo
                cargo = None
                if result.get('cargo_id_db'):
                    cargo = Cargo(
                        id=result['cargo_id_db'],
                        nombre_cargo=result.get('nombre_cargo', ''),
                        descripcion=result.get('cargo_descripcion')
                    )

                # Crear persona
                persona = Persona(
                    id=result['id_persona'],
                    id_rol=result['id_rol'],
                    primer_nombre=result['primer_nombre'],
                    segundo_nombre=result['segundo_nombre'],
                    primer_apellido=result['primer_apellido'],
                    segundo_apellido=result['segundo_apellido'],
                    email=result['email'],
                    telefono=result['telefono'],
                    fecha_creacion=result['fecha_creacion'],
                    cargo_id=result.get('cargo_id'),
                    cargo=cargo
                )

                # Crear usuario
                # IMPORTANTE: tenant_id viene de personas (p.tenant_id), no de usuarios (u.tenant_id)
                tenant_id_persona = result.get('tenant_id')  # Este viene de p.* (personas)
                usuario = Usuario(
                    id=result['id'],
                    id_persona=result['id_persona'],
                    id_rol=result['id_rol'],
                    contrasena=result['contrasena'],
                    estado=EstadoUsuario(result['estado']),
                    persona=persona,
                    rol=rol,
                    tenant_id=tenant_id_persona  # tenant_id desde personas
                )
                print(f"[USUARIO_SERVICE] obtener_usuario: Usuario {usuario.id} con tenant_id={tenant_id_persona} desde personas")

                return usuario
            return None

        except Exception as e:
            print(f"Error al obtener usuario: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def obtener_todos_usuarios(incluir_inactivos: bool = False, tenant_id: Optional[int] = None, excluir_super_admin: bool = False, solo_admins: bool = False) -> List[Usuario]:
        """
        Obtener todos los usuarios con filtrado automático de super admin para usuarios no privilegiados.

        IMPORTANTE: 
        - Si tenant_id es None, NO filtrar (solo para super_admin)
        - Si tenant_id está definido, filtrar estrictamente por p.tenant_id
        
        Args:
            incluir_inactivos: Incluir usuarios inactivos
            tenant_id: Filtrar por tenant específico (None para super admin, OBLIGATORIO para usuarios normales)
            excluir_super_admin: Forzar exclusión de super admin (siempre True para no super admin)
        """
        print(f"[USUARIO_SERVICE] obtener_todos_usuarios called with incluir_inactivos={incluir_inactivos}, tenant_id={tenant_id}, excluir_super_admin={excluir_super_admin}")

        es_super_admin_actual = UsuarioService._determinar_si_es_super_admin()
        tenant_id = UsuarioService._obtener_tenant_id_para_listado(tenant_id, es_super_admin_actual)
        
        if not es_super_admin_actual:
            excluir_super_admin = True
            if tenant_id is None:
                print("[USUARIO_SERVICE] ERROR CRÍTICO: Usuario normal sin tenant_id después de todos los intentos. Retornando lista vacía por seguridad.")
                return []

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            sql = """
                SELECT u.*, 
                       p.id as id_persona,
                       p.id_rol as persona_id_rol,
                       p.primer_nombre,
                       p.segundo_nombre,
                       p.primer_apellido,
                       p.segundo_apellido,
                       p.email,
                       p.telefono,
                       p.fecha_creacion,
                       p.tenant_id,
                       p.cargo_id,
                       r.rol as rol_nombre,
                       c.id as cargo_id_db,
                       c.nombre_cargo,
                       c.descripcion as cargo_descripcion
                FROM usuarios u
                INNER JOIN personas p ON u.id_persona = p.id
                LEFT JOIN roles r ON u.id_rol = r.id
                LEFT JOIN cargos c ON p.cargo_id = c.id
            """

            conditions, params = UsuarioService._construir_condiciones_sql(incluir_inactivos, tenant_id, excluir_super_admin, solo_admins)
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
            
            sql, params = UsuarioService._validar_y_agregar_tenant_id_sql(sql, params, tenant_id)
            cursor.execute(sql, params)
            results = cursor.fetchall()
            usuarios = UsuarioService._procesar_resultados_usuarios(results, tenant_id)
            return usuarios

        except Exception as e:
            print(f"Error al obtener usuarios: {e}")
            # En caso de error de BD, retornar lista vacía (modo sin BD)
            return []
        finally:
            if 'conn' in locals():
                try:
                    conn.close()
                except Exception:
                    pass

    @staticmethod
    def actualizar_usuario(id: int, usuario: Usuario) -> bool:
        try:
            conn = get_connection()
            cursor = conn.cursor()

            sql = """
                UPDATE usuarios SET
                    estado = %s
                WHERE id = %s
            """

            values = (usuario.estado.value, id)

            cursor.execute(sql, values)
            conn.commit()

            return cursor.rowcount > 0

        except Exception as e:
            print(f"Error al actualizar usuario: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def _validar_usuario_para_actualizacion(cursor, id, tenant_id):
        """Valida que el usuario existe y pertenece al tenant correcto."""
        sql_check = "SELECT u.id_persona, p.tenant_id FROM usuarios u INNER JOIN personas p ON u.id_persona = p.id WHERE u.id = %s"
        cursor.execute(sql_check, (id,))
        result = cursor.fetchone()
        if not result:
            return None
        if tenant_id is not None and result.get('tenant_id') != tenant_id:
            return None
        return result['id_persona']
    
    @staticmethod
    def _preparar_transaccion(conn):
        """Prepara la conexión para una transacción."""
        original_autocommit = getattr(conn, 'autocommit', None)
        if original_autocommit is not None and original_autocommit:
            conn.autocommit = False
        if hasattr(conn, 'in_transaction') and conn.in_transaction:
            conn.rollback()
        conn.start_transaction()
        return original_autocommit
    
    @staticmethod
    def _actualizar_persona_en_bd(cursor, usuario, id_persona):
        """Actualiza los datos de la persona en la BD."""
        sql_persona = """
            UPDATE personas SET
                id_rol = %s,
                primer_nombre = %s,
                segundo_nombre = %s,
                primer_apellido = %s,
                segundo_apellido = %s,
                email = %s,
                telefono = %s,
                cargo_id = %s
            WHERE id = %s
        """
        values_persona = (
            usuario.persona.id_rol,
            usuario.persona.primer_nombre,
            usuario.persona.segundo_nombre,
            usuario.persona.primer_apellido,
            usuario.persona.segundo_apellido,
            usuario.persona.email,
            usuario.persona.telefono,
            usuario.persona.cargo_id,
            id_persona
        )
        cursor.execute(sql_persona, values_persona)
    
    @staticmethod
    def _actualizar_usuario_en_bd(cursor, usuario, id, tenant_id):
        """Actualiza los datos del usuario en la BD."""
        sql_usuario = """
            UPDATE usuarios SET
                id_rol = %s,
                estado = %s
            WHERE id = %s
        """
        params_usuario = (usuario.id_rol, usuario.estado.value, id)
        if tenant_id is not None:
            sql_usuario += UsuarioService.SQL_AND_TENANT_ID
            params_usuario = params_usuario + (tenant_id,)
        cursor.execute(sql_usuario, params_usuario)
    
    @staticmethod
    def _actualizar_contrasena_en_bd(cursor, usuario, id, tenant_id):
        """Actualiza la contraseña del usuario en la BD si es necesario."""
        if not usuario.contrasena:
            return
        sql_actualizar_contrasena = """
            UPDATE usuarios SET
                contrasena = %s
            WHERE id = %s
        """
        params_contrasena = (usuario.contrasena, id)
        if tenant_id is not None:
            sql_actualizar_contrasena += UsuarioService.SQL_AND_TENANT_ID
            params_contrasena = params_contrasena + (tenant_id,)
        cursor.execute(sql_actualizar_contrasena, params_contrasena)
    
    @staticmethod
    def actualizar_usuario_completo(id: int, usuario: Usuario, tenant_id_override: Optional[int] = None) -> bool:
        """
        Actualizar usuario completo con validación de tenant.
        
        Args:
            id: ID del usuario
            usuario: Objeto Usuario con los datos actualizados
            tenant_id_override: Si se proporciona, valida que el usuario pertenezca a este tenant
        """
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            tenant_id = tenant_id_override if tenant_id_override is not None else UsuarioService._obtener_tenant_id()
            id_persona = UsuarioService._validar_usuario_para_actualizacion(cursor, id, tenant_id)
            if id_persona is None:
                return False

            try:
                original_autocommit = UsuarioService._preparar_transaccion(conn)
                UsuarioService._actualizar_persona_en_bd(cursor, usuario, id_persona)
                UsuarioService._actualizar_usuario_en_bd(cursor, usuario, id, tenant_id)
                UsuarioService._actualizar_contrasena_en_bd(cursor, usuario, id, tenant_id)
                conn.commit()
                return True

            except Exception as e:
                conn.rollback()
                raise e
            finally:
                if 'original_autocommit' in locals() and original_autocommit is not None:
                    try:
                        conn.autocommit = original_autocommit
                    except Exception:
                        pass

        except Exception as e:
            print(f"Error al actualizar usuario completo: {e}")
            return False
        finally:
            if 'conn' in locals():
                try:
                    conn.close()
                except Exception:
                    pass


    @staticmethod
    def buscar_por_email(email: str) -> Optional[Usuario]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            sql = """
                SELECT u.*, p.*, r.rol as rol_nombre,
                       c.id as cargo_id_db, c.nombre_cargo, c.descripcion as cargo_descripcion 
                FROM usuarios u
                INNER JOIN personas p ON u.id_persona = p.id
                LEFT JOIN roles r ON u.id_rol = r.id
                LEFT JOIN cargos c ON p.cargo_id = c.id
                WHERE p.email = %s AND u.estado = 'activo'
            """
            cursor.execute(sql, (email,))

            result = cursor.fetchone()
            if result:
                # Crear rol
                rol = None
                if result.get('rol_nombre'):
                    rol = Rol(
                        id=result['id_rol'],
                        nombre_rol=result['rol_nombre']
                    )

                # Crear cargo
                cargo = None
                if result.get('cargo_id_db'):
                    cargo = Cargo(
                        id=result['cargo_id_db'],
                        nombre_cargo=result.get('nombre_cargo', ''),
                        descripcion=result.get('cargo_descripcion')
                    )

                # Crear persona - IMPORTANTE: tenant_id está en personas, no en usuarios
                persona = Persona(
                    id=result['id_persona'],
                    id_rol=result['id_rol'],
                    primer_nombre=result['primer_nombre'],
                    segundo_nombre=result['segundo_nombre'],
                    primer_apellido=result['primer_apellido'],
                    segundo_apellido=result['segundo_apellido'],
                    email=result['email'],
                    telefono=result['telefono'],
                    fecha_creacion=result['fecha_creacion'],
                    cargo_id=result.get('cargo_id'),
                    cargo=cargo
                )

                # Obtener tenant_id desde personas (campo p.tenant_id)
                tenant_id_persona = result.get('tenant_id')  # Este viene de personas p.*
                
                # Crear usuario
                usuario = Usuario(
                    id=result['id'],
                    id_persona=result['id_persona'],
                    id_rol=result['id_rol'],
                    contrasena=result.get('contrasena'),
                    estado=EstadoUsuario(result['estado']),
                    persona=persona,
                    rol=rol,
                    tenant_id=tenant_id_persona  # tenant_id viene de personas, no de usuarios
                )
                
                print(f"[BUSCAR_POR_EMAIL] Usuario encontrado: id={usuario.id}, persona_id={usuario.id_persona}, tenant_id={tenant_id_persona}")

                return usuario
            return None

        except Exception as e:
            print(f"Error al buscar usuario por email: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def _cargar_tenant_id_si_falta(usuario):
        """Carga tenant_id desde BD si falta en el usuario."""
        if hasattr(usuario, 'tenant_id') and usuario.tenant_id is not None:
            return
        try:
            conn = get_connection()
            if not conn:
                return
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT tenant_id FROM personas WHERE id = %s", (usuario.id_persona,))
            result = cursor.fetchone()
            if result and result.get('tenant_id') is not None:
                usuario.tenant_id = result['tenant_id']
                print(f"[AUTENTICACION] tenant_id cargado desde personas para usuario {usuario.id} (persona_id={usuario.id_persona}): {usuario.tenant_id}")
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"[AUTENTICACION] Error obteniendo tenant_id desde personas: {e}")

    # Remover método buscar_por_documento ya que no existen campos tipo_documento y numero_documento en la nueva BD

    @staticmethod
    def autenticar_usuario(email: str, password: str) -> Optional[Usuario]:
        try:
            # Buscar usuario por email en la base de datos
            usuario = UsuarioService.buscar_por_email(email)
            if usuario and usuario.check_password(password) and usuario.estado == EstadoUsuario.ACTIVO:
                # Cargar información del rol
                if usuario.id_rol:
                    rol = UsuarioService.obtener_rol(usuario.id_rol)
                    usuario.rol = rol
                
                UsuarioService._cargar_tenant_id_si_falta(usuario)
                
                return usuario
            return None

        except Exception as e:
            print(f"Error en autenticación: {e}")
            return None

    # Remover método actualizar_last_login ya que no existe el campo last_login en la nueva BD
