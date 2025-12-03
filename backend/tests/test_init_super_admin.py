"""Tests para init_super_admin."""
import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path


def test_obtener_posibles_rutas_env():
    """Test _obtener_posibles_rutas_env."""
    from src.utils.init_super_admin import _obtener_posibles_rutas_env
    
    rutas = _obtener_posibles_rutas_env()
    assert len(rutas) == 2
    assert all(isinstance(r, Path) for r in rutas)


def test_verificar_variables_env():
    """Test _verificar_variables_env."""
    from src.utils.init_super_admin import _verificar_variables_env
    
    contenido = "ROOT_SUPER_ADMIN_EMAIL=test@example.com\nROOT_SUPER_ADMIN_PASSWORD=pass123"
    tiene_email, tiene_password = _verificar_variables_env(contenido)
    assert tiene_email is True
    assert tiene_password is True


def test_procesar_archivo_env(monkeypatch):
    """Test _procesar_archivo_env."""
    from src.utils.init_super_admin import _procesar_archivo_env
    
    env_path = Path("/tmp/test.env")
    contenido = "ROOT_SUPER_ADMIN_EMAIL=test@example.com\nROOT_SUPER_ADMIN_PASSWORD=pass123"
    
    with patch('builtins.open', mock_open(read_data=contenido)):
        _procesar_archivo_env(env_path)
    # No debería lanzar excepción


def test_cargar_desde_rutas_posibles(monkeypatch):
    """Test _cargar_desde_rutas_posibles."""
    from src.utils.init_super_admin import _cargar_desde_rutas_posibles
    
    with patch('src.utils.init_super_admin.Path.exists', return_value=True), \
         patch('src.utils.init_super_admin._procesar_archivo_env'), \
         patch('src.utils.init_super_admin.load_dotenv', return_value=True):
        result = _cargar_desde_rutas_posibles()
        assert result is True


def test_buscar_env_hacia_arriba(monkeypatch):
    """Test _buscar_env_hacia_arriba."""
    from src.utils.init_super_admin import _buscar_env_hacia_arriba
    
    with patch('src.utils.init_super_admin.Path.exists', return_value=True), \
         patch('src.utils.init_super_admin.load_dotenv', return_value=True):
        result = _buscar_env_hacia_arriba()
        assert result is True


@patch('src.utils.init_super_admin.get_connection')
def test_obtener_rol_super_admin_id_success(mock_get_connection):
    """Test obtener_rol_super_admin_id exitoso."""
    from src.utils.init_super_admin import obtener_rol_super_admin_id
    
    mock_conn = Mock()
    mock_cursor = Mock(dictionary=True)
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {'id': 3}

    result = obtener_rol_super_admin_id()

    assert result == 3


@patch('src.utils.init_super_admin.get_connection')
def test_obtener_rol_super_admin_id_not_found(mock_get_connection):
    """Test obtener_rol_super_admin_id cuando no existe."""
    from src.utils.init_super_admin import obtener_rol_super_admin_id
    
    mock_conn = Mock()
    mock_cursor = Mock(dictionary=True)
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None

    result = obtener_rol_super_admin_id()

    assert result is None


@patch('src.utils.init_super_admin.get_connection')
def test_existe_super_admin_true(mock_get_connection):
    """Test existe_super_admin cuando existe."""
    from src.utils.init_super_admin import existe_super_admin
    
    mock_conn = Mock()
    mock_cursor = Mock(dictionary=True)
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {'count': 1}

    result = existe_super_admin('test@example.com')

    assert result is True


@patch('src.utils.init_super_admin.get_connection')
def test_existe_super_admin_false(mock_get_connection):
    """Test existe_super_admin cuando no existe."""
    from src.utils.init_super_admin import existe_super_admin
    
    mock_conn = Mock()
    mock_cursor = Mock(dictionary=True)
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {'count': 0}

    result = existe_super_admin('test@example.com')

    assert result is False


@patch('src.utils.init_super_admin.get_connection')
def test_crear_super_admin_desde_env_success(mock_get_connection, monkeypatch):
    """Test crear_super_admin_desde_env exitoso."""
    from src.utils.init_super_admin import crear_super_admin_desde_env
    
    monkeypatch.setenv('ROOT_SUPER_ADMIN_EMAIL', 'test@example.com')
    monkeypatch.setenv('ROOT_SUPER_ADMIN_PASSWORD', 'password123')
    monkeypatch.setenv('ROOT_SUPER_ADMIN_NOMBRE', 'Super Admin')

    mock_conn = Mock()
    mock_cursor = Mock(dictionary=True)
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.lastrowid = 1

    with patch('src.utils.init_super_admin._cargar_env', return_value=True), \
         patch('src.utils.init_super_admin.existe_super_admin', return_value=False), \
         patch('src.utils.init_super_admin.obtener_rol_super_admin_id', return_value=3), \
         patch('src.utils.init_super_admin.bcrypt') as mock_bcrypt, \
         patch('src.utils.init_super_admin.hashlib') as mock_hashlib:
        mock_bcrypt.hash.return_value = 'hashed_password'
        mock_hashlib.sha256.return_value.hexdigest.return_value = 'sha256_hash'

        exito, mensaje = crear_super_admin_desde_env()

        assert exito is True


@patch('src.utils.init_super_admin.get_connection')
def test_crear_super_admin_desde_env_missing_vars(mock_get_connection, monkeypatch):
    """Test crear_super_admin_desde_env sin variables de entorno."""
    from src.utils.init_super_admin import crear_super_admin_desde_env
    
    monkeypatch.delenv('ROOT_SUPER_ADMIN_EMAIL', raising=False)
    monkeypatch.delenv('ROOT_SUPER_ADMIN_PASSWORD', raising=False)

    with patch('src.utils.init_super_admin._cargar_env', return_value=True):
        exito, mensaje = crear_super_admin_desde_env()

        assert exito is False
        assert 'no configuradas' in mensaje


@patch('src.utils.init_super_admin.crear_super_admin_desde_env')
def test_inicializar_super_admin_success(mock_crear):
    """Test inicializar_super_admin exitoso."""
    from src.utils.init_super_admin import inicializar_super_admin
    
    mock_crear.return_value = (True, "Super admin creado")

    result = inicializar_super_admin()

    assert result is True


@patch('src.utils.init_super_admin.crear_super_admin_desde_env')
def test_inicializar_super_admin_failure(mock_crear):
    """Test inicializar_super_admin con fallo."""
    from src.utils.init_super_admin import inicializar_super_admin
    
    mock_crear.return_value = (False, "Error")

    result = inicializar_super_admin()

    assert result is False


@patch('src.utils.init_super_admin.get_connection')
def test_crear_super_admin_desde_env_bcrypt_error(mock_get_connection, monkeypatch):
    """Test crear_super_admin_desde_env cuando bcrypt falla y usa fallback."""
    import hashlib
    from src.utils.init_super_admin import crear_super_admin_desde_env
    
    monkeypatch.setenv('ROOT_SUPER_ADMIN_EMAIL', 'test@example.com')
    monkeypatch.setenv('ROOT_SUPER_ADMIN_PASSWORD', 'password123')
    monkeypatch.setenv('ROOT_SUPER_ADMIN_NOMBRE', 'Super Admin')

    mock_conn = Mock()
    mock_cursor = Mock(dictionary=True)
    mock_get_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.lastrowid = 1

    with patch('src.utils.init_super_admin._cargar_env', return_value=True), \
         patch('src.utils.init_super_admin.existe_super_admin', return_value=False), \
         patch('src.utils.init_super_admin.obtener_rol_super_admin_id', return_value=3), \
         patch('src.utils.init_super_admin.bcrypt') as mock_bcrypt:
        # Simular error de bcrypt
        mock_bcrypt.hash.side_effect = AttributeError("module 'bcrypt' has no attribute 'about'")
        
        # Verificar que se llama a hashlib cuando bcrypt falla
        with patch('hashlib.sha256') as mock_sha256:
            mock_sha256_instance = Mock()
            mock_sha256_instance.hexdigest.return_value = 'sha256_hash'
            mock_sha256.return_value = mock_sha256_instance

            exito, mensaje = crear_super_admin_desde_env()

            # Debe usar el fallback de hashlib
            assert exito is True
            mock_sha256.assert_called_once()


@patch('src.utils.init_super_admin.get_connection')
def test_inicializar_super_admin_no_db(mock_get_connection):
    """Test inicializar_super_admin cuando la BD no está disponible."""
    from src.utils.init_super_admin import inicializar_super_admin
    
    mock_get_connection.return_value = None

    result = inicializar_super_admin()

    assert result is False

