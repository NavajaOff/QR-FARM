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

    def test_registrar_usuario_success(self, app_context, mock_jsonify, mock_current_app, mock_request):
        """Test registrar_usuario exitoso."""
        mock_request.get_json.return_value = {
            'primer_nombre': 'Juan',
            'primer_apellido': 'Pérez',
            'email': 'juan@example.com',
            'password': 'password123'
        }
        mock_request.headers = {}

        with patch('src.controllers.usuario_controller.UsuarioService') as mock_service, \
             patch('src.controllers.usuario_controller.Usuario') as mock_usuario_class, \
             patch('src.controllers.usuario_controller.UsuarioController._obtener_usuario_desde_token') as mock_get_token:
            
            mock_get_token.return_value = None
            mock_persona = Mock()
            mock_usuario = Mock()
            mock_usuario.to_dict.return_value = {'id': 1, 'email': 'juan@example.com'}
            mock_usuario_class.from_registration_data.return_value = (mock_persona, mock_usuario)
            mock_service.buscar_por_email.return_value = None
            mock_service.crear_usuario.return_value = (mock_usuario, "Usuario creado exitosamente")

            result = UsuarioController.registrar_usuario()

            assert result[1] == 201
            response_data = result[0].get_json()
            assert response_data['status'] == 'success'

    def test_registrar_usuario_invalid_data(self, app_context, mock_jsonify, mock_current_app, mock_request):
        """Test registrar_usuario con datos inválidos."""
        mock_request.get_json.return_value = {
            'primer_nombre': 'Juan',
            'email': 'invalid-email'
        }
        mock_request.headers = {}

        with patch('src.controllers.usuario_controller.UsuarioService') as mock_service:
            mock_service.buscar_por_email.return_value = None

            result = UsuarioController.registrar_usuario()

            assert result[1] in [400, 500]

    def test_obtener_todos_usuarios_success(self, app_context, mock_jsonify, mock_current_app, mock_g):
        """Test obtener_todos_usuarios exitoso."""
        with patch('src.controllers.usuario_controller._obtener_usuario_actual') as mock_get_user, \
             patch('src.controllers.usuario_controller.UsuarioService') as mock_service:
            
            mock_user = Mock()
            mock_user.tenant_id = 1
            mock_get_user.return_value = mock_user
            mock_service.obtener_todos_usuarios.return_value = []

            result = UsuarioController.obtener_todos_usuarios()

            assert result[1] == 200
            response_data = result[0].get_json()
            assert response_data['status'] == 'success'

    def test_obtener_todos_usuarios_not_authenticated(self, app_context, mock_jsonify, mock_current_app, mock_g):
        """Test obtener_todos_usuarios sin autenticación."""
        with patch('src.controllers.usuario_controller._obtener_usuario_actual') as mock_get_user:
            mock_get_user.return_value = None

            result = UsuarioController.obtener_todos_usuarios()

            assert result[1] == 401

    def test_cambiar_estado_usuario_success(self, app_context, mock_jsonify, mock_current_app, mock_request):
        """Test cambiar_estado_usuario exitoso."""
        mock_request.get_json.return_value = {'estado': 'activo'}

        with patch('src.controllers.usuario_controller.UsuarioService') as mock_service:
            mock_usuario = Mock()
            mock_usuario.estado = Mock()
            mock_service.obtener_usuario.return_value = mock_usuario
            mock_service.actualizar_usuario.return_value = True

            result = UsuarioController.cambiar_estado_usuario(1)

            assert result[1] == 200
            response_data = result[0].get_json()
            assert response_data['status'] == 'success'

    def test_cambiar_estado_usuario_invalid(self, app_context, mock_jsonify, mock_current_app, mock_request):
        """Test cambiar_estado_usuario con estado inválido."""
        mock_request.get_json.return_value = {'estado': 'invalid'}

        result = UsuarioController.cambiar_estado_usuario(1)

        assert result[1] == 400

    def test_actualizar_perfil_actual_success(self, app_context, mock_jsonify, mock_current_app, mock_g):
        """Test actualizar_perfil_actual exitoso."""
        mock_request.get_json.return_value = {
            'nombre_completo': 'Juan Pérez',
            'email': 'juan@example.com',
            'telefono': '123456789'
        }

        with patch('src.controllers.usuario_controller._obtener_usuario_actual') as mock_get_user, \
             patch('src.controllers.usuario_controller.UsuarioService') as mock_service, \
             patch('src.controllers.usuario_controller._validar_datos_perfil') as mock_validar, \
             patch('src.controllers.usuario_controller._parsear_nombre_completo') as mock_parsear, \
             patch('src.controllers.usuario_controller._actualizar_persona_perfil') as mock_actualizar:
            
            mock_user = Mock()
            mock_user.id = 1
            mock_persona = Mock()
            mock_user.persona = mock_persona
            mock_get_user.return_value = mock_user
            mock_validar.return_value = ({
                'nombre_completo': 'Juan Pérez',
                'email': 'juan@example.com',
                'telefono': '123456789'
            }, None, None)
            mock_parsear.return_value = ('Juan', None, 'Pérez', None)
            mock_actualizar.return_value = True
            mock_service.actualizar_usuario_completo.return_value = True
            mock_service.obtener_usuario.return_value = mock_user

            result = UsuarioController.actualizar_perfil_actual()

            assert result[1] == 200

    def test_actualizar_usuario_success(self, app_context, mock_jsonify, mock_current_app, mock_request):
        """Test actualizar_usuario exitoso."""
        mock_request.get_json.return_value = {
            'primer_nombre': 'Juan',
            'primer_apellido': 'Pérez',
            'email': 'juan@example.com'
        }

        with patch('src.controllers.usuario_controller.UsuarioService') as mock_service, \
             patch('src.controllers.usuario_controller.UsuarioController._validar_campos') as mock_validar, \
             patch('src.controllers.usuario_controller.UsuarioController._actualizar_datos_persona') as mock_actualizar_persona, \
             patch('src.controllers.usuario_controller.UsuarioController._actualizar_datos_usuario') as mock_actualizar_usuario, \
             patch('src.controllers.usuario_controller.UsuarioController._emitir_actualizacion') as mock_emitir:
            
            mock_usuario = Mock()
            mock_persona = Mock()
            mock_persona.email = 'juan@example.com'
            mock_usuario.persona = mock_persona
            mock_usuario.to_dict.return_value = {'id': 1, 'email': 'juan@example.com'}
            mock_service.obtener_usuario.return_value = mock_usuario
            mock_validar.return_value = None
            mock_service.actualizar_usuario_completo.return_value = True

            result = UsuarioController.actualizar_usuario(1)

            assert result[1] == 200
            response_data = result[0].get_json()
            assert response_data['status'] == 'success'

    def test_eliminar_usuario_success(self, app_context, mock_jsonify, mock_current_app):
        """Test eliminar_usuario exitoso."""
        with patch('src.controllers.usuario_controller.UsuarioService') as mock_service, \
             patch('src.controllers.usuario_controller.emit_update') as mock_emit:
            mock_service.eliminar_usuario.return_value = True

            result = UsuarioController.eliminar_usuario(1)

            assert result[1] == 200
            response_data = result[0].get_json()
            assert response_data['status'] == 'success'

    def test_eliminar_usuario_not_found(self, app_context, mock_jsonify, mock_current_app):
        """Test eliminar_usuario cuando no existe."""
        with patch('src.controllers.usuario_controller.UsuarioService') as mock_service:
            mock_service.eliminar_usuario.return_value = False

            result = UsuarioController.eliminar_usuario(999)

            assert result[1] == 404

    def test_validar_credenciales_login(self, app_context, mock_jsonify, mock_current_app, mock_request):
        """Test _validar_credenciales_login."""
        mock_request.get_json.return_value = {
            'email': 'test@example.com',
            'password': 'password123'
        }
        email, password, error = UsuarioController._validar_credenciales_login(mock_request.get_json())
        assert email == 'test@example.com'
        assert password == 'password123'
        assert error is None

    def test_validar_credenciales_login_missing(self, app_context, mock_jsonify, mock_current_app, mock_request):
        """Test _validar_credenciales_login con datos faltantes."""
        mock_request.get_json.return_value = {'email': 'test@example.com'}
        email, password, error = UsuarioController._validar_credenciales_login(mock_request.get_json())
        assert error is not None
        assert error[1] == 400

    def test_generar_token_jwt(self, app_context, mock_jsonify, mock_current_app):
        """Test _generar_token_jwt."""
        with patch('src.controllers.usuario_controller.jwt') as mock_jwt, \
             patch('src.controllers.usuario_controller.current_app') as mock_app:
            mock_app.config = {'SECRET_KEY': 'test-key'}
            mock_jwt.encode.return_value = 'fake_token'
            
            mock_usuario = Mock()
            mock_usuario.id = 1
            mock_usuario.persona = Mock()
            mock_usuario.persona.email = 'test@example.com'
            mock_usuario.rol = Mock()
            mock_usuario.rol.nombre_rol = 'usuario'

            token = UsuarioController._generar_token_jwt(mock_usuario, 'test@example.com')
            assert token == 'fake_token'

    def test_validar_campos_requeridos(self, app_context, mock_jsonify, mock_current_app):
        """Test _validar_campos_requeridos."""
        data = {'primer_nombre': '', 'primer_apellido': 'Pérez', 'email': 'test@example.com'}
        error = UsuarioController._validar_campos_requeridos(data)
        assert error is not None

    def test_validar_email_en_actualizacion(self, app_context, mock_jsonify, mock_current_app):
        """Test _validar_email_en_actualizacion."""
        with patch('src.controllers.usuario_controller._validar_email') as mock_validar, \
             patch('src.controllers.usuario_controller.UsuarioService') as mock_service:
            mock_validar.return_value = False
            mock_usuario = Mock()
            mock_persona = Mock()
            mock_persona.email = 'old@example.com'
            mock_usuario.persona = mock_persona

            error = UsuarioController._validar_email_en_actualizacion({'email': 'invalid'}, mock_usuario)
            assert error is not None

    def test_validar_password_en_actualizacion(self, app_context, mock_jsonify, mock_current_app):
        """Test _validar_password_en_actualizacion."""
        data = {'password': '123'}
        error = UsuarioController._validar_password_en_actualizacion(data)
        assert error is not None

    def test_validar_rol_en_actualizacion(self, app_context, mock_jsonify, mock_current_app):
        """Test _validar_rol_en_actualizacion."""
        with patch('src.controllers.usuario_controller.UsuarioController._obtener_nombre_rol_por_id') as mock_get_rol:
            mock_get_rol.return_value = 'super_admin'
            error = UsuarioController._validar_rol_en_actualizacion({'id_rol': 1})
            assert error is not None