"""Tests para VacunacionController."""
import pytest
from unittest.mock import Mock, patch
from flask import Flask, g
from src.controllers.vacunacion_controller import VacunacionController


def _create_mock_user():
    """Helper para crear un usuario mock."""
    mock_user = Mock()
    mock_user.id = 1
    mock_user.tenant_id = 1
    mock_estado = Mock()
    mock_estado.value = 'activo'
    mock_user.estado = mock_estado
    mock_rol = Mock()
    mock_rol.nombre_rol = 'tenant_admin'
    mock_rol.rol = 'tenant_admin'
    mock_user.rol = mock_rol
    type(mock_user).tenant_id = 1
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


class TestVacunacionController:
    """Tests para VacunacionController."""

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.vacunacion_controller.VacunacionService')
    def test_obtener_todas_vacunaciones_success(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test obtener_todas_vacunaciones exitoso."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            g.tenant_id = 1
            
            mock_service.obtener_todas_vacunaciones.return_value = [
                {'id': 1, 'tipo_vacuna': 'Fiebre Aftosa'}
            ]

            result = VacunacionController.obtener_todas_vacunaciones()

            assert result[1] == 200
            mock_service.obtener_todas_vacunaciones.assert_called_once()

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.vacunacion_controller.VacunacionService')
    def test_obtener_todas_vacunaciones_exception(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test obtener_todas_vacunaciones con excepción."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            g.tenant_id = 1
            
            mock_service.obtener_todas_vacunaciones.side_effect = Exception("Error")

            result = VacunacionController.obtener_todas_vacunaciones()

            assert result[1] == 500

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.vacunacion_controller.VacunacionService')
    def test_obtener_vacunacion_por_id_success(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test obtener_vacunacion_por_id exitoso."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            g.tenant_id = 1
            
            mock_service.obtener_vacunacion_por_id.return_value = {
                'id': 1,
                'tipo_vacuna': 'Fiebre Aftosa'
            }

            result = VacunacionController.obtener_vacunacion_por_id(1)

            assert result[1] == 200
            mock_service.obtener_vacunacion_por_id.assert_called_once_with(1)

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.vacunacion_controller.VacunacionService')
    def test_obtener_vacunacion_por_id_not_found(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test obtener_vacunacion_por_id cuando no existe."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            g.tenant_id = 1
            
            mock_service.obtener_vacunacion_por_id.return_value = None

            result = VacunacionController.obtener_vacunacion_por_id(999)

            assert result[1] == 404

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.vacunacion_controller.VacunacionService')
    def test_crear_vacunacion_success(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test crear_vacunacion exitoso."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            json={
                'id_ganado': 1,
                'id_tipo_vacuna': 1,
                'fecha_vacunacion': '2023-01-01'
            },
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            g.tenant_id = 1
            
            mock_service.crear_vacunacion.return_value = {
                'id': 1,
                'tipo_vacuna': 'Fiebre Aftosa'
            }

            result = VacunacionController.crear_vacunacion()

            assert result[1] == 201
            mock_service.crear_vacunacion.assert_called_once()

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.vacunacion_controller.VacunacionService')
    def test_crear_vacunacion_no_data(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test crear_vacunacion sin datos."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            g.tenant_id = 1

            result = VacunacionController.crear_vacunacion()

            assert result[1] == 400

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.vacunacion_controller.VacunacionService')
    def test_crear_vacunacion_exception(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test crear_vacunacion con excepción."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            json={'id_ganado': 1},
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            g.tenant_id = 1
            
            mock_service.crear_vacunacion.side_effect = Exception("Error")

            result = VacunacionController.crear_vacunacion()

            assert result[1] == 500

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.vacunacion_controller.VacunacionService')
    def test_actualizar_vacunacion_success(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test actualizar_vacunacion exitoso."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            json={'tipo_vacuna': 'Fiebre Aftosa Actualizada'},
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            g.tenant_id = 1
            
            mock_service.actualizar_vacunacion.return_value = {
                'id': 1,
                'tipo_vacuna': 'Fiebre Aftosa Actualizada'
            }

            result = VacunacionController.actualizar_vacunacion(1)

            assert result[1] == 200
            mock_service.actualizar_vacunacion.assert_called_once()

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.vacunacion_controller.VacunacionService')
    def test_actualizar_vacunacion_not_found(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test actualizar_vacunacion cuando no existe."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            json={'tipo_vacuna': 'Actualizada'},
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            g.tenant_id = 1
            
            mock_service.actualizar_vacunacion.return_value = None

            result = VacunacionController.actualizar_vacunacion(999)

            assert result[1] == 404

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.vacunacion_controller.VacunacionService')
    def test_eliminar_vacunacion_success(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test eliminar_vacunacion exitoso."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            g.tenant_id = 1
            
            mock_service.eliminar_vacunacion.return_value = True

            result = VacunacionController.eliminar_vacunacion(1)

            assert result[1] == 200
            mock_service.eliminar_vacunacion.assert_called_once_with(1)

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.vacunacion_controller.VacunacionService')
    def test_eliminar_vacunacion_not_found(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test eliminar_vacunacion cuando no existe."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            g.tenant_id = 1
            
            mock_service.eliminar_vacunacion.return_value = False

            result = VacunacionController.eliminar_vacunacion(999)

            assert result[1] == 404

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.vacunacion_controller.VacunacionService')
    def test_obtener_tipos_vacuna_success(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test obtener_tipos_vacuna exitoso."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            g.tenant_id = 1
            
            mock_service.obtener_tipos_vacuna.return_value = [
                {'id': 1, 'tipo_vacuna': 'Fiebre Aftosa'}
            ]

            result = VacunacionController.obtener_tipos_vacuna()

            assert result[1] == 200
            mock_service.obtener_tipos_vacuna.assert_called_once()

