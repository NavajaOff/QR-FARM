"""Módulo de conexión a la base de datos."""
import os
from typing import Dict, Any, Generator, Optional
from contextlib import contextmanager
import logging
import mysql.connector
from passlib.hash import bcrypt
from mysql.connector import Error
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import MySQLCursor

# Configurar el registrador de eventos
registrador = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def _require_env(nombre_variable: str) -> str:
    """Obtiene una variable de entorno obligatoria."""
    valor = os.getenv(nombre_variable)
    if valor is None:
        raise ValueError(f"Variable de entorno obligatoria no configurada: {nombre_variable}")
    return valor


def _require_int_env(nombre_variable: str) -> int:
    """Obtiene una variable de entorno entera obligatoria."""
    valor = _require_env(nombre_variable)
    try:
        return int(valor)
    except ValueError as error:
        raise ValueError(f"La variable de entorno {nombre_variable} debe ser un número entero válido") from error


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
                'host': _require_env('DB_HOST'),
                'user': _require_env('DB_USER'),
                'password': _require_env('DB_PASSWORD'),
                'database': _require_env('DB_NAME'),
                'port': _require_int_env('DB_PORT'),
                'use_unicode': True,
                'charset': 'utf8mb4',
                'ssl_disabled': True
            }
            # Log de configuración DB para debug
            print(f"Configuración DB cargada: host={self.configuracion['host']}, user={self.configuracion['user']}, database={self.configuracion['database']}, port={self.configuracion['port']}")
            # Probar conexión
            self._obtener_conexion()
            registrador.info("Conexión a la base de datos inicializada correctamente")
        except (Error, ValueError) as e:
            registrador.error(f"Error al inicializar la conexión a la base de datos: {e}")
            raise ErrorBaseDatos(f"Error de inicialización de base de datos: {e}")

    def _obtener_conexion(self) -> MySQLConnection:
        """Obtener una conexión a la base de datos."""
        try:
            # Siempre crear una nueva conexión para evitar problemas de estado
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
            cursor = conexion.cursor(dictionary=True)  # Siempre usar dictionary=True
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
    # Nota: El super_admin se crea automáticamente desde variables de entorno
    # en app.py mediante inicializar_super_admin()
    return db

# ✅ FUNCIÓN ACTUALIZADA
def get_connection():
    """Obtener una conexión activa a la base de datos."""
    try:
        if db is None:
            print("Advertencia: Base de datos no disponible, retornando None")
            return None
        conexion = db._obtener_conexion()
        return conexion
    except Exception as e:
        print(f"Advertencia: Base de datos no disponible, retornando None: {e}")
        return None

# Crear instancia global (solo si no hay errores de conexión)
try:
    db = ConexionBaseDatos()
except ErrorBaseDatos:
    print("Advertencia: No se pudo conectar a la base de datos. El sistema funcionará en modo limitado.")
    db = None

# Alias para mantener compatibilidad con código existente
def get_cursor(dictionary=True):
    """Alias para db.obtener_cursor para compatibilidad."""
    if db is None:
        raise ErrorBaseDatos("Base de datos no disponible")
    return db.obtener_cursor(dictionary)

# Agregar método get_cursor a la clase para compatibilidad
if db is not None:
    ConexionBaseDatos.get_cursor = get_cursor
