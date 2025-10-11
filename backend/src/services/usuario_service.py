# Servicio Usuario
from typing import List, Optional
from datetime import datetime
from ..database.db import get_connection
from ..models.usuario import Usuario

class UsuarioService:
    @staticmethod
    def crear_usuario(usuario: Usuario) -> Optional[Usuario]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            sql = """
                INSERT INTO usuarios (
                    primer_nombre, segundo_nombre, primer_apellido, segundo_apellido,
                    direccion, telefono, email, password_hash, pais,
                    tipo_documento, numero_documento, observaciones,
                    fecha_registro, activo
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), TRUE
                )
            """
            
            values = (
                usuario.primer_nombre, usuario.segundo_nombre,
                usuario.primer_apellido, usuario.segundo_apellido,
                usuario.direccion, usuario.telefono, usuario.email,
                usuario.password_hash, usuario.pais, usuario.tipo_documento,
                usuario.numero_documento, usuario.observaciones
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
