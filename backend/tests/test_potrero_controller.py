"""Tests para PotreroController."""
import pytest
from unittest.mock import Mock, patch
from flask import Flask, g
from src.controllers.potrero_controller import PotreroController
from src.database.db import DatabaseError


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


class TestPotreroController:
    """Tests para PotreroController."""

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_get_all_success(self, mock_service, mock_jwt, mock_usuario_service, app_context, mock_request):
        """Test get_all exitoso."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        g.current_user = mock_user
        g.tenant_id = 1
        
        mock_service.get_all.return_value = [{'id': 1, 'nombre': 'Potrero 1'}]
        mock_request.args = {}

        result = PotreroController.get_all()

        assert result[1] == 200
        mock_service.get_all.assert_called_once()

class TestPotreroController:
    """Tests para PotreroController."""

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_get_all_success(self, mock_service, mock_jwt, mock_usuario_service, app_context, mock_request):
        """Test get_all exitoso."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        g.current_user = mock_user
        g.tenant_id = 1
        
        mock_service.get_all.return_value = [{'id': 1, 'nombre': 'Potrero 1'}]
        mock_request.args = {}

        result = PotreroController.get_all()

        assert result[1] == 200
        mock_service.get_all.assert_called_once()

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_get_all_with_tenant_id(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test get_all con tenant_id."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'},
            query_string={'tenant_id': '1'}
        ):
            g.current_user = mock_user
            g.tenant_id = 1
            
            mock_service.get_all.return_value = [{'id': 1, 'nombre': 'Potrero 1'}]

            result = PotreroController.get_all()

            assert result[1] == 200
            mock_service.get_all.assert_called_once()

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_get_all_exception(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test get_all con excepción."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            g.tenant_id = 1
            
            mock_service.get_all.side_effect = Exception("Error")

            result = PotreroController.get_all()

            assert result[1] == 500

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_get_by_id_success(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test get_by_id exitoso."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            g.tenant_id = 1
            
            mock_service.get_by_id.return_value = {'id': 1, 'nombre': 'Potrero 1'}

            result = PotreroController.get_by_id(1)

            assert result[1] == 200
            mock_service.get_by_id.assert_called_once()

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_get_by_id_not_found(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test get_by_id cuando no existe."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            g.tenant_id = 1
            
            mock_service.get_by_id.side_effect = ValueError("No encontrado")

            result = PotreroController.get_by_id(999)

            assert result[1] == 404

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_get_by_id_database_error(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test get_by_id con error de base de datos."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            g.tenant_id = 1
            
            mock_service.get_by_id.side_effect = DatabaseError("DB Error")

            result = PotreroController.get_by_id(1)

            assert result[1] == 500

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_create_success(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test create exitoso."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            json={'nombre': 'Nuevo Potrero', 'capacidad': 10},
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            g.tenant_id = 1
            
            mock_service.create.return_value = {'id': 1, 'nombre': 'Nuevo Potrero'}

            result = PotreroController.create()

            assert result[1] == 201
            mock_service.create.assert_called_once()

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_create_no_data(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test create sin datos."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            g.tenant_id = 1

            result = PotreroController.create()

            assert result[1] == 400

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_create_exception(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test create con excepción."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            json={'nombre': 'Potrero'},
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            g.tenant_id = 1
            
            mock_service.create.side_effect = Exception("Error")

            result = PotreroController.create()

            assert result[1] == 500

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_update_success(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test update exitoso."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            json={'nombre': 'Potrero Actualizado'},
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            g.tenant_id = 1
            
            mock_service.update.return_value = {'id': 1, 'nombre': 'Potrero Actualizado'}

            result = PotreroController.update(1)

            assert result[1] == 200
            mock_service.update.assert_called_once()

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_update_not_found(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test update cuando no existe."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            json={'nombre': 'Potrero'},
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            g.tenant_id = 1
            
            mock_service.update.side_effect = ValueError("No encontrado")

            result = PotreroController.update(999)

            assert result[1] == 404

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_delete_success(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test delete exitoso."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            g.tenant_id = 1
            
            mock_service.delete.return_value = True

            result = PotreroController.delete(1)

            assert result[1] == 200
            mock_service.delete.assert_called_once_with(1)

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_delete_not_found(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test delete cuando no existe."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            g.tenant_id = 1
            
            mock_service.delete.side_effect = ValueError("No encontrado")

            result = PotreroController.delete(999)

            assert result[1] == 404

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_get_by_estado_success(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test get_by_estado exitoso."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            g.tenant_id = 1
            
            mock_service.get_all.return_value = [{'id': 1, 'estado': 'disponible'}]

            result = PotreroController.get_by_estado('disponible')

            assert result[1] == 200

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_actualizar_ocupacion_success(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test actualizar_ocupacion exitoso."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            g.tenant_id = 1
            
            mock_service.sincronizar_ocupacion.return_value = {'id': 1, 'ocupacion': 5}

            result = PotreroController.actualizar_ocupacion(1)

            assert result[1] == 200
            mock_service.sincronizar_ocupacion.assert_called_once_with(1)

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_get_tipos_pasto_success(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test get_tipos_pasto exitoso."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            g.tenant_id = 1
            
            mock_service.get_tipos_pasto.return_value = [{'id': 1, 'tipo_pasto': 'Césped'}]

            result = PotreroController.get_tipos_pasto()

            assert result[1] == 200

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_get_estados_potrero_success(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test get_estados_potrero exitoso."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            g.tenant_id = 1
            
            mock_service.get_estados_potrero.return_value = [{'id': 1, 'estado': 'disponible'}]

            result = PotreroController.get_estados_potrero()

            assert result[1] == 200

