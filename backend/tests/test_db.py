"""Tests para el módulo de conexión a la base de datos."""
import os
import pytest
from unittest.mock import patch, MagicMock, Mock
import mysql.connector
from mysql.connector import Error

from src.database.db import (
    _require_env,
    _require_int_env,
    ErrorBaseDatos,
    DatabaseError,
    ConexionBaseDatos,
    init_db,
    get_connection,
    get_cursor
)


class TestRequireEnv:
    """Tests para _require_env."""

    def test_require_env_with_existing_variable(self):
        """Debería retornar el valor de la variable de entorno existente."""
        with patch.dict(os.environ, {'TEST_VAR': 'test_value'}):
            result = _require_env('TEST_VAR')
            assert result == 'test_value'

    def test_require_env_with_missing_variable(self):
        """Debería lanzar ValueError si la variable no existe."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match='Variable de entorno obligatoria no configurada'):
                _require_env('MISSING_VAR')


class TestRequireIntEnv:
    """Tests para _require_int_env."""

    def test_require_int_env_with_valid_integer(self):
        """Debería retornar un entero válido."""
        with patch.dict(os.environ, {'TEST_INT': '123'}):
            result = _require_int_env('TEST_INT')
            assert result == 123
            assert isinstance(result, int)

    def test_require_int_env_with_invalid_integer(self):
        """Debería lanzar ValueError si el valor no es un entero válido."""
        with patch.dict(os.environ, {'TEST_INT': 'not_a_number'}):
            with pytest.raises(ValueError, match='debe ser un número entero válido'):
                _require_int_env('TEST_INT')

    def test_require_int_env_with_missing_variable(self):
        """Debería lanzar ValueError si la variable no existe."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match='Variable de entorno obligatoria no configurada'):
                _require_int_env('MISSING_VAR')


class TestErrorBaseDatos:
    """Tests para ErrorBaseDatos."""

    def test_error_base_datos_is_exception(self):
        """ErrorBaseDatos debería ser una subclase de Exception."""
        assert issubclass(ErrorBaseDatos, Exception)

    def test_error_base_datos_can_be_raised(self):
        """Debería poder lanzarse ErrorBaseDatos."""
        with pytest.raises(ErrorBaseDatos):
            raise ErrorBaseDatos('Test error')

    def test_database_error_alias(self):
        """DatabaseError debería ser un alias de ErrorBaseDatos."""
        assert DatabaseError is ErrorBaseDatos


class TestConexionBaseDatos:
    """Tests para ConexionBaseDatos."""

    def setup_method(self):
        """Resetear la instancia singleton antes de cada test."""
        ConexionBaseDatos._instancia = None
        ConexionBaseDatos._conexion = None

    @patch('src.database.db.mysql.connector.connect')
    @patch.dict(os.environ, {
        'DB_HOST': 'localhost',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password',
        'DB_NAME': 'test_db',
        'DB_PORT': '3306'
    })
    def test_singleton_pattern(self, mock_connect):
        """Debería retornar la misma instancia (patrón Singleton)."""
        mock_connect.return_value = MagicMock()
        instance1 = ConexionBaseDatos()
        instance2 = ConexionBaseDatos()
        assert instance1 is instance2

    @patch('src.database.db.mysql.connector.connect')
    @patch.dict(os.environ, {
        'DB_HOST': 'localhost',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password',
        'DB_NAME': 'test_db',
        'DB_PORT': '3306'
    })
    def test_inicializar_conexion_success(self, mock_connect):
        """Debería inicializar la conexión correctamente."""
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        db = ConexionBaseDatos()
        assert db.configuracion is not None
        assert db.configuracion['host'] == 'localhost'
        assert db.configuracion['user'] == 'test_user'
        assert db.configuracion['database'] == 'test_db'
        assert db.configuracion['port'] == 3306

    @patch.dict(os.environ, {}, clear=True)
    def test_inicializar_conexion_missing_env(self):
        """Debería lanzar ErrorBaseDatos si faltan variables de entorno."""
        ConexionBaseDatos._instancia = None
        with pytest.raises(ErrorBaseDatos, match='Error de inicialización'):
            ConexionBaseDatos()

    @patch('src.database.db.mysql.connector.connect')
    @patch.dict(os.environ, {
        'DB_HOST': 'localhost',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password',
        'DB_NAME': 'test_db',
        'DB_PORT': '3306'
    })
    def test_obtener_conexion_success(self, mock_connect):
        """Debería obtener una conexión exitosamente."""
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        db = ConexionBaseDatos()
        conexion = db._obtener_conexion()
        assert conexion == mock_connection
        mock_connect.assert_called()

    @patch('src.database.db.mysql.connector.connect')
    @patch.dict(os.environ, {
        'DB_HOST': 'localhost',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password',
        'DB_NAME': 'test_db',
        'DB_PORT': '3306'
    })
    def test_obtener_conexion_error(self, mock_connect):
        """Debería lanzar ErrorBaseDatos si falla la conexión."""
        # Primero crear la instancia con conexión exitosa
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        db = ConexionBaseDatos()
        # Luego hacer que falle en la siguiente llamada
        mock_connect.side_effect = Error('Connection failed')
        with pytest.raises(ErrorBaseDatos, match='Error al obtener la conexión'):
            db._obtener_conexion()

    @patch('src.database.db.mysql.connector.connect')
    @patch.dict(os.environ, {
        'DB_HOST': 'localhost',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password',
        'DB_NAME': 'test_db',
        'DB_PORT': '3306'
    })
    def test_obtener_cursor_success(self, mock_connect):
        """Debería obtener un cursor exitosamente."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        db = ConexionBaseDatos()
        with db.obtener_cursor() as cursor:
            assert cursor == mock_cursor
        mock_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()

    @patch('src.database.db.mysql.connector.connect')
    @patch.dict(os.environ, {
        'DB_HOST': 'localhost',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password',
        'DB_NAME': 'test_db',
        'DB_PORT': '3306'
    })
    def test_obtener_cursor_with_error(self, mock_connect):
        """Debería hacer rollback y lanzar ErrorBaseDatos si hay un error."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Error('Query failed')
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        db = ConexionBaseDatos()
        with pytest.raises(ErrorBaseDatos, match='Error en la operación de base de datos'):
            with db.obtener_cursor() as cursor:
                cursor.execute('SELECT 1')
        mock_connection.rollback.assert_called_once()
        mock_cursor.close.assert_called_once()

    @patch('src.database.db.mysql.connector.connect')
    @patch.dict(os.environ, {
        'DB_HOST': 'localhost',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password',
        'DB_NAME': 'test_db',
        'DB_PORT': '3306'
    })
    def test_ejecutar_consulta_success(self, mock_connect):
        """Debería ejecutar una consulta exitosamente."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.description = [('id',), ('name',)]
        mock_cursor.fetchall.return_value = [{'id': 1, 'name': 'Test'}]
        mock_cursor.rowcount = 1
        mock_cursor.lastrowid = 123
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        db = ConexionBaseDatos()
        result = db.ejecutar_consulta('SELECT * FROM test', ())
        assert result['datos'] == [{'id': 1, 'name': 'Test'}]
        assert result['filas_afectadas'] == 1
        assert result['id_insertado'] == 123

    @patch('src.database.db.mysql.connector.connect')
    @patch.dict(os.environ, {
        'DB_HOST': 'localhost',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password',
        'DB_NAME': 'test_db',
        'DB_PORT': '3306'
    })
    def test_ejecutar_consulta_with_no_description(self, mock_connect):
        """Debería manejar consultas sin descripción (ej: INSERT sin RETURNING)."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.description = None
        mock_cursor.rowcount = 1
        mock_cursor.lastrowid = None
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        db = ConexionBaseDatos()
        result = db.ejecutar_consulta('INSERT INTO test VALUES (1)')
        assert result['datos'] is None
        assert result['filas_afectadas'] == 1

    @patch('src.database.db.mysql.connector.connect')
    @patch.dict(os.environ, {
        'DB_HOST': 'localhost',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password',
        'DB_NAME': 'test_db',
        'DB_PORT': '3306'
    })
    def test_ejecutar_consulta_with_error(self, mock_connect):
        """Debería lanzar ErrorBaseDatos si la consulta falla."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Error('Query failed')
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        db = ConexionBaseDatos()
        with pytest.raises(ErrorBaseDatos, match='Error en la ejecución de la consulta'):
            db.ejecutar_consulta('INVALID QUERY')

    @patch('src.database.db.mysql.connector.connect')
    @patch.dict(os.environ, {
        'DB_HOST': 'localhost',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password',
        'DB_NAME': 'test_db',
        'DB_PORT': '3306'
    })
    def test_cerrar_conexion(self, mock_connect):
        """Debería cerrar la conexión correctamente."""
        mock_connection = MagicMock()
        mock_connection.is_connected.return_value = True
        mock_connect.return_value = mock_connection
        db = ConexionBaseDatos()
        db.cerrar()
        mock_connection.close.assert_called_once()

    @patch('src.database.db.mysql.connector.connect')
    @patch.dict(os.environ, {
        'DB_HOST': 'localhost',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password',
        'DB_NAME': 'test_db',
        'DB_PORT': '3306'
    })
    def test_cerrar_conexion_when_not_connected(self, mock_connect):
        """No debería intentar cerrar si no está conectado."""
        mock_connection = MagicMock()
        mock_connection.is_connected.return_value = False
        mock_connect.return_value = mock_connection
        db = ConexionBaseDatos()
        db.cerrar()
        mock_connection.close.assert_not_called()

    @patch('src.database.db.mysql.connector.connect')
    @patch.dict(os.environ, {
        'DB_HOST': 'localhost',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password',
        'DB_NAME': 'test_db',
        'DB_PORT': '3306'
    })
    def test_cerrar_conexion_when_none(self, mock_connect):
        """No debería fallar si _conexion es None."""
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        db = ConexionBaseDatos()
        db._conexion = None
        db.cerrar()  # No debería lanzar error


class TestInitDb:
    """Tests para init_db."""

    def setup_method(self):
        """Resetear la instancia singleton antes de cada test."""
        ConexionBaseDatos._instancia = None
        ConexionBaseDatos._conexion = None

    @patch('src.database.db.mysql.connector.connect')
    @patch.dict(os.environ, {
        'DB_HOST': 'localhost',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password',
        'DB_NAME': 'test_db',
        'DB_PORT': '3306'
    })
    def test_init_db_returns_instance(self, mock_connect):
        """Debería retornar una instancia de ConexionBaseDatos."""
        mock_connect.return_value = MagicMock()
        db = init_db()
        assert isinstance(db, ConexionBaseDatos)


class TestGetConnection:
    """Tests para get_connection."""

    def setup_method(self):
        """Resetear la instancia singleton antes de cada test."""
        ConexionBaseDatos._instancia = None
        ConexionBaseDatos._conexion = None

    @patch('src.database.db.mysql.connector.connect')
    @patch.dict(os.environ, {
        'DB_HOST': 'localhost',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password',
        'DB_NAME': 'test_db',
        'DB_PORT': '3306'
    })
    def test_get_connection_success(self, mock_connect):
        """Debería retornar una conexión cuando db está disponible."""
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        # Crear una instancia de db para el test
        db = ConexionBaseDatos()
        with patch('src.database.db.db', db):
            conexion = get_connection()
            assert conexion == mock_connection

    def test_get_connection_when_db_is_none(self):
        """Debería retornar None cuando db es None."""
        with patch('src.database.db.db', None):
            conexion = get_connection()
            assert conexion is None

    @patch('src.database.db.mysql.connector.connect')
    @patch.dict(os.environ, {
        'DB_HOST': 'localhost',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password',
        'DB_NAME': 'test_db',
        'DB_PORT': '3306'
    })
    def test_get_connection_with_exception(self, mock_connect):
        """Debería retornar None si hay una excepción."""
        # Primero crear la instancia con conexión exitosa
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        db = ConexionBaseDatos()
        with patch('src.database.db.db', db):
            with patch.object(db, '_obtener_conexion', side_effect=Exception('Connection error')):
                conexion = get_connection()
                assert conexion is None


class TestGetCursor:
    """Tests para get_cursor."""

    def setup_method(self):
        """Resetear la instancia singleton antes de cada test."""
        ConexionBaseDatos._instancia = None
        ConexionBaseDatos._conexion = None

    @patch('src.database.db.mysql.connector.connect')
    @patch.dict(os.environ, {
        'DB_HOST': 'localhost',
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password',
        'DB_NAME': 'test_db',
        'DB_PORT': '3306'
    })
    def test_get_cursor_success(self, mock_connect):
        """Debería retornar un cursor cuando db está disponible."""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        db = ConexionBaseDatos()
        with patch('src.database.db.db', db):
            cursor = get_cursor()
            assert cursor is not None

    def test_get_cursor_when_db_is_none(self):
        """Debería lanzar ErrorBaseDatos cuando db es None."""
        with patch('src.database.db.db', None):
            with pytest.raises(ErrorBaseDatos, match='Base de datos no disponible'):
                get_cursor()

