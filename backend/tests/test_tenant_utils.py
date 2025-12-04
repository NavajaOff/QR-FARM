"""Tests para utilidades de tenant."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask, g, request


class TestTenantUtils:
    """Tests para utils/tenant.py."""

    @pytest.fixture
    def app(self):
        """Create Flask app for testing."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        return app

    @pytest.fixture
    def app_context(self, app):
        """Provide Flask application context for tests."""
        with app.app_context():
            yield

    def test_obtener_rol_nombre_with_nombre_rol(self, app, app_context):
        """Test _obtener_rol_nombre with nombre_rol attribute."""
        from src.utils.tenant import _obtener_rol_nombre

        class MockRol:
            def __init__(self):
                self.nombre_rol = 'admin'
        
        mock_usuario = Mock()
        mock_usuario.rol = MockRol()

        result = _obtener_rol_nombre(mock_usuario)

        assert result == 'admin'

    def test_obtener_rol_nombre_with_rol_attribute(self, app, app_context):
        """Test _obtener_rol_nombre with rol attribute."""
        from src.utils.tenant import _obtener_rol_nombre

        class MockRol:
            def __init__(self):
                self.rol = 'tenant_admin'
        
        mock_usuario = Mock()
        mock_usuario.rol = MockRol()

        result = _obtener_rol_nombre(mock_usuario)

        assert result == 'tenant_admin'

    def test_obtener_rol_nombre_no_rol(self, app, app_context):
        """Test _obtener_rol_nombre without rol."""
        from src.utils.tenant import _obtener_rol_nombre

        mock_usuario = Mock()
        mock_usuario.rol = None

        result = _obtener_rol_nombre(mock_usuario)

        assert result is None

    def test_obtener_rol_nombre_no_rol_attribute(self, app, app_context):
        """Test _obtener_rol_nombre without rol attribute."""
        from src.utils.tenant import _obtener_rol_nombre

        mock_usuario = Mock()
        del mock_usuario.rol

        result = _obtener_rol_nombre(mock_usuario)

        assert result is None

    def test_obtener_tenant_desde_query_param_super_admin(self, app, app_context):
        """Test _obtener_tenant_desde_query_param with super admin."""
        from src.utils.tenant import _obtener_tenant_desde_query_param

        mock_usuario = Mock()
        mock_rol = Mock()
        mock_rol.nombre_rol = 'super_admin'
        mock_usuario.rol = mock_rol

        with app.test_request_context('/?tenant_id=123'):
            g.current_user = mock_usuario

            result = _obtener_tenant_desde_query_param()

            assert result == 123

    def test_obtener_tenant_desde_query_param_no_super_admin(self, app, app_context):
        """Test _obtener_tenant_desde_query_param with non super admin."""
        from src.utils.tenant import _obtener_tenant_desde_query_param

        mock_usuario = Mock()
        mock_rol = Mock()
        mock_rol.nombre_rol = 'admin'
        mock_usuario.rol = mock_rol

        with app.test_request_context('/?tenant_id=123'):
            g.current_user = mock_usuario

            result = _obtener_tenant_desde_query_param()

            assert result is None

    def test_obtener_tenant_desde_query_param_no_param(self, app, app_context):
        """Test _obtener_tenant_desde_query_param without param."""
        from src.utils.tenant import _obtener_tenant_desde_query_param

        mock_usuario = Mock()
        mock_rol = Mock()
        mock_rol.nombre_rol = 'super_admin'
        mock_usuario.rol = mock_rol

        with app.test_request_context('/'):
            g.current_user = mock_usuario

            result = _obtener_tenant_desde_query_param()

            assert result is None

    def test_obtener_tenant_desde_query_param_invalid_value(self, app, app_context):
        """Test _obtener_tenant_desde_query_param with invalid value."""
        from src.utils.tenant import _obtener_tenant_desde_query_param

        mock_usuario = Mock()
        mock_rol = Mock()
        mock_rol.nombre_rol = 'super_admin'
        mock_usuario.rol = mock_rol

        with app.test_request_context('/?tenant_id=invalid'):
            g.current_user = mock_usuario

            result = _obtener_tenant_desde_query_param()

            assert result is None

    def test_obtener_tenant_del_usuario_super_admin(self, app, app_context):
        """Test _obtener_tenant_del_usuario with super admin."""
        from src.utils.tenant import _obtener_tenant_del_usuario

        mock_usuario = Mock()
        mock_rol = Mock()
        mock_rol.nombre_rol = 'super_admin'
        mock_usuario.rol = mock_rol

        with app.app_context():
            g.current_user = mock_usuario

            result = _obtener_tenant_del_usuario()

            assert result is None

    def test_obtener_tenant_del_usuario_normal_user(self, app, app_context):
        """Test _obtener_tenant_del_usuario with normal user."""
        from src.utils.tenant import _obtener_tenant_del_usuario

        mock_usuario = Mock()
        mock_rol = Mock()
        mock_rol.nombre_rol = 'admin'
        mock_usuario.rol = mock_rol
        mock_usuario.tenant_id = 456

        with app.app_context():
            g.current_user = mock_usuario

            result = _obtener_tenant_del_usuario()

            assert result == 456

    def test_obtener_tenant_del_usuario_no_user(self, app, app_context):
        """Test _obtener_tenant_del_usuario without user."""
        from src.utils.tenant import _obtener_tenant_del_usuario

        with app.app_context():
            if hasattr(g, 'current_user'):
                delattr(g, 'current_user')

            result = _obtener_tenant_del_usuario()

            assert result is None

    def test_get_current_tenant_id_super_admin_with_query(self, app, app_context):
        """Test get_current_tenant_id for super admin with query param."""
        from src.utils.tenant import get_current_tenant_id

        mock_usuario = Mock()
        mock_rol = Mock()
        mock_rol.nombre_rol = 'super_admin'
        mock_usuario.rol = mock_rol

        with app.test_request_context('/?tenant_id=123'):
            g.current_user = mock_usuario

            result = get_current_tenant_id(allow_query_param=True, require_tenant=False)

            assert result == 123

    def test_get_current_tenant_id_super_admin_no_query(self, app, app_context):
        """Test get_current_tenant_id for super admin without query param."""
        from src.utils.tenant import get_current_tenant_id

        class MockRol:
            def __init__(self):
                self.nombre_rol = 'super_admin'

        mock_usuario = Mock()
        mock_usuario.rol = MockRol()

        with app.test_request_context('/'):
            g.current_user = mock_usuario

            result = get_current_tenant_id(allow_query_param=True, require_tenant=False)

            assert result is None

    def test_get_current_tenant_id_normal_user(self, app, app_context):
        """Test get_current_tenant_id for normal user."""
        from src.utils.tenant import get_current_tenant_id

        mock_usuario = Mock()
        mock_rol = Mock()
        mock_rol.nombre_rol = 'admin'
        mock_usuario.rol = mock_rol
        mock_usuario.tenant_id = 789

        with app.app_context():
            g.current_user = mock_usuario

            result = get_current_tenant_id(allow_query_param=True, require_tenant=False)

            assert result == 789

    def test_get_current_tenant_id_from_g(self, app, app_context):
        """Test get_current_tenant_id getting from g.tenant_id."""
        from src.utils.tenant import get_current_tenant_id

        mock_usuario = Mock()
        mock_rol = Mock()
        mock_rol.nombre_rol = 'admin'
        mock_usuario.rol = mock_rol
        # Ensure usuario doesn't have tenant_id so it falls back to g.tenant_id
        if hasattr(mock_usuario, 'tenant_id'):
            delattr(mock_usuario, 'tenant_id')

        with app.app_context():
            g.current_user = mock_usuario
            # Use setattr to ensure the value is set directly
            setattr(g, 'tenant_id', 999)

            result = get_current_tenant_id(allow_query_param=True, require_tenant=False)

            assert result == 999

    def test_es_super_admin_usuario_true(self, app, app_context):
        """Test _es_super_admin_usuario returns True."""
        from src.utils.tenant import _es_super_admin_usuario

        mock_usuario = Mock()
        mock_rol = Mock()
        mock_rol.nombre_rol = 'super_admin'
        mock_usuario.rol = mock_rol

        with app.app_context():
            g.current_user = mock_usuario

            result = _es_super_admin_usuario()

            assert result is True

    def test_es_super_admin_usuario_false(self, app, app_context):
        """Test _es_super_admin_usuario returns False."""
        from src.utils.tenant import _es_super_admin_usuario

        mock_usuario = Mock()
        mock_rol = Mock()
        mock_rol.nombre_rol = 'admin'
        mock_usuario.rol = mock_rol

        with app.app_context():
            g.current_user = mock_usuario

            result = _es_super_admin_usuario()

            assert result is False

    def test_es_super_admin_usuario_no_user(self, app, app_context):
        """Test _es_super_admin_usuario with no user."""
        from src.utils.tenant import _es_super_admin_usuario

        with app.app_context():
            if hasattr(g, 'current_user'):
                delattr(g, 'current_user')

            result = _es_super_admin_usuario()

            assert result is False

    def test_validar_tenant_super_admin_no_param(self, app, app_context):
        """Test _validar_tenant_super_admin without tenant_id param."""
        from src.utils.tenant import _validar_tenant_super_admin

        with app.test_request_context('/'):
            response, status_code = _validar_tenant_super_admin()

            assert status_code == 403
            assert response.get_json()['code'] == 'tenant_required_for_super_admin'

    def test_validar_tenant_super_admin_invalid(self, app, app_context):
        """Test _validar_tenant_super_admin with invalid tenant_id."""
        from src.utils.tenant import _validar_tenant_super_admin

        with app.test_request_context('/?tenant_id=invalid'):
            response, status_code = _validar_tenant_super_admin()

            assert status_code == 400
            assert response.get_json()['code'] == 'invalid_tenant_id'

    def test_validar_tenant_usuario_normal(self, app, app_context):
        """Test _validar_tenant_usuario_normal."""
        from src.utils.tenant import _validar_tenant_usuario_normal

        with app.app_context():
            response, status_code = _validar_tenant_usuario_normal()

            assert status_code == 403
            assert response.get_json()['code'] == 'tenant_required'

    def test_tenant_required_super_admin(self, app, app_context):
        """Test tenant_required decorator with super admin."""
        from src.utils.tenant import tenant_required

        mock_usuario = Mock()
        mock_rol = Mock()
        mock_rol.nombre_rol = 'super_admin'
        mock_usuario.rol = mock_rol

        @tenant_required
        def test_function():
            return 'success'

        with app.app_context():
            g.current_user = mock_usuario

            result = test_function()

            assert result == 'success'

    def test_tenant_required_normal_user_with_tenant(self, app, app_context):
        """Test tenant_required decorator with normal user having tenant."""
        from src.utils.tenant import tenant_required

        mock_usuario = Mock()
        mock_rol = Mock()
        mock_rol.nombre_rol = 'admin'
        mock_usuario.rol = mock_rol
        mock_usuario.tenant_id = 123

        @tenant_required
        def test_function():
            return 'success'

        with app.app_context():
            g.current_user = mock_usuario

            result = test_function()

            assert result == 'success'

    def test_tenant_required_normal_user_no_tenant(self, app, app_context):
        """Test tenant_required decorator with normal user without tenant."""
        from src.utils.tenant import tenant_required

        mock_usuario = Mock()
        mock_rol = Mock()
        mock_rol.nombre_rol = 'admin'
        mock_usuario.rol = mock_rol
        # Ensure usuario doesn't have tenant_id
        if hasattr(mock_usuario, 'tenant_id'):
            delattr(mock_usuario, 'tenant_id')

        @tenant_required
        def test_function():
            return 'success'

        with app.app_context():
            g.current_user = mock_usuario
            # Ensure g doesn't have tenant_id
            if hasattr(g, 'tenant_id'):
                delattr(g, 'tenant_id')

            result = test_function()

            # The decorator should return a tuple (response, status_code)
            assert isinstance(result, tuple)
            assert len(result) == 2
            response, status_code = result

            assert status_code == 403
            assert response.get_json()['code'] == 'tenant_required'

    def test_super_admin_required_no_user(self, app, app_context):
        """Test super_admin_required decorator with no user."""
        from src.utils.tenant import super_admin_required

        @super_admin_required
        def test_function():
            return 'success'

        with app.app_context():
            if hasattr(g, 'current_user'):
                delattr(g, 'current_user')

            response, status_code = test_function()

            assert status_code == 401
            assert response.get_json()['code'] == 'unauthorized'

    def test_super_admin_required_no_rol(self, app, app_context):
        """Test super_admin_required decorator with no rol."""
        from src.utils.tenant import super_admin_required

        mock_usuario = Mock()
        mock_usuario.rol = None

        @super_admin_required
        def test_function():
            return 'success'

        with app.app_context():
            g.current_user = mock_usuario

            response, status_code = test_function()

            assert status_code == 403
            assert response.get_json()['code'] == 'insufficient_permissions'

    def test_super_admin_required_not_super_admin(self, app, app_context):
        """Test super_admin_required decorator with non super admin."""
        from src.utils.tenant import super_admin_required

        mock_usuario = Mock()
        mock_rol = Mock()
        mock_rol.nombre_rol = 'admin'
        mock_usuario.rol = mock_rol

        @super_admin_required
        def test_function():
            return 'success'

        with app.app_context():
            g.current_user = mock_usuario

            response, status_code = test_function()

            assert status_code == 403
            assert response.get_json()['code'] == 'insufficient_permissions'

    def test_super_admin_required_success(self, app, app_context):
        """Test super_admin_required decorator success."""
        from src.utils.tenant import super_admin_required

        mock_usuario = Mock()
        mock_rol = Mock()
        mock_rol.nombre_rol = 'super_admin'
        mock_usuario.rol = mock_rol

        @super_admin_required
        def test_function():
            return 'success'

        with app.app_context():
            g.current_user = mock_usuario

            result = test_function()

            assert result == 'success'
