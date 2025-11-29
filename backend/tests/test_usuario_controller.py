import pytest
from unittest.mock import Mock, patch
import json

# Mock Flask modules
with patch.dict('sys.modules', {
    'flask': Mock(),
    'flask.jsonify': Mock(),
    'flask.request': Mock(),
    'flask.current_app': Mock(),
    'flask.g': Mock(),
    'flask.abort': Mock(),
}):
    from src.controllers.usuario_controller import UsuarioController


class TestUsuarioController:
    @patch('src.controllers.usuario_controller.jwt')
    @patch('src.controllers.usuario_controller.current_app')
    @patch('src.controllers.usuario_controller.UsuarioService')
    @patch('src.controllers.usuario_controller.request')
    def test_login_success(self, mock_request, mock_service, mock_app, mock_jwt):
        """Test login with successful authentication"""
        # Mock request data
        mock_request.get_json.return_value = {
            'email': 'test@example.com',
            'password': 'password123'
        }

        # Mock user service
        mock_user = Mock()
        mock_user.id = 1
        mock_user.persona.email = 'test@example.com'
        mock_user.rol.nombre_rol = 'usuario'
        mock_user.to_dict.return_value = {'id': 1, 'email': 'test@example.com'}
        mock_service.autenticar_usuario.return_value = mock_user

        # Mock JWT
        mock_jwt.encode.return_value = 'fake_token'

        # Mock current_app
        mock_app.config = {'SECRET_KEY': 'test_key'}

        result = UsuarioController.login()

        assert result[1] == 200
        response_data = result[0].get_json()
        assert response_data['status'] == 'success'
        assert 'token' in response_data
        assert response_data['user']['id'] == 1

    @patch('src.controllers.usuario_controller.request')
    def test_login_missing_credentials(self, mock_request):
        """Test login with missing email or password"""
        mock_request.get_json.return_value = {'email': 'test@example.com'}

        result = UsuarioController.login()

        assert result[1] == 400
        response_data = result[0].get_json()
        assert response_data['status'] == 'error'
        assert 'requeridos' in response_data['message']

    @patch('src.controllers.usuario_controller.UsuarioService')
    @patch('src.controllers.usuario_controller.request')
    def test_login_invalid_credentials(self, mock_request, mock_service):
        """Test login with invalid credentials"""
        mock_request.get_json.return_value = {
            'email': 'test@example.com',
            'password': 'wrong_password'
        }
        mock_service.autenticar_usuario.return_value = None

        result = UsuarioController.login()

        assert result[1] == 401
        response_data = result[0].get_json()
        assert response_data['status'] == 'error'
        assert 'inválidas' in response_data['message']

    @patch('src.controllers.usuario_controller.UsuarioService')
    def test_obtener_usuario_success(self, mock_service):
        """Test obtener_usuario with existing user"""
        mock_user = Mock()
        mock_user.to_dict.return_value = {'id': 1, 'email': 'test@example.com'}
        mock_service.obtener_usuario.return_value = mock_user

        result = UsuarioController.obtener_usuario(1)

        assert result[1] == 200
        response_data = result[0].get_json()
        assert response_data['status'] == 'success'
        assert response_data['data']['id'] == 1

    @patch('src.controllers.usuario_controller.UsuarioService')
    def test_obtener_usuario_not_found(self, mock_service):
        """Test obtener_usuario with non-existing user"""
        mock_service.obtener_usuario.return_value = None

        result = UsuarioController.obtener_usuario(999)

        assert result[1] == 404
        response_data = result[0].get_json()
        assert response_data['status'] == 'error'
        assert 'no encontrado' in response_data['message']

    @patch('src.controllers.usuario_controller._obtener_usuario_actual')
    def test_obtener_perfil_actual_success(self, mock_get_user):
        """Test obtener_perfil_actual with authenticated user"""
        mock_user = Mock()
        mock_persona = Mock()
        mock_persona.nombre_completo = 'Juan Pérez'
        mock_persona.email = 'juan@example.com'
        mock_persona.telefono = '123456789'
        mock_persona.fecha_creacion = '2023-01-01'
        mock_user.persona = mock_persona
        mock_get_user.return_value = mock_user

        result = UsuarioController.obtener_perfil_actual()

        assert result[1] == 200
        response_data = result[0].get_json()
        assert response_data['status'] == 'success'
        assert response_data['data']['email'] == 'juan@example.com'

    @patch('src.controllers.usuario_controller._obtener_usuario_actual')
    def test_obtener_perfil_actual_not_authenticated(self, mock_get_user):
        """Test obtener_perfil_actual without authentication"""
        mock_get_user.return_value = None

        result = UsuarioController.obtener_perfil_actual()

        assert result[1] == 401
        response_data = result[0].get_json()
        assert response_data['status'] == 'error'
        assert 'no autenticado' in response_data['message']

    @patch('src.controllers.usuario_controller._validar_email')
    def test_validar_email_valid(self, mock_validar):
        """Test _validar_email with valid email"""
        mock_validar.return_value = True
        result = UsuarioController._validar_email('test@example.com')
        assert result is True

    @patch('src.controllers.usuario_controller._validar_email')
    def test_validar_email_invalid(self, mock_validar):
        """Test _validar_email with invalid email"""
        mock_validar.return_value = False
        result = UsuarioController._validar_email('invalid-email')
        assert result is False

    def test_error_method(self):
        """Test _error method"""
        result = UsuarioController._error('Test error', 400)
        assert result[1] == 400
        response_data = result[0].get_json()
        assert response_data['status'] == 'error'
        assert response_data['message'] == 'Test error'