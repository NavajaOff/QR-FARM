# Servicio Usuario
from typing import List, Optional, Tuple
from datetime import datetime
from ..database.db import get_connection
from ..models.usuario import Usuario, Persona, Rol, EstadoUsuario

class UsuarioService:
    # Constantes para mensajes y queries
    EMAIL_DUPLICADO_MSG = "El email ya está registrado"
    QUERY_PERSONA_ID = "SELECT id_persona FROM usuarios WHERE id = %s"
    @staticmethod
    def _determinar_si_es_super_admin():
        """Determina si el usuario actual es super admin."""
        from ..utils.tenant import get_current_tenant_id
        try:
            current_tenant_id = get_current_tenant_id()
            return current_tenant_id is None
        except Exception:
            return False

    @staticmethod
    def _construir_condiciones_sql(incluir_inactivos, tenant_id, excluir_super_admin):
        """Construye las condiciones SQL para la consulta."""
        conditions = []
        params = []
        if not incluir_inactivos:
            conditions.append("u.estado = 'activo'")
        if tenant_id is not None:
            conditions.append("u.tenant_id = %s")
            params.append(tenant_id)
        if excluir_super_admin:
            conditions.append("(r.rol IS NULL OR LOWER(TRIM(r.rol)) != 'super_admin')")
        return conditions, params

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
        
        persona = Persona(
            id=result['id_persona'],
            id_rol=result['id_rol'],
            primer_nombre=result['primer_nombre'],
            segundo_nombre=result['segundo_nombre'],
            primer_apellido=result['primer_apellido'],
            segundo_apellido=result['segundo_apellido'],
            email=result['email'],
            telefono=result['telefono'],
            fecha_creacion=result['fecha_creacion']
        )
        
        return Usuario(
            id=result['id'],
            id_persona=result['id_persona'],
            id_rol=result['id_rol'],
            contrasena=result.get('contrasena'),
            estado=EstadoUsuario(result['estado']),
            persona=persona,
            rol=rol,
            tenant_id=result.get('tenant_id')
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
                segundo_apellido, email, telefono, fecha_creacion, tenant_id
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, NOW(), %s
            )
        """
        values_persona = (
            persona.id_rol, persona.primer_nombre, persona.segundo_nombre,
            persona.primer_apellido, persona.segundo_apellido,
            persona.email, persona.telefono, tenant_id
        )
        cursor.execute(sql_persona, values_persona)
        return cursor.lastrowid

    @staticmethod
    def _insertar_usuario(cursor, id_persona, usuario, tenant_id):
        """Inserta el usuario en la base de datos."""
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
                        telefono = %s
                    WHERE id = %s
                """
                
                values_persona = (
                    persona.id_rol, persona.primer_nombre, persona.segundo_nombre,
                    persona.primer_apellido, persona.segundo_apellido, 
                    persona.email, persona.telefono, id_persona
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
    def eliminar_usuario(id: int) -> Tuple[bool, str]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Verificar que el usuario existe y obtener id_persona
            cursor.execute(UsuarioService.QUERY_PERSONA_ID, (id,))
            result = cursor.fetchone()
            if not result:
                return False, "Usuario no encontrado"
                
            id_persona = result['id_persona']
            
            try:
                # Iniciar transacción
                conn.start_transaction()
                
                # Eliminar usuario
                cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
                
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
            if 'conn' in locals():
                conn.close()
    @staticmethod
    def registrar_usuario(persona: Persona, usuario: Usuario) -> Tuple[Optional[Usuario], str]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            # DEBUG: Verificar estado de la conexión
            print(f"DEBUG - Conexión obtenida: {conn}")
            print(f"DEBUG - Autocommit: {conn.autocommit}")

            # BLOQUEO: No permitir crear super_admin desde el registro público
            if persona.id_rol or usuario.id_rol:
                rol_id = persona.id_rol or usuario.id_rol
                cursor.execute("SELECT rol FROM roles WHERE id = %s", (rol_id,))
                rol = cursor.fetchone()
                if rol and rol.get('rol') == 'super_admin':
                    return None, "No se puede crear usuarios super_admin desde el registro público."

            # Verificar si el email ya existe
            cursor.execute("SELECT id FROM personas WHERE email = %s", (persona.email,))
            if cursor.fetchone():
                return None, UsuarioService.EMAIL_DUPLICADO_MSG

            try:
                if hasattr(conn, 'in_transaction') and conn.in_transaction:
                    conn.rollback()

                conn.start_transaction()

                # Obtener tenant_id del contexto (para tenant_admin creando usuarios)
                from ..utils.tenant import get_current_tenant_id
                tenant_id_contexto = get_current_tenant_id()

                # Insertar persona con tenant_id
                sql_persona = """
                    INSERT INTO personas (
                        id_rol, primer_nombre, segundo_nombre, primer_apellido,
                        segundo_apellido, email, telefono, fecha_creacion, tenant_id
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, NOW(), %s
                    )
                """

                values_persona = (
                    persona.id_rol, persona.primer_nombre, persona.segundo_nombre,
                    persona.primer_apellido, persona.segundo_apellido,
                    persona.email, persona.telefono, tenant_id_contexto
                )

                cursor.execute(sql_persona, values_persona)
                id_persona = cursor.lastrowid

                # Luego crear el usuario con tenant_id
                sql_usuario = """
                    INSERT INTO usuarios (
                        id_persona, id_rol, contrasena, estado, tenant_id
                    ) VALUES (
                        %s, %s, %s, %s, %s
                    )
                """

                values_usuario = (
                    id_persona, usuario.id_rol or 1, usuario.contrasena,
                    usuario.estado.value, tenant_id_contexto
                )

                cursor.execute(sql_usuario, values_usuario)

                # Commit de la transacción
                conn.commit()

                usuario.id = cursor.lastrowid
                usuario.id_persona = id_persona
                usuario.tenant_id = tenant_id_contexto
                persona.id = id_persona
                usuario.persona = persona

                return usuario, "Usuario registrado exitosamente"

            except Exception as e:
                # Rollback en caso de error
                conn.rollback()
                raise e

        except Exception as e:
            print(f"Error al registrar usuario: {e}")
            return None, str(e)
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def obtener_usuario(id: int, incluir_inactivos: bool = False) -> Optional[Usuario]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            sql = """
                SELECT u.*, p.*, r.rol as rol_nombre FROM usuarios u
                INNER JOIN personas p ON u.id_persona = p.id
                LEFT JOIN roles r ON u.id_rol = r.id
                WHERE u.id = %s
            """
            params = (id,)

            if not incluir_inactivos:
                sql += " AND u.estado = 'activo'"

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
                    fecha_creacion=result['fecha_creacion']
                )

                # Crear usuario
                usuario = Usuario(
                    id=result['id'],
                    id_persona=result['id_persona'],
                    id_rol=result['id_rol'],
                    contrasena=result['contrasena'],
                    estado=EstadoUsuario(result['estado']),
                    persona=persona,
                    rol=rol,
                    tenant_id=result.get('tenant_id')
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
    def obtener_todos_usuarios(incluir_inactivos: bool = False, tenant_id: Optional[int] = None, excluir_super_admin: bool = False) -> List[Usuario]:
        """
        Obtener todos los usuarios con filtrado automático de super admin para usuarios no privilegiados.

        Args:
            incluir_inactivos: Incluir usuarios inactivos
            tenant_id: Filtrar por tenant específico (None para super admin)
            excluir_super_admin: Forzar exclusión de super admin (siempre True para no super admin)
        """
        print(f"[USUARIO_SERVICE] obtener_todos_usuarios called with incluir_inactivos={incluir_inactivos}, tenant_id={tenant_id}, excluir_super_admin={excluir_super_admin}")

        es_super_admin_actual = UsuarioService._determinar_si_es_super_admin()
        print(f"[USUARIO_SERVICE] Usuario actual es super_admin: {es_super_admin_actual}")

        if not es_super_admin_actual:
            excluir_super_admin = True
            print("[USUARIO_SERVICE] Usuario no es super_admin, forzando excluir_super_admin=True")

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            sql = """
                SELECT u.*, p.*, r.rol as rol_nombre
                FROM usuarios u
                INNER JOIN personas p ON u.id_persona = p.id
                LEFT JOIN roles r ON u.id_rol = r.id
            """

            conditions, params = UsuarioService._construir_condiciones_sql(incluir_inactivos, tenant_id, excluir_super_admin)
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)

            print(f"[USUARIO_SERVICE] SQL: {sql}, params: {params}")
            print(f"[USUARIO_SERVICE] Condiciones aplicadas: tenant_id={tenant_id}, excluir_super_admin={excluir_super_admin}")
            cursor.execute(sql, params)
            results = cursor.fetchall()
            print(f"[USUARIO_SERVICE] Resultados obtenidos: {len(results)} usuarios")

            usuarios = []
            for result in results:
                usuario = UsuarioService._crear_usuario_desde_resultado(result)
                if usuario:
                    usuarios.append(usuario)
                    print(f"[USUARIO_SERVICE] Usuario agregado: id={usuario.id}, email={usuario.persona.email}, rol={result.get('rol_nombre')}, tenant_id={usuario.tenant_id}")

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
    def actualizar_usuario_completo(id: int, usuario: Usuario) -> bool:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            # Verificar que el usuario existe y obtener id_persona
            cursor.execute(UsuarioService.QUERY_PERSONA_ID, (id,))
            result = cursor.fetchone()
            if not result:
                return False

            id_persona = result['id_persona']

            try:
                original_autocommit = getattr(conn, 'autocommit', None)
                if original_autocommit is not None and original_autocommit:
                    conn.autocommit = False

                if hasattr(conn, 'in_transaction') and conn.in_transaction:
                    conn.rollback()

                # Iniciar transacción
                conn.start_transaction()

                # Actualizar persona
                sql_persona = """
                    UPDATE personas SET
                        id_rol = %s,
                        primer_nombre = %s,
                        segundo_nombre = %s,
                        primer_apellido = %s,
                        segundo_apellido = %s,
                        email = %s,
                        telefono = %s
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
                    id_persona
                )

                cursor.execute(sql_persona, values_persona)

                # Actualizar usuario
                sql_usuario = """
                    UPDATE usuarios SET
                        id_rol = %s,
                        estado = %s
                    WHERE id = %s
                """

                values_usuario = (usuario.id_rol, usuario.estado.value, id)
                cursor.execute(sql_usuario, values_usuario)

                # Si hay nueva contraseña, actualizarla
                if usuario.contrasena:
                    sql_actualizar_contrasena = """
                        UPDATE usuarios SET
                            contrasena = %s
                        WHERE id = %s
                    """
                    cursor.execute(sql_actualizar_contrasena, (usuario.contrasena, id))

                # Commit de la transacción
                conn.commit()

                return True

            except Exception as e:
                # Rollback en caso de error
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
    def eliminar_usuario(id: int) -> bool:
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Cambiar estado a inactivo
            sql = "UPDATE usuarios SET estado = 'inactivo' WHERE id = %s"
            cursor.execute(sql, (id,))
            conn.commit()

            return cursor.rowcount > 0

        except Exception as e:
            print(f"Error al eliminar usuario: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def buscar_por_email(email: str) -> Optional[Usuario]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            sql = """
                SELECT u.*, p.*, r.rol as rol_nombre FROM usuarios u
                INNER JOIN personas p ON u.id_persona = p.id
                LEFT JOIN roles r ON u.id_rol = r.id
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
                    fecha_creacion=result['fecha_creacion']
                )

                # Crear usuario
                usuario = Usuario(
                    id=result['id'],
                    id_persona=result['id_persona'],
                    id_rol=result['id_rol'],
                    contrasena=result.get('contrasena'),
                    estado=EstadoUsuario(result['estado']),
                    persona=persona,
                    rol=rol
                )

                return usuario
            return None

        except Exception as e:
            print(f"Error al buscar usuario por email: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

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
                return usuario
            return None

        except Exception as e:
            print(f"Error en autenticación: {e}")
            return None

    # Remover método actualizar_last_login ya que no existe el campo last_login en la nueva BD
