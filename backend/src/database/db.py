"""Módulo de conexión a la base de                'host': os.getenv('DB_HOST', 'localhost'),
                'user': os.getenv('DB_USER', 'root'),
                'password': os.getenv('DB_PASSWORD', ''),
                'database': os.getenv('DB_NAME', 'gestion_ganadera'),
                'port': int(os.getenv('DB_PORT', '3306'),s."""
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
                'database': os.getenv('DB_NAME', 'qr_farm'),
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
            if not self._conexion or not self._conexion.is_connected():
                self._conexion = mysql.connector.connect(**self.configuracion)
            return self._conexion
        except Error as e:
            registrador.error(f"Error al obtener la conexión a la base de datos: {e}")
            raise ErrorBaseDatos(f"Error al obtener la conexión: {e}")

    @contextmanager
    def obtener_cursor(self, como_diccionario: bool = True) -> Generator[MySQLCursor, None, None]:
        """Obtener un cursor de base de datos con gestión automática de la conexión.

        Args:
            como_diccionario (bool): Si es True, devuelve los resultados como diccionarios

        Yields:
            MySQLCursor: Objeto cursor de la base de datos

        Raises:
            ErrorBaseDatos: Si hay un error en las operaciones de base de datos
        """
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
        """Ejecutar una consulta en la base de datos y devolver los resultados.

        Args:
            consulta (str): Consulta SQL a ejecutar
            parametros (tuple, opcional): Parámetros de la consulta

        Returns:
            Dict[str, Any]: Resultados de la consulta con metadatos

        Raises:
            ErrorBaseDatos: Si hay un error en la ejecución de la consulta
        """
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
    return ConexionBaseDatos()

def get_connection():
    """Obtener una conexión a la base de datos."""
    db = ConexionBaseDatos()
    return db._conexion

# Crear instancia global
db = ConexionBaseDatos()
