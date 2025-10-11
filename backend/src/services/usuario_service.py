# Servicio Usuario
from typing import List, Optional, Tuple
from datetime import datetime
from ..database.db import get_connection
from ..models.usuario import Usuario, Persona, Rol, EstadoUsuario

class UsuarioService:
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
    def crear_usuario(persona: Persona, usuario: Usuario) -> Tuple[Optional[Usuario], str]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Verificar si el email ya existe
            cursor.execute("SELECT id FROM personas WHERE email = %s", (persona.email,))
            if cursor.fetchone():
                return None, "El email ya está registrado"

            # Verificar si el username ya existe
            if usuario.username:
                cursor.execute("SELECT id FROM usuarios WHERE username = %s", (usuario.username,))
                if cursor.fetchone():
                    return None, "El nombre de usuario ya está registrado"

            try:
                # Iniciar transacción
                conn.start_transaction()

                # Insertar persona
                sql_persona = """
                    INSERT INTO personas (
                        id_rol, primer_nombre, segundo_nombre, primer_apellido,
                        segundo_apellido, email, telefono, created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
                    )
                """
                
                values_persona = (
                    persona.id_rol, persona.primer_nombre, persona.segundo_nombre,
                    persona.primer_apellido, persona.segundo_apellido, 
                    persona.email, persona.telefono
                )
                
                cursor.execute(sql_persona, values_persona)
                id_persona = cursor.lastrowid
                
                # Luego crear el usuario
                sql_usuario = """
                    INSERT INTO usuarios (
                        id_persona, id_rol, username, password_hash,
                        estado, created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, NOW(), NOW()
                    )
                """
                
                values_usuario = (
                    id_persona, usuario.id_rol, usuario.username,
                    usuario.password_hash, usuario.estado.value
                )
                
                cursor.execute(sql_usuario, values_usuario)
                
                # Commit de la transacción
                conn.commit()
                
                usuario.id = cursor.lastrowid
                usuario.id_persona = id_persona
                persona.id = id_persona
                usuario.persona = persona
                
                return usuario, "Usuario creado exitosamente"

            except Exception as e:
                # Rollback en caso de error
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
            cursor.execute("SELECT id_persona FROM usuarios WHERE id = %s", (id,))
            result = cursor.fetchone()
            if not result:
                return None, "Usuario no encontrado"
                
            id_persona = result['id_persona']
            
            # Verificar si el email ya existe para otro usuario
            cursor.execute("SELECT id FROM personas WHERE email = %s AND id != %s", 
                         (persona.email, id_persona))
            if cursor.fetchone():
                return None, "El email ya está registrado"

            # Verificar si el username ya existe para otro usuario
            if usuario.username:
                cursor.execute("SELECT id FROM usuarios WHERE username = %s AND id != %s", 
                             (usuario.username, id))
                if cursor.fetchone():
                    return None, "El nombre de usuario ya está registrado"

            try:
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
                        telefono = %s,
                        updated_at = NOW()
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
                
                # Si hay nueva contraseña, actualizarla
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
                    nombre=row['rol_nombre'],
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
                    nombre=result['rol_nombre'],
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
                    nombre=result['rol_nombre'],
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
            cursor.execute("SELECT id_persona FROM usuarios WHERE id = %s", (id,))
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
    def crear_usuario(persona: Persona, usuario: Usuario) -> Tuple[Optional[Usuario], str]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Primero crear la persona
            sql_persona = """
                INSERT INTO personas (
                    id_rol, primer_nombre, segundo_nombre, primer_apellido,
                    segundo_apellido, email, telefono, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
                )
            """
            
            # Verificar si el email ya existe
            cursor.execute("SELECT id FROM personas WHERE email = %s", (persona.email,))
            if cursor.fetchone():
                return None, "El email ya está registrado"

            # Verificar si el username ya existe
            if usuario.username:
                cursor.execute("SELECT id FROM usuarios WHERE username = %s", (usuario.username,))
                if cursor.fetchone():
                    return None, "El nombre de usuario ya está registrado"

            # Insertar persona
            values_persona = (
                persona.id_rol, persona.primer_nombre, persona.segundo_nombre,
                persona.primer_apellido, persona.segundo_apellido, 
                persona.email, persona.telefono
            )
            
            cursor.execute(sql_persona, values_persona)
            conn.commit()
            
            id_persona = cursor.lastrowid
            
            # Luego crear el usuario
            sql_usuario = """
                INSERT INTO usuarios (
                    id_persona, id_rol, username, password_hash,
                    estado, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, NOW(), NOW()
                )
            """
            
            values_usuario = (
                id_persona, usuario.id_rol, usuario.username,
                usuario.password_hash, usuario.estado.value
            )
            
            cursor.execute(sql, values)
            conn.commit()
            
            usuario.id = cursor.lastrowid
            usuario.fecha_registro = datetime.now()
            return usuario
            
        except Exception as e:
            print(f"Error al crear usuario: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def obtener_usuario(id: int) -> Optional[Usuario]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            sql = "SELECT * FROM usuarios WHERE id = %s AND activo = TRUE"
            cursor.execute(sql, (id,))
            
            result = cursor.fetchone()
            if result:
                return Usuario.from_dict(result)
            return None
            
        except Exception as e:
            print(f"Error al obtener usuario: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def obtener_todos_usuarios() -> List[Usuario]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            sql = "SELECT * FROM usuarios WHERE activo = TRUE"
            cursor.execute(sql)
            results = cursor.fetchall()
            
            return [Usuario.from_dict(result) for result in results]
            
        except Exception as e:
            print(f"Error al obtener usuarios: {e}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def actualizar_usuario(id: int, usuario: Usuario) -> bool:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            sql = """
                UPDATE usuarios SET 
                    primer_nombre = %s,
                    segundo_nombre = %s,
                    primer_apellido = %s,
                    segundo_apellido = %s,
                    direccion = %s,
                    telefono = %s,
                    email = %s,
                    pais = %s,
                    tipo_documento = %s,
                    numero_documento = %s,
                    observaciones = %s
                WHERE id = %s AND activo = TRUE
            """
            
            values = (
                usuario.primer_nombre, usuario.segundo_nombre,
                usuario.primer_apellido, usuario.segundo_apellido,
                usuario.direccion, usuario.telefono, usuario.email,
                usuario.pais, usuario.tipo_documento,
                usuario.numero_documento, usuario.observaciones,
                id
            )
            
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
    def eliminar_usuario(id: int) -> bool:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Soft delete - marcar como inactivo en lugar de eliminar
            sql = "UPDATE usuarios SET activo = FALSE WHERE id = %s"
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
            
            sql = "SELECT * FROM usuarios WHERE email = %s AND activo = TRUE"
            cursor.execute(sql, (email,))
            
            result = cursor.fetchone()
            if result:
                return Usuario.from_dict(result)
            return None
            
        except Exception as e:
            print(f"Error al buscar usuario por email: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def buscar_por_documento(tipo_documento: str, numero_documento: str) -> Optional[Usuario]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            sql = """
                SELECT * FROM usuarios 
                WHERE tipo_documento = %s 
                AND numero_documento = %s 
                AND activo = TRUE
            """
            cursor.execute(sql, (tipo_documento, numero_documento))
            
            result = cursor.fetchone()
            if result:
                return Usuario.from_dict(result)
            return None
            
        except Exception as e:
            print(f"Error al buscar usuario por documento: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def autenticar_usuario(email: str, password: str) -> Optional[Usuario]:
        try:
            usuario = UsuarioService.buscar_por_email(email)
            if usuario and usuario.check_password(password):
                return usuario
            return None
            
        except Exception as e:
            print(f"Error en autenticación: {e}")
            return None
