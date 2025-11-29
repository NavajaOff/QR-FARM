"""Tests para TenantController."""
import pytest
from unittest.mock import Mock, patch
from flask import Flask, g
from src.controllers.tenant_controller import TenantController


def _create_mock_super_admin():
    """Helper para crear un super admin mock."""
    mock_user = Mock()
    mock_user.id = 1
    mock_user.tenant_id = None
    mock_estado = Mock()
    mock_estado.value = 'activo'
    mock_user.estado = mock_estado
    mock_rol = Mock()
    mock_rol.nombre_rol = 'super_admin'
    mock_rol.rol = 'super_admin'
    mock_user.rol = mock_rol
    type(mock_user).tenant_id = None
    return mock_user


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


class TestTenantController:
    """Tests para TenantController."""

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.tenant_controller.TenantService')
    def test_listar_tenants_success(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test listar_tenants exitoso."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'super_admin'}
        mock_user = _create_mock_super_admin()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'},
            query_string={'activos_only': 'true'}
        ):
            g.current_user = mock_user
            
            mock_tenant = Mock()
            mock_tenant.to_dict.return_value = {'id': 1, 'nombre': 'Tenant 1'}
            mock_service.listar_tenants.return_value = [mock_tenant]

            result = TenantController.listar_tenants()

            assert result[1] == 200
            mock_service.listar_tenants.assert_called_once()

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.tenant_controller.TenantService')
    def test_listar_tenants_exception(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test listar_tenants con excepción."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'super_admin'}
        mock_user = _create_mock_super_admin()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            
            mock_service.listar_tenants.side_effect = Exception("Error")

            result = TenantController.listar_tenants()

            assert result[1] == 500

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.tenant_controller.TenantService')
    def test_crear_tenant_success(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test crear_tenant exitoso."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'super_admin'}
        mock_user = _create_mock_super_admin()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            json={'nombre': 'Nuevo Tenant', 'codigo_tenant': 'TENANT001'},
            content_type='application/json',
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            
            mock_tenant = Mock()
            mock_tenant.to_dict.return_value = {
                'id': 1,
                'nombre': 'Nuevo Tenant'
            }
            mock_service.crear_tenant.return_value = mock_tenant

            result = TenantController.crear_tenant()

            assert result[1] == 201
            mock_service.crear_tenant.assert_called_once()

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.tenant_controller.TenantService')
    def test_crear_tenant_no_data(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test crear_tenant sin datos."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'super_admin'}
        mock_user = _create_mock_super_admin()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            data='{}',
            content_type='application/json',
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user

            result = TenantController.crear_tenant()

            assert result[1] == 400

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.tenant_controller.TenantService')
    def test_crear_tenant_exception(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test crear_tenant con excepción."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'super_admin'}
        mock_user = _create_mock_super_admin()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            json={'nombre': 'Tenant', 'codigo_tenant': 'TENANT002'},
            content_type='application/json',
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            
            mock_service.crear_tenant.side_effect = Exception("Error")

            result = TenantController.crear_tenant()

            assert result[1] == 500

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.tenant_controller.TenantService')
    def test_obtener_tenant_success(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test obtener_tenant exitoso."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'super_admin'}
        mock_user = _create_mock_super_admin()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            
            mock_tenant = Mock()
            mock_tenant.to_dict.return_value = {
                'id': 1,
                'nombre': 'Tenant 1'
            }
            mock_service.obtener_tenant.return_value = mock_tenant

            result = TenantController.obtener_tenant(1)

            assert result[1] == 200
            mock_service.obtener_tenant.assert_called_once_with(1)

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.tenant_controller.TenantService')
    def test_obtener_tenant_not_found(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test obtener_tenant cuando no existe."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'super_admin'}
        mock_user = _create_mock_super_admin()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            
            mock_service.obtener_tenant.return_value = None

            result = TenantController.obtener_tenant(999)

            assert result[1] == 404

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.tenant_controller.TenantService')
    def test_actualizar_tenant_success(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test actualizar_tenant exitoso."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'super_admin'}
        mock_user = _create_mock_super_admin()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            json={'nombre': 'Tenant Actualizado'},
            content_type='application/json',
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            
            mock_tenant = Mock()
            mock_tenant.to_dict.return_value = {'id': 1, 'nombre': 'Tenant Actualizado'}
            mock_service.actualizar_tenant.return_value = mock_tenant

            result = TenantController.actualizar_tenant(1)

            assert result[1] == 200
            mock_service.actualizar_tenant.assert_called_once()

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.tenant_controller.TenantService')
    def test_actualizar_tenant_not_found(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test actualizar_tenant cuando no existe."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'super_admin'}
        mock_user = _create_mock_super_admin()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            json={'nombre': 'Actualizado'},
            content_type='application/json',
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            
            mock_service.actualizar_tenant.return_value = None

            result = TenantController.actualizar_tenant(999)

            assert result[1] == 400

