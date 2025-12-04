"""Tests para el controlador de animales."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from flask import Flask, g

from src.controllers.animal_controller import GanadoController
from src.models.animal import Ganado, EstadoGanado
from src.services.animal_service import GanadoService


def _create_mock_user():
    """Helper para crear un usuario mock con todas las propiedades necesarias."""
    mock_user = Mock()
    mock_user.id = 1
    mock_user.tenant_id = 1
    mock_user.estado = Mock()
    mock_user.estado.value = 'activo'
    mock_rol = Mock()
    mock_rol.nombre_rol = 'tenant_admin'  # Cambiar a tenant_admin para que permission_required no bloquee
    mock_rol.rol = 'tenant_admin'
    mock_user.rol = mock_rol
    # Asegurar que tenant_id sea un atributo real
    type(mock_user).tenant_id = 1
    return mock_user


def _setup_mock_user():
    """Helper para configurar un usuario mock en g."""
    mock_user = _create_mock_user()
    g.current_user = mock_user
    g.tenant_id = 1
    g.jwt_payload = {'user_id': 1, 'role': 'tenant_admin', 'tenant_id': 1}


class TestGanadoController:
    """Tests para GanadoController."""

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch.object(Ganado, 'from_dict')
    @patch.object(GanadoService, 'crear_ganado')
    @patch('src.controllers.animal_controller.emit_update')
    @patch('src.controllers.animal_controller.jsonify')
    def test_crear_ganado_success(self, mock_jsonify, mock_emit, mock_crear, mock_from_dict, mock_jwt, mock_usuario_service):
        """Test crear_ganado exitoso."""
        # Mock JWT decode
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        
        # Mock UsuarioService.obtener_usuario
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user

        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            json={'nombre': 'Test Animal', 'fecha_nacimiento': '2020-01-01', 'estado': 'activo'},
            headers={'Authorization': 'Bearer fake_token'},
            query_string={'tenant_id': '1'}
        ):
            _setup_mock_user()
            # Mock Ganado.from_dict
            mock_ganado_obj = Mock()
            mock_ganado_obj.to_dict.return_value = {'id': 1, 'nombre': 'Test Animal'}
            mock_from_dict.return_value = mock_ganado_obj

            # Mock GanadoService.crear_ganado
            mock_ganado = Mock()
            mock_ganado.to_dict.return_value = {'id': 1, 'nombre': 'Test Animal'}
            mock_crear.return_value = mock_ganado

            # Mock jsonify - retorna una tupla (response, status_code)
            mock_response = Mock()
            mock_jsonify.return_value = mock_response

            result = GanadoController.crear_ganado()

            # El resultado es una tupla (response, status_code)
            assert isinstance(result, tuple)
            assert len(result) == 2
            assert result[1] == 201
            mock_crear.assert_called_once()
            mock_jsonify.assert_called_once()

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch.object(GanadoService, 'crear_ganado')
    @patch('src.controllers.animal_controller.jsonify')
    def test_crear_ganado_error(self, mock_jsonify, mock_crear, mock_jwt, mock_usuario_service):
        """Test crear_ganado con error."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'tenant_admin', 'tenant_id': 1}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user

        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            json={'nombre': 'Test Animal'},
            headers={'Authorization': 'Bearer fake_token'},
            query_string={'tenant_id': '1'}
        ):
            _setup_mock_user()
            mock_crear.return_value = None

            from flask import jsonify
            mock_response = jsonify({
                'status': 'error',
                'message': 'No se pudo crear el animal',
                'success': False
            })
            mock_response.status_code = 500
            mock_jsonify.return_value = mock_response

            result, status = GanadoController.crear_ganado()

            assert status == 500
            # Verificar que se llamó con tenant_id_override
            mock_crear.assert_called_once()
            call_args = mock_crear.call_args
            # Verificar que se pasó tenant_id_override como keyword argument
            assert call_args.kwargs.get('tenant_id_override') == 1

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.animal_controller.jsonify')
    def test_crear_ganado_value_error(self, mock_jsonify, mock_jwt, mock_usuario_service):
        """Test crear_ganado con ValueError."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'tenant_admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user

        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            json={'nombre': 'Test Animal', 'fecha_nacimiento': 'invalid-date'},
            headers={'Authorization': 'Bearer fake_token'},
            query_string={'tenant_id': '1'}
        ):
            _setup_mock_user()
            mock_response = Mock()
            mock_response.json = {'status': 'error', 'message': 'Invalid date'}
            mock_jsonify.return_value = (mock_response, 400)

            with patch.object(Ganado, 'from_dict', side_effect=ValueError("Invalid date")):
                result, status = GanadoController.crear_ganado()

                assert status == 400

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch.object(GanadoService, 'obtener_ganado_detallado')
    @patch('src.controllers.animal_controller.jsonify')
    def test_obtener_ganado_success(self, mock_jsonify, mock_obtener, mock_jwt, mock_usuario_service):
        """Test obtener_ganado exitoso."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'tenant_admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user

        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'},
            query_string={'tenant_id': '1'}
        ):
            _setup_mock_user()
            mock_obtener.return_value = {'id': 1, 'nombre': 'Test Animal'}

            mock_response = Mock()
            mock_response.json = {'status': 'success', 'data': {'id': 1, 'nombre': 'Test Animal'}}
            mock_jsonify.return_value = (mock_response, 200)

            result, status = GanadoController.obtener_ganado(1)

            assert status == 200

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch.object(GanadoService, 'obtener_ganado_detallado')
    @patch('src.controllers.animal_controller.jsonify')
    def test_obtener_ganado_not_found(self, mock_jsonify, mock_obtener, mock_jwt, mock_usuario_service):
        """Test obtener_ganado cuando no existe."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'tenant_admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user

        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'},
            query_string={'tenant_id': '1'}
        ):
            _setup_mock_user()
            mock_obtener.return_value = None

            mock_response = Mock()
            mock_response.json = {'status': 'error', 'message': 'Ganado no encontrado'}
            mock_jsonify.return_value = (mock_response, 404)

            result, status = GanadoController.obtener_ganado(999)

            assert status == 404

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch.object(GanadoService, 'obtener_todos_ganados')
    @patch('src.controllers.animal_controller.jsonify')
    def test_obtener_todos_ganados_success(self, mock_jsonify, mock_obtener, mock_jwt, mock_usuario_service):
        """Test obtener_todos_ganados exitoso."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'tenant_admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user

        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'},
            query_string={'tenant_id': '1'}
        ):
            _setup_mock_user()
            mock_ganado1 = Mock()
            mock_ganado1.to_dict.return_value = {'id': 1, 'nombre': 'Animal 1'}
            mock_ganado2 = Mock()
            mock_ganado2.to_dict.return_value = {'id': 2, 'nombre': 'Animal 2'}

            mock_obtener.return_value = [mock_ganado1, mock_ganado2]

            mock_response = Mock()
            mock_response.json = {'status': 'success', 'data': [{'id': 1, 'nombre': 'Animal 1'}, {'id': 2, 'nombre': 'Animal 2'}]}
            mock_jsonify.return_value = (mock_response, 200)

            result, status = GanadoController.obtener_todos_ganados()

            assert status == 200

    @patch('src.controllers.animal_controller.token_required')
    @patch('src.controllers.animal_controller.tenant_required')
    @patch.object(GanadoService, 'obtener_estados_ganado')
    @patch('src.controllers.animal_controller.jsonify')
    def test_obtener_estados_ganado_success(self, mock_jsonify, mock_obtener, mock_tenant_required, mock_token_required):
        """Test obtener_estados_ganado exitoso."""
        mock_token_required.return_value = lambda f: f
        mock_tenant_required.return_value = lambda f: f

        app = Flask(__name__)
        with app.test_request_context():
            mock_obtener.return_value = [
                {'id': 1, 'estado': 'activo'},
                {'id': 2, 'estado': 'inactivo'}
            ]

            mock_response = Mock()
            mock_response.json = {'status': 'success', 'data': [{'id': 1, 'estado': 'activo'}, {'id': 2, 'estado': 'inactivo'}]}
            mock_jsonify.return_value = (mock_response, 200)

            result, status = GanadoController.obtener_estados_ganado()

            assert status == 200

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch.object(GanadoService, 'obtener_ganado')
    @patch.object(GanadoService, 'actualizar_ganado')
    @patch('src.controllers.animal_controller.emit_update')
    @patch('src.controllers.animal_controller.jsonify')
    def test_actualizar_ganado_success(self, mock_jsonify, mock_emit, mock_actualizar, mock_obtener, mock_jwt, mock_usuario_service):
        """Test actualizar_ganado exitoso."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'tenant_admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user

        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            json={'nombre': 'Updated Animal'},
            headers={'Authorization': 'Bearer fake_token'},
            query_string={'tenant_id': '1'}
        ):
            _setup_mock_user()
            mock_ganado = Mock()
            mock_ganado.to_dict.return_value = {'id': 1, 'nombre': 'Updated Animal'}
            mock_obtener.return_value = mock_ganado
            mock_actualizar.return_value = True

            mock_response = Mock()
            mock_response.json = {'status': 'success', 'message': 'Ganado actualizado exitosamente', 'data': {'id': 1, 'nombre': 'Updated Animal'}}
            mock_jsonify.return_value = (mock_response, 200)

            result, status = GanadoController.actualizar_ganado(1)

            assert status == 200

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch.object(GanadoService, 'obtener_ganado')
    @patch('src.controllers.animal_controller.jsonify')
    def test_actualizar_ganado_not_found(self, mock_jsonify, mock_obtener, mock_jwt, mock_usuario_service):
        """Test actualizar_ganado cuando no existe."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'tenant_admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user

        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            json={'nombre': 'Updated Animal'},
            headers={'Authorization': 'Bearer fake_token'},
            query_string={'tenant_id': '1'}
        ):
            _setup_mock_user()
            mock_obtener.return_value = None

            mock_response = Mock()
            mock_response.json = {'status': 'error', 'message': 'Ganado no encontrado'}
            mock_jsonify.return_value = (mock_response, 404)

            result, status = GanadoController.actualizar_ganado(999)

            assert status == 404

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch.object(GanadoService, 'eliminar_ganado')
    @patch('src.controllers.animal_controller.emit_update')
    @patch('src.controllers.animal_controller.jsonify')
    def test_eliminar_ganado_success(self, mock_jsonify, mock_emit, mock_eliminar, mock_jwt, mock_usuario_service):
        """Test eliminar_ganado exitoso."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'tenant_admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user

        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'},
            query_string={'tenant_id': '1'}
        ):
            _setup_mock_user()
            mock_eliminar.return_value = True

            mock_response = Mock()
            mock_response.json = {'status': 'success', 'message': 'Ganado eliminado exitosamente'}
            mock_jsonify.return_value = (mock_response, 200)

            result, status = GanadoController.eliminar_ganado(1)

            assert status == 200

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch.object(GanadoService, 'eliminar_ganado')
    @patch('src.controllers.animal_controller.jsonify')
    def test_eliminar_ganado_error_message(self, mock_jsonify, mock_eliminar, mock_jwt, mock_usuario_service):
        """Test eliminar_ganado con mensaje de error."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'tenant_admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user

        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'},
            query_string={'tenant_id': '1'}
        ):
            _setup_mock_user()
            mock_eliminar.return_value = "Error message"

            mock_response = Mock()
            mock_response.json = {'status': 'error', 'message': 'Error message'}
            mock_jsonify.return_value = (mock_response, 400)

            result, status = GanadoController.eliminar_ganado(1)

            assert status == 400

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch.object(GanadoService, 'eliminar_ganado')
    @patch('src.controllers.animal_controller.jsonify')
    def test_eliminar_ganado_not_found(self, mock_jsonify, mock_eliminar, mock_jwt, mock_usuario_service):
        """Test eliminar_ganado cuando no existe."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'tenant_admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user

        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'},
            query_string={'tenant_id': '1'}
        ):
            _setup_mock_user()
            mock_eliminar.return_value = False

            mock_response = Mock()
            mock_response.json = {'status': 'error', 'message': 'Ganado no encontrado o error al eliminar'}
            mock_jsonify.return_value = (mock_response, 404)

            result, status = GanadoController.eliminar_ganado(999)

            assert status == 404

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch.object(GanadoService, 'buscar_por_potrero')
    @patch('src.controllers.animal_controller.jsonify')
    def test_obtener_ganados_por_potrero_success(self, mock_jsonify, mock_buscar, mock_jwt, mock_usuario_service):
        """Test obtener_ganados_por_potrero exitoso."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'tenant_admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user

        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'},
            query_string={'tenant_id': '1'}
        ):
            _setup_mock_user()
            mock_ganado1 = Mock()
            mock_ganado1.to_dict.return_value = {'id': 1, 'nombre': 'Animal 1'}
            mock_ganado2 = Mock()
            mock_ganado2.to_dict.return_value = {'id': 2, 'nombre': 'Animal 2'}

            mock_buscar.return_value = [mock_ganado1, mock_ganado2]

            mock_response = Mock()
            mock_response.json = {'status': 'success', 'data': [{'id': 1, 'nombre': 'Animal 1'}, {'id': 2, 'nombre': 'Animal 2'}]}
            mock_jsonify.return_value = (mock_response, 200)

            result, status = GanadoController.obtener_ganados_por_potrero(1)

            assert status == 200

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch.object(GanadoService, 'buscar_por_codigo_qr')
    @patch.object(GanadoService, 'obtener_ganado_detallado')
    @patch('src.controllers.animal_controller.jsonify')
    def test_buscar_por_codigo_qr_success(self, mock_jsonify, mock_detalle, mock_buscar, mock_jwt, mock_usuario_service):
        """Test buscar_por_codigo_qr exitoso."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'tenant_admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user

        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'},
            query_string={'tenant_id': '1'}
        ):
            _setup_mock_user()
            mock_ganado = Mock()
            mock_ganado.id = 1
            mock_buscar.return_value = mock_ganado
            mock_detalle.return_value = {'id': 1, 'nombre': 'Test Animal'}

            mock_response = Mock()
            mock_response.json = {'status': 'success', 'data': {'id': 1, 'nombre': 'Test Animal'}}
            mock_jsonify.return_value = (mock_response, 200)

            result, status = GanadoController.buscar_por_codigo_qr('QR_1_Test')

            assert status == 200

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch.object(GanadoService, 'buscar_por_codigo_qr')
    @patch('src.controllers.animal_controller.jsonify')
    def test_buscar_por_codigo_qr_not_found(self, mock_jsonify, mock_buscar, mock_jwt, mock_usuario_service):
        """Test buscar_por_codigo_qr cuando no existe."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'tenant_admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user

        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'},
            query_string={'tenant_id': '1'}
        ):
            _setup_mock_user()
            mock_buscar.return_value = None

            mock_response = Mock()
            mock_response.json = {'status': 'error', 'message': 'Ganado no encontrado'}
            mock_jsonify.return_value = (mock_response, 404)

            result, status = GanadoController.buscar_por_codigo_qr('QR_INVALID')

            assert status == 404

