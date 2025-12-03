"""Tests para permissions.py."""
import pytest
from unittest.mock import Mock, patch
from flask import Flask, g


@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def app_context(app):
    """Provide Flask application context."""
    with app.app_context():
        yield


def test_validar_usuario_autenticado_success(app_context):
    """Test _validar_usuario_autenticado exitoso."""
    from src.utils.permissions import _validar_usuario_autenticado
    
    with patch('src.utils.permissions.g') as mock_g:
        mock_user = Mock()
        mock_g.current_user = mock_user

        usuario, error_response, error_status = _validar_usuario_autenticado()

        assert usuario == mock_user
        assert error_response is None


def test_validar_usuario_autenticado_failure(app_context):
    """Test _validar_usuario_autenticado sin usuario."""
    from src.utils.permissions import _validar_usuario_autenticado
    
    with patch('src.utils.permissions.g') as mock_g, \
         patch('src.utils.permissions.jsonify') as mock_jsonify:
        mock_g.current_user = None
        mock_jsonify.return_value = ({'status': 'error'}, 401)

        usuario, error_response, error_status = _validar_usuario_autenticado()

        assert usuario is None
        assert error_response is not None


def test_obtener_rol_usuario_with_nombre_rol(app_context):
    """Test _obtener_rol_usuario con nombre_rol."""
    from src.utils.permissions import _obtener_rol_usuario
    
    mock_usuario = Mock()
    mock_rol = Mock()
    mock_rol.nombre_rol = 'admin'
    mock_usuario.rol = mock_rol

    result = _obtener_rol_usuario(mock_usuario)

    assert result == 'admin'


def test_obtener_rol_usuario_with_rol(app_context):
    """Test _obtener_rol_usuario con rol."""
    from src.utils.permissions import _obtener_rol_usuario
    
    mock_usuario = Mock()
    mock_rol = Mock()
    # No tiene nombre_rol, solo tiene rol
    del mock_rol.nombre_rol
    mock_rol.rol = 'usuario'
    mock_usuario.rol = mock_rol

    result = _obtener_rol_usuario(mock_usuario)

    assert result == 'usuario'


def test_obtener_rol_usuario_none(app_context):
    """Test _obtener_rol_usuario cuando no hay rol."""
    from src.utils.permissions import _obtener_rol_usuario
    
    mock_usuario = Mock()
    mock_usuario.rol = None

    result = _obtener_rol_usuario(mock_usuario)

    assert result is None


def test_validar_permiso_super_admin_global_permission(app_context):
    """Test _validar_permiso con super admin para permisos globales."""
    from src.utils.permissions import _validar_permiso
    
    # Super admin puede gestionar tenants (permiso global)
    tiene_permiso, error_response = _validar_permiso('super_admin', 'gestionar_tenants')

    assert tiene_permiso is True
    assert error_response is None


def test_validar_permiso_super_admin_tenant_permission_blocked(app_context):
    """Test _validar_permiso con super admin para permisos de tenant (bloqueado)."""
    from src.utils.permissions import _validar_permiso
    
    # Super admin NO puede ver ganado (permiso de tenant)
    tiene_permiso, error_response = _validar_permiso('super_admin', 'ver_ganado')

    assert tiene_permiso is False
    assert error_response is not None


def test_validar_permiso_authorized(app_context):
    """Test _validar_permiso con permiso autorizado."""
    from src.utils.permissions import _validar_permiso
    
    tiene_permiso, error_response = _validar_permiso('usuario', 'ver_ganado')

    assert tiene_permiso is True
    assert error_response is None


def test_validar_permiso_unauthorized(app_context):
    """Test _validar_permiso sin permiso."""
    from src.utils.permissions import _validar_permiso
    
    tiene_permiso, error_response = _validar_permiso('usuario', 'gestionar_tenants')

    assert tiene_permiso is False
    assert error_response is not None
    # error_response es una tupla (response, status_code)
    assert error_response[1] == 403


def test_permission_required_success(app_context):
    """Test permission_required decorator exitoso."""
    from src.utils.permissions import permission_required
    
    @permission_required('ver_ganado')
    def test_function():
        return "success"
    
    with patch('src.utils.permissions._validar_usuario_autenticado') as mock_validar, \
         patch('src.utils.permissions._obtener_rol_usuario', return_value='usuario'), \
         patch('src.utils.permissions._validar_permiso', return_value=(True, None)):
        mock_user = Mock()
        mock_validar.return_value = (mock_user, None, None)

        result = test_function()

        assert result == "success"


def test_permission_required_no_auth(app_context):
    """Test permission_required sin autenticación."""
    from src.utils.permissions import permission_required
    
    @permission_required('ver_ganado')
    def test_function():
        return "success"
    
    with patch('src.utils.permissions._validar_usuario_autenticado') as mock_validar, \
         patch('src.utils.permissions.jsonify') as mock_jsonify:
        mock_jsonify.return_value = ({'status': 'error'}, 401)
        mock_validar.return_value = (None, {'status': 'error'}, 401)

        result = test_function()

        assert result[1] == 401


def test_permission_required_no_role(app_context):
    """Test permission_required sin rol."""
    from src.utils.permissions import permission_required
    
    @permission_required('ver_ganado')
    def test_function():
        return "success"
    
    with patch('src.utils.permissions._validar_usuario_autenticado') as mock_validar, \
         patch('src.utils.permissions._obtener_rol_usuario', return_value=None), \
         patch('src.utils.permissions.jsonify') as mock_jsonify:
        mock_user = Mock()
        mock_validar.return_value = (mock_user, None, None)
        mock_jsonify.return_value = ({'status': 'error'}, 403)

        result = test_function()

        assert result[1] == 403


def test_permission_required_insufficient_permissions(app_context):
    """Test permission_required con permisos insuficientes."""
    from src.utils.permissions import permission_required
    
    @permission_required('gestionar_tenants')
    def test_function():
        return "success"
    
    with patch('src.utils.permissions._validar_usuario_autenticado') as mock_validar, \
         patch('src.utils.permissions._obtener_rol_usuario', return_value='usuario'), \
         patch('src.utils.permissions._validar_permiso', return_value=(False, ({'status': 'error'}, 403))), \
         patch('src.utils.permissions.jsonify') as mock_jsonify:
        mock_user = Mock()
        mock_validar.return_value = (mock_user, None, None)
        mock_jsonify.return_value = ({'status': 'error'}, 403)

        result = test_function()

        assert result[1] == 403

