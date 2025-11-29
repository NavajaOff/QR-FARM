import pytest
from unittest.mock import Mock, patch
import json

# Import the controller after fixtures are set up
from src.controllers.usuario_controller import UsuarioController


class TestUsuarioController:
    def test_login_success(self, app_context, mock_jsonify, mock_current_app, mock_request):
        """Test login with successful authentication"""
        # Mock request data
        mock_request.get_json.return_value = {
            'email': 'test@example.com',
            'password': 'password123'
        }

        # Mock user service
        with patch('src.controllers.usuario_controller.UsuarioService') as mock_service, \
             patch('src.controllers.usuario_controller.jwt') as mock_jwt:

            mock_user = Mock()
            mock_user.id = 1
            mock_user.persona.email = 'test@example.com'
            mock_user.rol.nombre_rol = 'usuario'
            mock_user.to_dict.return_value = {'id': 1, 'email': 'test@example.com'}
            mock_service.autenticar_usuario.return_value = mock_user

            # Mock JWT
            mock_jwt.encode.return_value = 'fake_token'

            result = UsuarioController.login()

            assert result[1] == 200
            # result[0] is the response object from jsonify
            response_data = result[0].get_json()
            assert response_data['status'] == 'success'
            assert 'token' in response_data
            assert response_data['user']['id'] == 1

    def test_login_missing_credentials(self, app_context, mock_jsonify, mock_current_app, mock_request):
        """Test login with missing email or password"""
        mock_request.get_json.return_value = {'email': 'test@example.com'}

        result = UsuarioController.login()

        assert result[1] == 400
        response_data = result[0].get_json()
        assert response_data['status'] == 'error'
        assert 'requeridos' in response_data['message']

    def test_login_invalid_credentials(self, app_context, mock_jsonify, mock_current_app, mock_request):
        """Test login with invalid credentials"""
        mock_request.get_json.return_value = {
            'email': 'test@example.com',
            'password': 'wrong_password'
        }

        with patch('src.controllers.usuario_controller.UsuarioService') as mock_service:
            mock_service.autenticar_usuario.return_value = None

            result = UsuarioController.login()

            assert result[1] == 401
            response_data = result[0].get_json()
            assert response_data['status'] == 'error'
            assert 'inválidas' in response_data['message']

    def test_obtener_usuario_success(self, app_context, mock_jsonify, mock_current_app):
        """Test obtener_usuario with existing user"""
        with patch('src.controllers.usuario_controller.UsuarioService') as mock_service:
            mock_user = Mock()
            mock_user.to_dict.return_value = {'id': 1, 'email': 'test@example.com'}
            mock_service.obtener_usuario.return_value = mock_user

            result = UsuarioController.obtener_usuario(1)

            assert result[1] == 200
            response_data = result[0].get_json()
            assert response_data['status'] == 'success'
            assert response_data['data']['id'] == 1

    def test_obtener_usuario_not_found(self, app_context, mock_jsonify, mock_current_app):
        """Test obtener_usuario with non-existing user"""
        with patch('src.controllers.usuario_controller.UsuarioService') as mock_service:
            mock_service.obtener_usuario.return_value = None

            result = UsuarioController.obtener_usuario(999)

            assert result[1] == 404
            response_data = result[0].get_json()
            assert response_data['status'] == 'error'
            assert 'no encontrado' in response_data['message']

    def test_obtener_perfil_actual_success(self, app_context, mock_jsonify, mock_current_app, mock_g):
        """Test obtener_perfil_actual with authenticated user"""
        with patch('src.controllers.usuario_controller._obtener_usuario_actual') as mock_get_user:
            mock_user = Mock()
            mock_persona = Mock()
            mock_persona.to_dict.return_value = {
                'nombre_completo': 'Juan Pérez',
                'email': 'juan@example.com',
                'telefono': '123456789',
                'fecha_creacion': '2023-01-01'
            }
            mock_user.persona = mock_persona
            mock_get_user.return_value = mock_user

            result = UsuarioController.obtener_perfil_actual()

            assert result[1] == 200
            response_data = result[0].get_json()
            assert response_data['status'] == 'success'
            assert response_data['data']['email'] == 'juan@example.com'

    def test_obtener_perfil_actual_not_authenticated(self, app_context, mock_jsonify, mock_current_app, mock_g):
        """Test obtener_perfil_actual without authentication"""
        with patch('src.controllers.usuario_controller._obtener_usuario_actual') as mock_get_user:
            mock_get_user.return_value = None

            result = UsuarioController.obtener_perfil_actual()

            assert result[1] == 401
            response_data = result[0].get_json()
            assert response_data['status'] == 'error'
            assert 'autenticado' in response_data['message']

    def test_validar_email_valid(self):
        """Test _validar_email with valid email"""
        from src.controllers.usuario_controller import _validar_email
        result = _validar_email('test@example.com')
        assert result is True

    def test_validar_email_invalid(self):
        """Test _validar_email with invalid email"""
        from src.controllers.usuario_controller import _validar_email
        result = _validar_email('invalid-email')
        assert result is False

    def test_error_method(self, app_context, mock_jsonify, mock_current_app):
        """Test _error method"""
        result = UsuarioController._error('Test error', 400)
        assert result[1] == 400
        response_data = result[0].get_json()
        assert response_data['status'] == 'error'
        assert response_data['message'] == 'Test error'