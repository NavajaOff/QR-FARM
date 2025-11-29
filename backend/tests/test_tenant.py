"""Tests para tenant.py."""
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


def test_obtener_rol_nombre_with_nombre_rol(app_context):
    """Test _obtener_rol_nombre con nombre_rol."""
    from src.utils.tenant import _obtener_rol_nombre
    
    mock_usuario = Mock()
    mock_rol = Mock()
    mock_rol.nombre_rol = 'admin'
    mock_usuario.rol = mock_rol

    result = _obtener_rol_nombre(mock_usuario)

    assert result == 'admin'


def test_obtener_rol_nombre_with_rol(app_context):
    """Test _obtener_rol_nombre con rol."""
    from src.utils.tenant import _obtener_rol_nombre
    
    mock_usuario = Mock()
    mock_rol = Mock()
    mock_rol.rol = 'usuario'
    mock_usuario.rol = mock_rol

    result = _obtener_rol_nombre(mock_usuario)

    assert result == 'usuario'


def test_obtener_rol_nombre_none(app_context):
    """Test _obtener_rol_nombre cuando no hay rol."""
    from src.utils.tenant import _obtener_rol_nombre
    
    mock_usuario = Mock()
    mock_usuario.rol = None

    result = _obtener_rol_nombre(mock_usuario)

    assert result is None


def test_obtener_tenant_desde_query_param_super_admin(app_context):
    """Test _obtener_tenant_desde_query_param con super admin."""
    from src.utils.tenant import _obtener_tenant_desde_query_param
    
    with patch('src.utils.tenant.request') as mock_request, \
         patch('src.utils.tenant.g') as mock_g:
        mock_request.args = {'tenant_id': '1'}
        mock_user = Mock()
        mock_rol = Mock()
        mock_rol.nombre_rol = 'super_admin'
        mock_user.rol = mock_rol
        mock_g.current_user = mock_user

        result = _obtener_tenant_desde_query_param()

        assert result == 1


def test_obtener_tenant_desde_query_param_no_super_admin(app_context):
    """Test _obtener_tenant_desde_query_param sin ser super admin."""
    from src.utils.tenant import _obtener_tenant_desde_query_param
    
    with patch('src.utils.tenant.request') as mock_request, \
         patch('src.utils.tenant.g') as mock_g:
        mock_request.args = {'tenant_id': '1'}
        mock_user = Mock()
        mock_rol = Mock()
        mock_rol.nombre_rol = 'usuario'
        mock_user.rol = mock_rol
        mock_g.current_user = mock_user

        result = _obtener_tenant_desde_query_param()

        assert result is None


def test_obtener_tenant_del_usuario_success(app_context):
    """Test _obtener_tenant_del_usuario exitoso."""
    from src.utils.tenant import _obtener_tenant_del_usuario
    
    with patch('src.utils.tenant.g') as mock_g:
        mock_user = Mock()
        mock_user.tenant_id = 1
        mock_rol = Mock()
        mock_rol.nombre_rol = 'usuario'
        mock_user.rol = mock_rol
        mock_g.current_user = mock_user

        result = _obtener_tenant_del_usuario()

        assert result == 1


def test_obtener_tenant_del_usuario_super_admin(app_context):
    """Test _obtener_tenant_del_usuario con super admin."""
    from src.utils.tenant import _obtener_tenant_del_usuario
    
    with patch('src.utils.tenant.g') as mock_g:
        mock_user = Mock()
        mock_rol = Mock()
        mock_rol.nombre_rol = 'super_admin'
        mock_user.rol = mock_rol
        mock_g.current_user = mock_user

        result = _obtener_tenant_del_usuario()

        assert result is None


def test_get_current_tenant_id_from_query(app_context):
    """Test get_current_tenant_id desde query param."""
    from src.utils.tenant import get_current_tenant_id
    
    with patch('src.utils.tenant.request') as mock_request, \
         patch('src.utils.tenant.g') as mock_g:
        mock_request.args = {'tenant_id': '1'}
        mock_user = Mock()
        mock_rol = Mock()
        mock_rol.nombre_rol = 'super_admin'
        mock_user.rol = mock_rol
        mock_g.current_user = mock_user

        result = get_current_tenant_id(allow_query_param=True)

        assert result == 1


def test_get_current_tenant_id_from_user(app_context):
    """Test get_current_tenant_id desde usuario."""
    from src.utils.tenant import get_current_tenant_id
    
    with patch('src.utils.tenant.request') as mock_request, \
         patch('src.utils.tenant.g') as mock_g:
        mock_request.args = {}
        mock_user = Mock()
        mock_user.tenant_id = 1
        mock_rol = Mock()
        mock_rol.nombre_rol = 'usuario'
        mock_user.rol = mock_rol
        mock_g.current_user = mock_user

        result = get_current_tenant_id()

        assert result == 1


def test_get_current_tenant_id_from_g(app_context):
    """Test get_current_tenant_id desde g.tenant_id."""
    from src.utils.tenant import get_current_tenant_id
    
    with patch('src.utils.tenant.request') as mock_request, \
         patch('src.utils.tenant.g') as mock_g:
        mock_request.args = {}
        mock_user = Mock()
        mock_user.rol = None
        mock_g.current_user = mock_user
        mock_g.tenant_id = 1

        result = get_current_tenant_id()

        assert result == 1


def test_es_super_admin_usuario_true(app_context):
    """Test _es_super_admin_usuario cuando es super admin."""
    from src.utils.tenant import _es_super_admin_usuario
    
    with patch('src.utils.tenant.g') as mock_g:
        mock_user = Mock()
        mock_rol = Mock()
        mock_rol.nombre_rol = 'super_admin'
        mock_user.rol = mock_rol
        mock_g.current_user = mock_user

        result = _es_super_admin_usuario()

        assert result is True


def test_es_super_admin_usuario_false(app_context):
    """Test _es_super_admin_usuario cuando no es super admin."""
    from src.utils.tenant import _es_super_admin_usuario
    
    with patch('src.utils.tenant.g') as mock_g:
        mock_user = Mock()
        mock_rol = Mock()
        mock_rol.nombre_rol = 'usuario'
        mock_user.rol = mock_rol
        mock_g.current_user = mock_user

        result = _es_super_admin_usuario()

        assert result is False


def test_tenant_required_success(app_context):
    """Test tenant_required decorator exitoso."""
    from src.utils.tenant import tenant_required
    
    @tenant_required
    def test_function():
        return "success"
    
    with patch('src.utils.tenant.get_current_tenant_id', return_value=1):
        result = test_function()
        assert result == "success"


def test_tenant_required_no_tenant_super_admin(app_context):
    """Test tenant_required sin tenant para super admin."""
    from src.utils.tenant import tenant_required
    
    @tenant_required
    def test_function():
        return "success"
    
    with patch('src.utils.tenant.get_current_tenant_id', return_value=None), \
         patch('src.utils.tenant._es_super_admin_usuario', return_value=True), \
         patch('src.utils.tenant.request') as mock_request, \
         patch('src.utils.tenant.jsonify') as mock_jsonify:
        mock_request.args = {}
        mock_jsonify.return_value = ({'status': 'error'}, 403)

        result = test_function()

        assert result[1] == 403


def test_tenant_required_no_tenant_normal_user(app_context):
    """Test tenant_required sin tenant para usuario normal."""
    from src.utils.tenant import tenant_required
    
    @tenant_required
    def test_function():
        return "success"
    
    with patch('src.utils.tenant.get_current_tenant_id', return_value=None), \
         patch('src.utils.tenant._es_super_admin_usuario', return_value=False), \
         patch('src.utils.tenant.jsonify') as mock_jsonify:
        mock_jsonify.return_value = ({'status': 'error'}, 403)

        result = test_function()

        assert result[1] == 403


def test_super_admin_required_success(app_context):
    """Test super_admin_required decorator exitoso."""
    from src.utils.tenant import super_admin_required
    
    @super_admin_required
    def test_function():
        return "success"
    
    with patch('src.utils.tenant.g') as mock_g:
        mock_user = Mock()
        mock_rol = Mock()
        mock_rol.nombre_rol = 'super_admin'
        mock_user.rol = mock_rol
        mock_g.current_user = mock_user

        result = test_function()

        assert result == "success"


def test_super_admin_required_no_auth(app_context):
    """Test super_admin_required sin autenticación."""
    from src.utils.tenant import super_admin_required
    
    @super_admin_required
    def test_function():
        return "success"
    
    with patch('src.utils.tenant.g') as mock_g, \
         patch('src.utils.tenant.jsonify') as mock_jsonify:
        mock_g.current_user = None
        mock_jsonify.return_value = ({'status': 'error'}, 401)

        result = test_function()

        assert result[1] == 401


def test_super_admin_required_not_super_admin(app_context):
    """Test super_admin_required sin ser super admin."""
    from src.utils.tenant import super_admin_required
    
    @super_admin_required
    def test_function():
        return "success"
    
    with patch('src.utils.tenant.g') as mock_g, \
         patch('src.utils.tenant.jsonify') as mock_jsonify:
        mock_user = Mock()
        mock_rol = Mock()
        mock_rol.nombre_rol = 'usuario'
        mock_user.rol = mock_rol
        mock_g.current_user = mock_user
        mock_jsonify.return_value = ({'status': 'error'}, 403)

        result = test_function()

        assert result[1] == 403

