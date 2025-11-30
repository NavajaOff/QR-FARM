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
        
        # El resultado puede ser una tupla o un int dependiendo de cómo se maneje el error
        if isinstance(result, tuple):
            assert result[1] == 400
            response_data = result[0].get_json()
            assert response_data['status'] == 'error'
            assert 'requeridos' in response_data['message']
        else:
            assert result == 400

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
            # _crear_usuario_en_bd retorna (usuario, mensaje)
            with patch('src.controllers.usuario_controller.UsuarioController._crear_usuario_en_bd') as mock_crear:
                mock_crear.return_value = (mock_usuario, "Usuario creado exitosamente")

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

    def test_actualizar_perfil_actual_success(self, app_context, mock_jsonify, mock_current_app, mock_g, mock_request):
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
        email, error_response, status_code = UsuarioController._validar_credenciales_login(mock_request.get_json())
        assert email is None
        assert error_response is not None
        assert status_code == 400

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

    def test_validar_rol_en_actualizacion_valid_rol(self, app_context, mock_jsonify, mock_current_app):
        """Test _validar_rol_en_actualizacion with valid rol."""
        with patch('src.controllers.usuario_controller.UsuarioController._obtener_nombre_rol_por_id') as mock_get_rol:
            mock_get_rol.return_value = 'usuario'
            error = UsuarioController._validar_rol_en_actualizacion({'id_rol': 2})
            assert error is None

    def test_validar_rol_en_actualizacion_no_id_rol(self, app_context, mock_jsonify, mock_current_app):
        """Test _validar_rol_en_actualizacion when id_rol not in data."""
        error = UsuarioController._validar_rol_en_actualizacion({})
        assert error is None

    def test_validar_rol_en_actualizacion_invalid_rol_id(self, app_context, mock_jsonify, mock_current_app):
        """Test _validar_rol_en_actualizacion with invalid rol_id type."""
        error = UsuarioController._validar_rol_en_actualizacion({'id_rol': 'invalid'})
        assert error is not None

    def test_obtener_usuario_desde_token_success(self, app_context, mock_jsonify, mock_current_app, mock_request):
        """Test _obtener_usuario_desde_token with valid token."""
        mock_request.headers = {'Authorization': 'Bearer valid_token'}
        
        with patch('src.controllers.usuario_controller.jwt') as mock_jwt, \
             patch('src.controllers.usuario_controller.UsuarioService') as mock_service:
            mock_jwt.decode.return_value = {'user_id': 1}
            mock_user = Mock()
            mock_service.obtener_usuario.return_value = mock_user

            result = UsuarioController._obtener_usuario_desde_token()
            assert result == mock_user
            mock_service.obtener_usuario.assert_called_once_with(1, incluir_inactivos=True)

    def test_obtener_usuario_desde_token_no_header(self, app_context, mock_jsonify, mock_current_app, mock_request):
        """Test _obtener_usuario_desde_token without Authorization header."""
        mock_request.headers = {}
        result = UsuarioController._obtener_usuario_desde_token()
        assert result is None

    def test_obtener_usuario_desde_token_invalid_format(self, app_context, mock_jsonify, mock_current_app, mock_request):
        """Test _obtener_usuario_desde_token with invalid format."""
        mock_request.headers = {'Authorization': 'InvalidFormat token'}
        result = UsuarioController._obtener_usuario_desde_token()
        assert result is None

    def test_obtener_usuario_desde_token_expired(self, app_context, mock_jsonify, mock_current_app, mock_request):
        """Test _obtener_usuario_desde_token with expired token."""
        mock_request.headers = {'Authorization': 'Bearer expired_token'}
        
        with patch('src.controllers.usuario_controller.jwt.decode') as mock_decode:
            from jwt.exceptions import ExpiredSignatureError
            mock_decode.side_effect = ExpiredSignatureError("Token expired")
            
            result = UsuarioController._obtener_usuario_desde_token()
            assert result is None

    def test_obtener_usuario_desde_token_invalid(self, app_context, mock_jsonify, mock_current_app, mock_request):
        """Test _obtener_usuario_desde_token with invalid token."""
        mock_request.headers = {'Authorization': 'Bearer invalid_token'}
        
        with patch('src.controllers.usuario_controller.jwt.decode') as mock_decode:
            from jwt.exceptions import InvalidTokenError
            mock_decode.side_effect = InvalidTokenError("Invalid token")
            
            result = UsuarioController._obtener_usuario_desde_token()
            assert result is None

    def test_obtener_usuario_desde_token_no_user_id(self, app_context, mock_jsonify, mock_current_app, mock_request):
        """Test _obtener_usuario_desde_token when token has no user_id."""
        mock_request.headers = {'Authorization': 'Bearer token'}
        
        with patch('src.controllers.usuario_controller.jwt') as mock_jwt:
            mock_jwt.decode.return_value = {}
            
            result = UsuarioController._obtener_usuario_desde_token()
            assert result is None

    def test_obtener_nombre_rol_with_nombre_rol(self, app_context, mock_jsonify, mock_current_app):
        """Test _obtener_nombre_rol when rol has nombre_rol."""
        mock_usuario = Mock()
        mock_rol = Mock()
        mock_rol.nombre_rol = 'admin'
        mock_usuario.rol = mock_rol
        
        result = UsuarioController._obtener_nombre_rol(mock_usuario)
        assert result == 'admin'

    def test_obtener_nombre_rol_with_rol_attribute(self, app_context, mock_jsonify, mock_current_app):
        """Test _obtener_nombre_rol when rol has rol attribute."""
        mock_usuario = Mock()
        mock_rol = Mock()
        del mock_rol.nombre_rol
        mock_rol.rol = 'usuario'
        mock_usuario.rol = mock_rol
        
        result = UsuarioController._obtener_nombre_rol(mock_usuario)
        assert result == 'usuario'

    def test_obtener_nombre_rol_no_rol(self, app_context, mock_jsonify, mock_current_app):
        """Test _obtener_nombre_rol when usuario has no rol."""
        mock_usuario = Mock()
        mock_usuario.rol = None
        
        result = UsuarioController._obtener_nombre_rol(mock_usuario)
        assert result is None

    def test_obtener_nombre_rol_no_usuario(self, app_context, mock_jsonify, mock_current_app):
        """Test _obtener_nombre_rol when usuario is None."""
        result = UsuarioController._obtener_nombre_rol(None)
        assert result is None

    @patch('src.database.db.get_connection')
    def test_obtener_nombre_rol_por_id_success(self, mock_get_connection, app_context):
        """Test _obtener_nombre_rol_por_id with successful fetch."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {'rol': 'admin'}
        
        result = UsuarioController._obtener_nombre_rol_por_id(1)
        assert result == 'admin'
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()
        assert mock_conn.close.call_count >= 1

    @patch('src.database.db.get_connection')
    def test_obtener_nombre_rol_por_id_not_found(self, mock_get_connection, app_context):
        """Test _obtener_nombre_rol_por_id when rol not found."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        result = UsuarioController._obtener_nombre_rol_por_id(999)
        assert result is None

    @patch('src.database.db.get_connection')
    def test_obtener_nombre_rol_por_id_exception(self, mock_get_connection, app_context):
        """Test _obtener_nombre_rol_por_id with exception."""
        mock_get_connection.side_effect = Exception("DB Error")
        
        result = UsuarioController._obtener_nombre_rol_por_id(1)
        assert result is None

    def test_es_super_admin_true(self, app_context, mock_jsonify, mock_current_app):
        """Test _es_super_admin returns True for super_admin."""
        mock_usuario = Mock()
        with patch('src.controllers.usuario_controller.UsuarioController._obtener_nombre_rol') as mock_get_rol:
            mock_get_rol.return_value = 'super_admin'
            result = UsuarioController._es_super_admin(mock_usuario)
            assert result is True

    def test_es_super_admin_false(self, app_context, mock_jsonify, mock_current_app):
        """Test _es_super_admin returns False for other roles."""
        mock_usuario = Mock()
        with patch('src.controllers.usuario_controller.UsuarioController._obtener_nombre_rol') as mock_get_rol:
            mock_get_rol.return_value = 'usuario'
            result = UsuarioController._es_super_admin(mock_usuario)
            assert result is False

    def test_obtener_tenant_id_override_not_super_admin(self, app_context, mock_jsonify, mock_current_app):
        """Test _obtener_tenant_id_override when not super admin."""
        result, error = UsuarioController._obtener_tenant_id_override(False, {'tenant_id': 1})
        assert result is None
        assert error is None

    def test_obtener_tenant_id_override_no_tenant_id(self, app_context, mock_jsonify, mock_current_app):
        """Test _obtener_tenant_id_override when tenant_id not in data."""
        result, error = UsuarioController._obtener_tenant_id_override(True, {})
        assert result is None
        assert error is None

    def test_obtener_tenant_id_override_invalid_type(self, app_context, mock_jsonify, mock_current_app):
        """Test _obtener_tenant_id_override with invalid tenant_id type."""
        result, error = UsuarioController._obtener_tenant_id_override(True, {'tenant_id': 'invalid'})
        assert result is None
        assert error == 'tenant_id debe ser un número válido'

    def test_asignar_rol_si_es_super_admin_success(self, app_context, mock_jsonify, mock_current_app):
        """Test _asignar_rol_si_es_super_admin assigns rol."""
        mock_persona = Mock()
        mock_usuario = Mock()
        data = {'id_rol': 2}
        
        UsuarioController._asignar_rol_si_es_super_admin(True, data, mock_persona, mock_usuario)
        
        assert mock_persona.id_rol == 2
        assert mock_usuario.id_rol == 2

    def test_asignar_rol_si_es_super_admin_not_super(self, app_context, mock_jsonify, mock_current_app):
        """Test _asignar_rol_si_es_super_admin doesn't assign when not super admin."""
        class MockPersona:
            def __init__(self):
                self.id_rol = None
        
        class MockUsuario:
            def __init__(self):
                self.id_rol = None
        
        mock_persona = MockPersona()
        mock_usuario = MockUsuario()
        data = {'id_rol': 2}
        
        UsuarioController._asignar_rol_si_es_super_admin(False, data, mock_persona, mock_usuario)
        
        # Verify that id_rol was not assigned
        assert mock_persona.id_rol is None
        assert mock_usuario.id_rol is None

    def test_asignar_rol_si_es_super_admin_invalid_rol_id(self, app_context, mock_jsonify, mock_current_app):
        """Test _asignar_rol_si_es_super_admin with invalid rol_id."""
        mock_persona = Mock()
        mock_usuario = Mock()
        data = {'id_rol': 'invalid'}
        
        # Should not raise exception, just silently fail
        UsuarioController._asignar_rol_si_es_super_admin(True, data, mock_persona, mock_usuario)

    @patch('src.controllers.usuario_controller.UsuarioService')
    def test_crear_usuario_en_bd_super_admin(self, mock_service, app_context):
        """Test _crear_usuario_en_bd with super admin."""
        mock_persona = Mock()
        mock_usuario = Mock()
        mock_service.crear_usuario.return_value = (mock_usuario, "Usuario creado")
        
        result = UsuarioController._crear_usuario_en_bd(True, 1, mock_persona, mock_usuario)
        
        assert result == (mock_usuario, "Usuario creado")
        mock_service.crear_usuario.assert_called_once_with(
            mock_persona, mock_usuario, tenant_id_override=1, es_super_admin=True
        )

    @patch('src.controllers.usuario_controller.UsuarioService')
    def test_crear_usuario_en_bd_normal_user(self, mock_service, app_context):
        """Test _crear_usuario_en_bd with normal user."""
        mock_persona = Mock()
        mock_usuario = Mock()
        mock_service.registrar_usuario.return_value = (mock_usuario, "Usuario registrado")
        
        result = UsuarioController._crear_usuario_en_bd(False, None, mock_persona, mock_usuario)
        
        assert result == (mock_usuario, "Usuario registrado")
        mock_service.registrar_usuario.assert_called_once_with(mock_persona, mock_usuario)

    def test_obtener_tenant_id_filtrado_super_admin_with_param(self, app_context, mock_jsonify, mock_current_app, mock_request):
        """Test _obtener_tenant_id_filtrado for super admin with tenant_id param."""
        mock_user = Mock()
        mock_request.args = Mock()
        mock_request.args.get = Mock(return_value='5')
        with patch('src.controllers.usuario_controller.UsuarioController._es_super_admin') as mock_is_super:
            mock_is_super.return_value = True
            
            tenant_id, error = UsuarioController._obtener_tenant_id_filtrado(mock_user)
            assert tenant_id == 5
            assert error is None

    def test_obtener_tenant_id_filtrado_super_admin_invalid_param(self, app_context, mock_jsonify, mock_current_app, mock_request):
        """Test _obtener_tenant_id_filtrado for super admin with invalid param."""
        mock_user = Mock()
        mock_request.args = Mock()
        mock_request.args.get = Mock(return_value='invalid')
        with patch('src.controllers.usuario_controller.UsuarioController._es_super_admin') as mock_is_super:
            mock_is_super.return_value = True
            
            tenant_id, error = UsuarioController._obtener_tenant_id_filtrado(mock_user)
            assert tenant_id is None
            assert error is None

    def test_obtener_tenant_id_filtrado_normal_user(self, app_context, mock_jsonify, mock_current_app):
        """Test _obtener_tenant_id_filtrado for normal user."""
        mock_user = Mock()
        mock_user.tenant_id = 1
        with patch('src.controllers.usuario_controller.UsuarioController._es_super_admin') as mock_is_super:
            mock_is_super.return_value = False
            
            tenant_id, error = UsuarioController._obtener_tenant_id_filtrado(mock_user)
            assert tenant_id == 1
            assert error is None

    def test_obtener_tenant_id_filtrado_no_tenant(self, app_context, mock_jsonify, mock_current_app):
        """Test _obtener_tenant_id_filtrado when user has no tenant_id."""
        mock_user = Mock()
        mock_user.tenant_id = None
        with patch('src.controllers.usuario_controller.UsuarioController._es_super_admin') as mock_is_super:
            mock_is_super.return_value = False
            
            tenant_id, error = UsuarioController._obtener_tenant_id_filtrado(mock_user)
            assert tenant_id is None
            assert error == 'No se puede determinar el tenant del usuario'

    def test_actualizar_datos_persona(self, app_context, mock_jsonify, mock_current_app):
        """Test _actualizar_datos_persona updates all fields."""
        mock_persona = Mock()
        mock_usuario = Mock()
        mock_usuario.persona = mock_persona
        
        data = {
            'primer_nombre': 'Juan',
            'segundo_nombre': 'Carlos',
            'primer_apellido': 'Pérez',
            'segundo_apellido': 'García',
            'email': 'juan@example.com',
            'telefono': '123456789',
            'id_rol': 2
        }
        
        UsuarioController._actualizar_datos_persona(mock_usuario, data)
        
        assert mock_persona.primer_nombre == 'Juan'
        assert mock_persona.segundo_nombre == 'Carlos'
        assert mock_persona.primer_apellido == 'Pérez'
        assert mock_persona.segundo_apellido == 'García'
        assert mock_persona.email == 'juan@example.com'
        assert mock_persona.telefono == '123456789'
        assert mock_persona.id_rol == 2

    def test_actualizar_datos_persona_none_values(self, app_context, mock_jsonify, mock_current_app):
        """Test _actualizar_datos_persona with None values."""
        mock_persona = Mock()
        mock_usuario = Mock()
        mock_usuario.persona = mock_persona
        
        data = {
            'primer_nombre': '',
            'telefono': None
        }
        
        UsuarioController._actualizar_datos_persona(mock_usuario, data)
        
        assert mock_persona.primer_nombre is None
        assert mock_persona.telefono is None

    def test_actualizar_datos_usuario(self, app_context, mock_jsonify, mock_current_app):
        """Test _actualizar_datos_usuario updates all fields."""
        from src.models.usuario import EstadoUsuario
        mock_usuario = Mock()
        mock_usuario.estado = EstadoUsuario.ACTIVO
        
        data = {
            'password': 'newpassword123',
            'estado': 'inactivo',
            'id_rol': 2
        }
        
        UsuarioController._actualizar_datos_usuario(mock_usuario, data)
        
        mock_usuario.set_password.assert_called_once_with('newpassword123')
        assert mock_usuario.id_rol == 2

    def test_emitir_actualizacion_success(self, app_context, mock_jsonify, mock_current_app):
        """Test _emitir_actualizacion with emit_update available."""
        mock_usuario = Mock()
        mock_usuario.to_dict.return_value = {'id': 1}
        
        with patch('src.controllers.usuario_controller.emit_update') as mock_emit:
            UsuarioController._emitir_actualizacion(1, mock_usuario)
            mock_emit.assert_called_once_with('usuario_updated', {'id': 1, 'data': {'id': 1}})

    def test_emitir_actualizacion_name_error(self, app_context, mock_jsonify, mock_current_app):
        """Test _emitir_actualizacion when emit_update not available."""
        mock_usuario = Mock()
        
        with patch('src.controllers.usuario_controller.emit_update', side_effect=NameError):
            # Should not raise exception
            UsuarioController._emitir_actualizacion(1, mock_usuario)

    def test_parsear_nombre_completo_two_parts(self, app_context, mock_jsonify, mock_current_app):
        """Test _parsear_nombre_completo with two parts."""
        from src.controllers.usuario_controller import _parsear_nombre_completo
        
        mock_usuario = Mock()
        mock_usuario.persona = None
        
        result = _parsear_nombre_completo('Juan Pérez', mock_usuario)
        assert result == ('Juan', 'Pérez', 'Pérez', None)

    def test_parsear_nombre_completo_three_parts(self, app_context, mock_jsonify, mock_current_app):
        """Test _parsear_nombre_completo with three parts."""
        from src.controllers.usuario_controller import _parsear_nombre_completo
        
        mock_usuario = Mock()
        mock_persona = Mock()
        mock_persona.primer_apellido = 'García'
        mock_persona.segundo_apellido = 'López'
        mock_usuario.persona = mock_persona
        
        result = _parsear_nombre_completo('Juan Carlos Pérez', mock_usuario)
        assert result == ('Juan', 'Carlos', 'Pérez', 'López')

    def test_parsear_nombre_completo_one_part(self, app_context, mock_jsonify, mock_current_app):
        """Test _parsear_nombre_completo with one part."""
        from src.controllers.usuario_controller import _parsear_nombre_completo
        
        mock_usuario = Mock()
        mock_persona = Mock()
        mock_persona.primer_apellido = 'Pérez'
        mock_persona.segundo_nombre = 'Carlos'
        mock_persona.segundo_apellido = 'García'
        mock_usuario.persona = mock_persona
        
        result = _parsear_nombre_completo('Juan', mock_usuario)
        assert result == ('Juan', 'Carlos', 'Pérez', 'García')

    def test_actualizar_persona_perfil_success(self, app_context, mock_jsonify, mock_current_app):
        """Test _actualizar_persona_perfil updates persona."""
        from src.controllers.usuario_controller import _actualizar_persona_perfil
        
        mock_persona = Mock()
        result = _actualizar_persona_perfil(
            mock_persona, 'Juan', 'Carlos', 'Pérez', 'García', 'juan@example.com', '123456789'
        )
        
        assert result is True
        assert mock_persona.primer_nombre == 'Juan'
        assert mock_persona.segundo_nombre == 'Carlos'
        assert mock_persona.primer_apellido == 'Pérez'
        assert mock_persona.segundo_apellido == 'García'
        assert mock_persona.email == 'juan@example.com'
        assert mock_persona.telefono == '123456789'

    def test_actualizar_persona_perfil_no_persona(self, app_context, mock_jsonify, mock_current_app):
        """Test _actualizar_persona_perfil when persona is None."""
        from src.controllers.usuario_controller import _actualizar_persona_perfil
        
        result = _actualizar_persona_perfil(
            None, 'Juan', None, 'Pérez', None, 'juan@example.com', None
        )
        
        assert result is False

    def test_registrar_usuario_email_duplicado(self, app_context, mock_jsonify, mock_current_app, mock_request):
        """Test registrar_usuario with duplicate email."""
        mock_request.get_json.return_value = {
            'primer_nombre': 'Juan',
            'primer_apellido': 'Pérez',
            'email': 'existing@example.com',
            'password': 'password123'
        }
        mock_request.headers = {}

        with patch('src.controllers.usuario_controller.UsuarioService') as mock_service:
            mock_service.buscar_por_email.return_value = Mock()  # Email exists
            
            result = UsuarioController.registrar_usuario()
            assert result[1] == 400

    def test_registrar_usuario_exception(self, app_context, mock_jsonify, mock_current_app, mock_request):
        """Test registrar_usuario with exception."""
        mock_request.get_json.side_effect = Exception("Error")
        
        result = UsuarioController.registrar_usuario()
        assert result[1] == 500

    def test_validar_datos_registro_no_data(self, app_context, mock_jsonify, mock_current_app):
        """Test _validar_datos_registro with no data."""
        result = UsuarioController._validar_datos_registro(None)
        assert result[0] is None
        assert result[1] == 'No se recibieron datos JSON válidos'
        assert result[2] == 400

    def test_validar_datos_registro_missing_field(self, app_context, mock_jsonify, mock_current_app):
        """Test _validar_datos_registro with missing field."""
        with patch('src.controllers.usuario_controller.UsuarioService') as mock_service:
            mock_service.buscar_por_email.return_value = None
            data = {'primer_nombre': 'Juan'}
            result = UsuarioController._validar_datos_registro(data)
            assert result[0] is None
            assert result[2] == 400

    def test_validar_email_en_actualizacion_same_email(self, app_context, mock_jsonify, mock_current_app):
        """Test _validar_email_en_actualizacion with same email."""
        with patch('src.controllers.usuario_controller._validar_email') as mock_validar:
            mock_validar.return_value = True
            mock_usuario = Mock()
            mock_persona = Mock()
            mock_persona.email = 'test@example.com'
            mock_usuario.persona = mock_persona
            
            error = UsuarioController._validar_email_en_actualizacion({'email': 'test@example.com'}, mock_usuario)
            assert error is None

    def test_validar_email_en_actualizacion_duplicate(self, app_context, mock_jsonify, mock_current_app):
        """Test _validar_email_en_actualizacion with duplicate email."""
        with patch('src.controllers.usuario_controller._validar_email') as mock_validar, \
             patch('src.controllers.usuario_controller.UsuarioService') as mock_service:
            mock_validar.return_value = True
            mock_service.buscar_por_email.return_value = Mock()  # Email exists
            mock_usuario = Mock()
            mock_persona = Mock()
            mock_persona.email = 'old@example.com'
            mock_usuario.persona = mock_persona
            
            error = UsuarioController._validar_email_en_actualizacion({'email': 'new@example.com'}, mock_usuario)
            assert error is not None

    def test_validar_datos_perfil_success(self, app_context, mock_jsonify, mock_current_app):
        """Test _validar_datos_perfil with valid data."""
        from src.controllers.usuario_controller import _validar_datos_perfil
        with patch('src.controllers.usuario_controller._validar_email') as mock_validar:
            mock_validar.return_value = True
            data = {
                'nombre_completo': 'Juan Pérez',
                'email': 'juan@example.com',
                'telefono': '123456789'
            }
            datos_validos, error_response, status = _validar_datos_perfil(data)
            assert datos_validos is not None
            assert error_response is None
            assert status is None

    def test_validar_datos_perfil_missing_fields(self, app_context, mock_jsonify, mock_current_app):
        """Test _validar_datos_perfil with missing fields."""
        from src.controllers.usuario_controller import _validar_datos_perfil
        data = {'nombre_completo': 'Juan Pérez'}
        datos_validos, error_response, status = _validar_datos_perfil(data)
        assert datos_validos is None
        assert error_response is not None
        assert status == 400

    def test_validar_datos_perfil_invalid_email(self, app_context, mock_jsonify, mock_current_app):
        """Test _validar_datos_perfil with invalid email."""
        from src.controllers.usuario_controller import _validar_datos_perfil
        with patch('src.controllers.usuario_controller._validar_email') as mock_validar:
            mock_validar.return_value = False
            data = {
                'nombre_completo': 'Juan Pérez',
                'email': 'invalid-email',
                'telefono': '123456789'
            }
            datos_validos, error_response, status = _validar_datos_perfil(data)
            assert datos_validos is None
            assert error_response is not None
            assert status == 400

    def test_respuesta_error(self, app_context, mock_jsonify, mock_current_app):
        """Test _respuesta_error function."""
        from src.controllers.usuario_controller import _respuesta_error
        result = _respuesta_error('Test error', 400)
        assert result[1] == 400
        response_data = result[0].get_json()
        assert response_data['status'] == 'error'
        assert response_data['message'] == 'Test error'

    def test_respuesta_actualizacion_exitosa(self, app_context, mock_jsonify, mock_current_app):
        """Test _respuesta_actualizacion_exitosa function."""
        from src.controllers.usuario_controller import _respuesta_actualizacion_exitosa
        mock_usuario = Mock()
        mock_persona = Mock()
        mock_persona.to_dict.return_value = {
            'nombre_completo': 'Juan Pérez',
            'email': 'juan@example.com',
            'telefono': '123456789',
            'fecha_creacion': '2023-01-01'
        }
        mock_usuario.persona = mock_persona
        
        result = _respuesta_actualizacion_exitosa(mock_usuario)
        assert result[1] == 200
        response_data = result[0].get_json()
        assert response_data['status'] == 'success'

    def test_respuesta_actualizacion_exitosa_no_persona(self, app_context, mock_jsonify, mock_current_app):
        """Test _respuesta_actualizacion_exitosa with no persona."""
        from src.controllers.usuario_controller import _respuesta_actualizacion_exitosa
        mock_usuario = Mock()
        mock_usuario.persona = None
        
        result = _respuesta_actualizacion_exitosa(mock_usuario)
        assert result[1] == 200
        response_data = result[0].get_json()
        assert response_data['status'] == 'success'

    def test_obtener_perfil_actual_no_persona(self, app_context, mock_jsonify, mock_current_app, mock_g):
        """Test obtener_perfil_actual when usuario has no persona."""
        with patch('src.controllers.usuario_controller._obtener_usuario_actual') as mock_get_user:
            mock_user = Mock()
            mock_user.persona = None
            mock_get_user.return_value = mock_user

            result = UsuarioController.obtener_perfil_actual()

            assert result[1] == 200
            response_data = result[0].get_json()
            assert response_data['status'] == 'success'

    def test_obtener_perfil_actual_exception(self, app_context, mock_jsonify, mock_current_app, mock_g):
        """Test obtener_perfil_actual with exception."""
        with patch('src.controllers.usuario_controller._obtener_usuario_actual') as mock_get_user:
            mock_get_user.side_effect = Exception("Error")
            
            result = UsuarioController.obtener_perfil_actual()
            assert result[1] == 500

    def test_actualizar_perfil_actual_no_persona(self, app_context, mock_jsonify, mock_current_app, mock_g, mock_request):
        """Test actualizar_perfil_actual when usuario has no persona."""
        mock_request.get_json.return_value = {
            'nombre_completo': 'Juan Pérez',
            'email': 'juan@example.com',
            'telefono': '123456789'
        }

        with patch('src.controllers.usuario_controller._obtener_usuario_actual') as mock_get_user, \
             patch('src.controllers.usuario_controller._validar_datos_perfil') as mock_validar:
            
            mock_user = Mock()
            mock_user.id = 1
            mock_user.persona = None
            mock_get_user.return_value = mock_user
            mock_validar.return_value = ({
                'nombre_completo': 'Juan Pérez',
                'email': 'juan@example.com',
                'telefono': '123456789'
            }, None, None)

            result = UsuarioController.actualizar_perfil_actual()
            assert result[1] == 404

    def test_actualizar_perfil_actual_update_fails(self, app_context, mock_jsonify, mock_current_app, mock_g, mock_request):
        """Test actualizar_perfil_actual when update fails."""
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
            mock_service.actualizar_usuario_completo.return_value = False

            result = UsuarioController.actualizar_perfil_actual()
            assert result[1] == 400

    def test_cambiar_estado_usuario_not_found(self, app_context, mock_jsonify, mock_current_app, mock_request):
        """Test cambiar_estado_usuario when usuario not found."""
        mock_request.get_json.return_value = {'estado': 'activo'}

        with patch('src.controllers.usuario_controller.UsuarioService') as mock_service:
            mock_service.obtener_usuario.return_value = None

            result = UsuarioController.cambiar_estado_usuario(999)
            assert result[1] == 404

    def test_cambiar_estado_usuario_update_fails(self, app_context, mock_jsonify, mock_current_app, mock_request):
        """Test cambiar_estado_usuario when update fails."""
        mock_request.get_json.return_value = {'estado': 'activo'}

        with patch('src.controllers.usuario_controller.UsuarioService') as mock_service:
            mock_usuario = Mock()
            mock_usuario.estado = Mock()
            mock_service.obtener_usuario.return_value = mock_usuario
            mock_service.actualizar_usuario.return_value = False

            result = UsuarioController.cambiar_estado_usuario(1)
            assert result[1] == 400

    def test_cambiar_estado_usuario_inactivo(self, app_context, mock_jsonify, mock_current_app, mock_request):
        """Test cambiar_estado_usuario to inactivo."""
        mock_request.get_json.return_value = {'estado': 'inactivo'}

        with patch('src.controllers.usuario_controller.UsuarioService') as mock_service:
            mock_usuario = Mock()
            mock_usuario.estado = Mock()
            mock_service.obtener_usuario.return_value = mock_usuario
            mock_service.actualizar_usuario.return_value = True

            result = UsuarioController.cambiar_estado_usuario(1)
            assert result[1] == 200
            response_data = result[0].get_json()
            assert 'desactivado' in response_data['message']

    def test_obtener_usuario_exception(self, app_context, mock_jsonify, mock_current_app):
        """Test obtener_usuario with exception."""
        with patch('src.controllers.usuario_controller.UsuarioService') as mock_service:
            mock_service.obtener_usuario.side_effect = Exception("Error")

            result = UsuarioController.obtener_usuario(1)
            assert result[1] == 500

    def test_login_exception(self, app_context, mock_jsonify, mock_current_app, mock_request):
        """Test login with exception."""
        mock_request.get_json.side_effect = Exception("Error")

        result = UsuarioController.login()
        assert result[1] == 500

    def test_obtener_todos_usuarios_exception(self, app_context, mock_jsonify, mock_current_app, mock_g):
        """Test obtener_todos_usuarios with exception."""
        with patch('src.controllers.usuario_controller._obtener_usuario_actual') as mock_get_user, \
             patch('src.controllers.usuario_controller.UsuarioService') as mock_service:
            
            mock_user = Mock()
            mock_user.tenant_id = 1
            mock_get_user.return_value = mock_user
            mock_service.obtener_todos_usuarios.side_effect = Exception("Error")

            result = UsuarioController.obtener_todos_usuarios()
            assert result[1] == 500

    def test_obtener_todos_usuarios_tenant_error(self, app_context, mock_jsonify, mock_current_app, mock_g):
        """Test obtener_todos_usuarios with tenant error."""
        with patch('src.controllers.usuario_controller._obtener_usuario_actual') as mock_get_user, \
             patch('src.controllers.usuario_controller.UsuarioController._obtener_tenant_id_filtrado') as mock_get_tenant:
            
            mock_user = Mock()
            mock_get_user.return_value = mock_user
            mock_get_tenant.return_value = (None, 'No se puede determinar el tenant')

            result = UsuarioController.obtener_todos_usuarios()
            assert result[1] == 403

    def test_actualizar_usuario_no_data(self, app_context, mock_jsonify, mock_current_app, mock_request):
        """Test actualizar_usuario with no data."""
        mock_request.get_json.return_value = None

        result = UsuarioController.actualizar_usuario(1)
        assert result[1] == 400

    def test_actualizar_usuario_not_found(self, app_context, mock_jsonify, mock_current_app, mock_request):
        """Test actualizar_usuario when usuario not found."""
        mock_request.get_json.return_value = {'primer_nombre': 'Juan'}

        with patch('src.controllers.usuario_controller.UsuarioService') as mock_service:
            mock_service.obtener_usuario.return_value = None

            result = UsuarioController.actualizar_usuario(999)
            assert result[1] == 404

    def test_actualizar_usuario_validation_error(self, app_context, mock_jsonify, mock_current_app, mock_request):
        """Test actualizar_usuario with validation error."""
        mock_request.get_json.return_value = {'email': 'invalid-email'}

        with patch('src.controllers.usuario_controller.UsuarioService') as mock_service, \
             patch('src.controllers.usuario_controller.UsuarioController._validar_campos') as mock_validar:
            
            mock_usuario = Mock()
            mock_service.obtener_usuario.return_value = mock_usuario
            mock_validar.return_value = (Mock(), 400)  # Error response

            result = UsuarioController.actualizar_usuario(1)
            assert result[1] == 400

    def test_actualizar_usuario_update_fails(self, app_context, mock_jsonify, mock_current_app, mock_request):
        """Test actualizar_usuario when update fails."""
        mock_request.get_json.return_value = {
            'primer_nombre': 'Juan',
            'primer_apellido': 'Pérez',
            'email': 'juan@example.com'
        }

        with patch('src.controllers.usuario_controller.UsuarioService') as mock_service, \
             patch('src.controllers.usuario_controller.UsuarioController._validar_campos') as mock_validar:
            
            mock_usuario = Mock()
            mock_service.obtener_usuario.return_value = mock_usuario
            mock_validar.return_value = None
            mock_service.actualizar_usuario_completo.return_value = False

            result = UsuarioController.actualizar_usuario(1)
            assert result[1] == 400

    def test_actualizar_usuario_exception(self, app_context, mock_jsonify, mock_current_app, mock_request):
        """Test actualizar_usuario with exception."""
        mock_request.get_json.side_effect = Exception("Error")

        result = UsuarioController.actualizar_usuario(1)
        assert result[1] == 500

    def test_eliminar_usuario_exception(self, app_context, mock_jsonify, mock_current_app):
        """Test eliminar_usuario with exception."""
        with patch('src.controllers.usuario_controller.UsuarioService') as mock_service:
            mock_service.eliminar_usuario.side_effect = Exception("Error")

            result = UsuarioController.eliminar_usuario(1)
            assert result[1] == 500

    def test_validar_datos_registro_invalid_email(self, app_context, mock_jsonify, mock_current_app):
        """Test _validar_datos_registro with invalid email."""
        with patch('src.controllers.usuario_controller._validar_email') as mock_validar, \
             patch('src.controllers.usuario_controller.UsuarioService') as mock_service:
            mock_validar.return_value = False
            mock_service.buscar_por_email.return_value = None
            data = {
                'primer_nombre': 'Juan',
                'primer_apellido': 'Pérez',
                'email': 'invalid-email',
                'password': 'password123'
            }
            result = UsuarioController._validar_datos_registro(data)
            assert result[0] is None
            assert result[2] == 400

    def test_validar_datos_registro_short_password(self, app_context, mock_jsonify, mock_current_app):
        """Test _validar_datos_registro with short password."""
        with patch('src.controllers.usuario_controller._validar_email') as mock_validar, \
             patch('src.controllers.usuario_controller.UsuarioService') as mock_service:
            mock_validar.return_value = True
            mock_service.buscar_por_email.return_value = None
            data = {
                'primer_nombre': 'Juan',
                'primer_apellido': 'Pérez',
                'email': 'juan@example.com',
                'password': '12345'  # Less than 6 characters
            }
            result = UsuarioController._validar_datos_registro(data)
            assert result[0] is None
            assert result[2] == 400

    def test_generar_token_jwt_no_persona(self, app_context, mock_jsonify, mock_current_app):
        """Test _generar_token_jwt when usuario has no persona."""
        with patch('src.controllers.usuario_controller.jwt') as mock_jwt, \
             patch('src.controllers.usuario_controller.current_app') as mock_app:
            mock_app.config = {'SECRET_KEY': 'test-key'}
            mock_jwt.encode.return_value = 'fake_token'
            
            mock_usuario = Mock()
            mock_usuario.id = 1
            mock_usuario.persona = None
            mock_usuario.rol = None

            token = UsuarioController._generar_token_jwt(mock_usuario, 'test@example.com')
            assert token == 'fake_token'

    def test_generar_token_jwt_no_rol(self, app_context, mock_jsonify, mock_current_app):
        """Test _generar_token_jwt when usuario has no rol."""
        with patch('src.controllers.usuario_controller.jwt') as mock_jwt, \
             patch('src.controllers.usuario_controller.current_app') as mock_app:
            mock_app.config = {'SECRET_KEY': 'test-key'}
            mock_jwt.encode.return_value = 'fake_token'
            
            mock_usuario = Mock()
            mock_usuario.id = 1
            mock_persona = Mock()
            mock_persona.email = 'test@example.com'
            mock_usuario.persona = mock_persona
            mock_usuario.rol = None

            token = UsuarioController._generar_token_jwt(mock_usuario, 'test@example.com')
            assert token == 'fake_token'

    def test_validar_autenticacion_para_listado_success(self, app_context, mock_jsonify, mock_current_app, mock_g):
        """Test _validar_autenticacion_para_listado with authenticated user."""
        with patch('src.controllers.usuario_controller._obtener_usuario_actual') as mock_get_user:
            mock_user = Mock()
            mock_get_user.return_value = mock_user
            
            current_user, error_response, error_status = UsuarioController._validar_autenticacion_para_listado()
            assert current_user == mock_user
            assert error_response is None
            assert error_status is None

    def test_validar_autenticacion_para_listado_not_authenticated(self, app_context, mock_jsonify, mock_current_app, mock_g):
        """Test _validar_autenticacion_para_listado without authentication."""
        with patch('src.controllers.usuario_controller._obtener_usuario_actual') as mock_get_user:
            mock_get_user.return_value = None
            
            current_user, error_response, error_status = UsuarioController._validar_autenticacion_para_listado()
            assert current_user is None
            assert error_response is not None
            assert error_status == 401