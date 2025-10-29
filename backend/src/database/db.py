"""Módulo de conexión a la base de datos."""
import os
from typing import Dict, Any, Generator, Optional
from contextlib import contextmanager
import logging
import mysql.connector
from mysql.connector import Error, connect
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import MySQLCursor

# Configurar el registrador de eventos
registrador = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ErrorBaseDatos(Exception):
    """Excepción personalizada para errores de base de datos."""
    pass

# Alias para mantener compatibilidad con código existente
DatabaseError = ErrorBaseDatos

class ConexionBaseDatos:
    """Clase para gestionar la conexión a la base de datos."""
    _instancia = None
    _conexion = None
    
    def __new__(cls):
        """Crear una instancia única (patrón Singleton)."""
        if cls._instancia is None:
            cls._instancia = super(ConexionBaseDatos, cls).__new__(cls)
            cls._instancia._inicializar_conexion()
        return cls._instancia

    def _inicializar_conexion(self) -> None:
        """Inicializar la configuración de la conexión a la base de datos."""
        try:
            self.configuracion = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'user': os.getenv('DB_USER', 'root'),
                'password': os.getenv('DB_PASSWORD', ''),
                'database': os.getenv('DB_NAME', 'gestion_ganadera'),
                'port': int(os.getenv('DB_PORT', '3306')),
                'use_unicode': True,
                'charset': 'utf8mb4'
            }
            # Probar conexión
            self._obtener_conexion()
            registrador.info("Conexión a la base de datos inicializada correctamente")
        except Error as e:
            registrador.error(f"Error al inicializar la conexión a la base de datos: {e}")
            raise ErrorBaseDatos(f"Error de inicialización de base de datos: {e}")

    def _obtener_conexion(self) -> MySQLConnection:
        """Obtener una conexión a la base de datos."""
        try:
            # Si no hay conexión o está cerrada, se crea una nueva
            if not self._conexion or not self._conexion.is_connected():
                self._conexion = mysql.connector.connect(**self.configuracion)
            else:
                # Se verifica la conexión y se reconecta automáticamente si está caída
                try:
                    self._conexion.ping(reconnect=True, attempts=3, delay=2)
                except Exception as e:
                    registrador.warning(f"Reconectando a la base de datos: {e}")
                    self._conexion = mysql.connector.connect(**self.configuracion)

            return self._conexion

        except Error as e:
            registrador.error(f"Error al obtener la conexión a la base de datos: {e}")
            raise ErrorBaseDatos(f"Error al obtener la conexión: {e}")

    @contextmanager
    def obtener_cursor(self, como_diccionario: bool = True) -> Generator[MySQLCursor, None, None]:
        """Obtener un cursor de base de datos con gestión automática de la conexión."""
        conexion = None
        cursor = None
        try:
            conexion = self._obtener_conexion()
            cursor = conexion.cursor(dictionary=como_diccionario)
            yield cursor
            conexion.commit()
        except Error as e:
            if conexion:
                conexion.rollback()
            registrador.error(f"Error de base de datos: {e}")
            raise ErrorBaseDatos(f"Error en la operación de base de datos: {e}")
        finally:
            if cursor:
                cursor.close()

    def ejecutar_consulta(self, consulta: str, parametros: Optional[tuple] = None) -> Dict[str, Any]:
        """Ejecutar una consulta en la base de datos y devolver los resultados."""
        with self.obtener_cursor(como_diccionario=True) as cursor:
            try:
                cursor.execute(consulta, parametros)
                resultado = {
                    'datos': cursor.fetchall() if cursor.description else None,
                    'filas_afectadas': cursor.rowcount,
                    'id_insertado': cursor.lastrowid if hasattr(cursor, 'lastrowid') else None
                }
                return resultado
            except Error as e:
                registrador.error(f"Error en la ejecución de la consulta: {e}\nConsulta: {consulta}\nParámetros: {parametros}")
                raise ErrorBaseDatos(f"Error en la ejecución de la consulta: {e}")

    def cerrar(self):
        """Cerrar la conexión a la base de datos."""
        if self._conexion and self._conexion.is_connected():
            self._conexion.close()
            registrador.info("Conexión a la base de datos cerrada")

def init_db():
    """Inicializar la base de datos."""
    db = ConexionBaseDatos()
    # Crear usuario admin por defecto si no existe
    crear_usuario_admin_por_defecto()
    return db

def crear_usuario_admin_por_defecto():
    """Crear usuario administrador por defecto si no existe."""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Usar la base de datos gestion_ganadera
        cursor.execute('USE gestion_ganadera')

        # Verificar si ya existe el usuario admin
        cursor.execute('SELECT COUNT(*) as count FROM usuarios u JOIN personas p ON u.id_persona = p.id WHERE p.email = %s', ('admin@qrfarm.com',))
        result = cursor.fetchone()

        if result['count'] == 0:
            # Verificar si existe el rol admin
            cursor.execute('SELECT id FROM roles WHERE rol = %s', ('admin',))
            rol_result = cursor.fetchone()

            if not rol_result:
                # Crear rol admin
                cursor.execute('INSERT INTO roles (rol, descripcion) VALUES (%s, %s)', ('admin', 'Administrador del sistema'))
                rol_id = cursor.lastrowid
            else:
                rol_id = rol_result['id']

            # Crear persona admin
            cursor.execute('''INSERT INTO personas (id_rol, primer_nombre, segundo_nombre, primer_apellido, segundo_apellido, email, telefono, fecha_creacion)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())''',
                         (rol_id, 'Admin', 'Sistema', 'QR', 'Farm', 'admin@qrfarm.com', '1234567890'))

            persona_id = cursor.lastrowid

            # Crear usuario admin
            cursor.execute('''INSERT INTO usuarios (id_persona, id_rol, contrasena, estado)
                            VALUES (%s, %s, %s, %s)''',
                         (persona_id, rol_id, 'admin123', 'activo'))

            conn.commit()

            registrador.info("Usuario administrador creado exitosamente")
            registrador.info("Email: admin@qrfarm.com")
            registrador.info("Contraseña: admin123")
        else:
            registrador.info("Usuario administrador ya existe")

        cursor.close()
        conn.close()

    except Exception as e:
        registrador.error(f"Error al crear usuario administrador por defecto: {e}")

# ✅ FUNCIÓN ACTUALIZADA
def get_connection():
    """Obtener una conexión activa a la base de datos."""
    try:
        db = ConexionBaseDatos()
        conexion = db._obtener_conexion()
        return conexion
    except Exception as e:
        registrador.error(f"No se pudo obtener conexión a la base de datos: {e}")
        return None

# Crear instancia global
db = ConexionBaseDatos()
