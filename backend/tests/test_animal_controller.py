"""Tests para el controlador de animales."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from flask import Flask, g

from src.controllers.animal_controller import GanadoController
from src.models.animal import Ganado, EstadoGanado
from src.services.animal_service import GanadoService


class TestGanadoController:
    """Tests para GanadoController."""

    @patch('src.controllers.animal_controller.token_required')
    @patch('src.controllers.animal_controller.tenant_required')
    @patch.object(Ganado, 'from_dict')
    @patch.object(GanadoService, 'crear_ganado')
    @patch('src.controllers.animal_controller.emit_update')
    @patch('src.controllers.animal_controller.jsonify')
    def test_crear_ganado_success(self, mock_jsonify, mock_emit, mock_crear, mock_from_dict, mock_tenant_required, mock_token_required):
        """Test crear_ganado exitoso."""
        # Make decorators return the function unchanged
        mock_token_required.return_value = lambda f: f
        mock_tenant_required.return_value = lambda f: f

        app = Flask(__name__)
        with app.test_request_context(json={'nombre': 'Test Animal', 'fecha_nacimiento': '2020-01-01', 'estado': 'activo'}):
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

    @patch('src.controllers.animal_controller.token_required')
    @patch('src.controllers.animal_controller.tenant_required')
    @patch.object(GanadoService, 'crear_ganado')
    @patch('src.controllers.animal_controller.jsonify')
    def test_crear_ganado_error(self, mock_jsonify, mock_crear, mock_tenant_required, mock_token_required):
        """Test crear_ganado con error."""
        mock_token_required.return_value = lambda f: f
        mock_tenant_required.return_value = lambda f: f

        app = Flask(__name__)
        with app.test_request_context(json={'nombre': 'Test Animal'}):
            mock_crear.return_value = None

            mock_response = Mock()
            mock_response.json = {'status': 'error', 'message': 'Error al crear el ganado'}
            mock_jsonify.return_value = (mock_response, 400)

            result, status = GanadoController.crear_ganado()

            assert status == 400

    @patch('src.controllers.animal_controller.token_required')
    @patch('src.controllers.animal_controller.tenant_required')
    @patch('src.controllers.animal_controller.jsonify')
    def test_crear_ganado_value_error(self, mock_jsonify, mock_tenant_required, mock_token_required):
        """Test crear_ganado con ValueError."""
        mock_token_required.return_value = lambda f: f
        mock_tenant_required.return_value = lambda f: f

        app = Flask(__name__)
        with app.test_request_context(json={'nombre': 'Test Animal', 'fecha_nacimiento': 'invalid-date'}):
            mock_response = Mock()
            mock_response.json = {'status': 'error', 'message': 'Invalid date'}
            mock_jsonify.return_value = (mock_response, 400)

            with patch.object(Ganado, 'from_dict', side_effect=ValueError("Invalid date")):
                result, status = GanadoController.crear_ganado()

                assert status == 400

    @patch('src.controllers.animal_controller.token_required')
    @patch('src.controllers.animal_controller.tenant_required')
    @patch.object(GanadoService, 'obtener_ganado_detallado')
    @patch('src.controllers.animal_controller.jsonify')
    def test_obtener_ganado_success(self, mock_jsonify, mock_obtener, mock_tenant_required, mock_token_required):
        """Test obtener_ganado exitoso."""
        mock_token_required.return_value = lambda f: f
        mock_tenant_required.return_value = lambda f: f

        app = Flask(__name__)
        with app.test_request_context():
            mock_obtener.return_value = {'id': 1, 'nombre': 'Test Animal'}

            mock_response = Mock()
            mock_response.json = {'status': 'success', 'data': {'id': 1, 'nombre': 'Test Animal'}}
            mock_jsonify.return_value = (mock_response, 200)

            result, status = GanadoController.obtener_ganado(1)

            assert status == 200

    @patch('src.controllers.animal_controller.token_required')
    @patch('src.controllers.animal_controller.tenant_required')
    @patch.object(GanadoService, 'obtener_ganado_detallado')
    @patch('src.controllers.animal_controller.jsonify')
    def test_obtener_ganado_not_found(self, mock_jsonify, mock_obtener, mock_tenant_required, mock_token_required):
        """Test obtener_ganado cuando no existe."""
        mock_token_required.return_value = lambda f: f
        mock_tenant_required.return_value = lambda f: f

        app = Flask(__name__)
        with app.test_request_context():
            mock_obtener.return_value = None

            mock_response = Mock()
            mock_response.json = {'status': 'error', 'message': 'Ganado no encontrado'}
            mock_jsonify.return_value = (mock_response, 404)

            result, status = GanadoController.obtener_ganado(999)

            assert status == 404

    @patch('src.controllers.animal_controller.token_required')
    @patch('src.controllers.animal_controller.tenant_required')
    @patch.object(GanadoService, 'obtener_todos_ganados')
    @patch('src.controllers.animal_controller.jsonify')
    def test_obtener_todos_ganados_success(self, mock_jsonify, mock_obtener, mock_tenant_required, mock_token_required):
        """Test obtener_todos_ganados exitoso."""
        mock_token_required.return_value = lambda f: f
        mock_tenant_required.return_value = lambda f: f

        app = Flask(__name__)
        with app.test_request_context():
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

    @patch('src.controllers.animal_controller.token_required')
    @patch('src.controllers.animal_controller.tenant_required')
    @patch.object(GanadoService, 'obtener_ganado')
    @patch.object(GanadoService, 'actualizar_ganado')
    @patch('src.controllers.animal_controller.emit_update')
    @patch('src.controllers.animal_controller.jsonify')
    def test_actualizar_ganado_success(self, mock_jsonify, mock_emit, mock_actualizar, mock_obtener, mock_tenant_required, mock_token_required):
        """Test actualizar_ganado exitoso."""
        mock_token_required.return_value = lambda f: f
        mock_tenant_required.return_value = lambda f: f

        app = Flask(__name__)
        with app.test_request_context(json={'nombre': 'Updated Animal'}):
            mock_ganado = Mock()
            mock_ganado.to_dict.return_value = {'id': 1, 'nombre': 'Updated Animal'}
            mock_obtener.return_value = mock_ganado
            mock_actualizar.return_value = True

            mock_response = Mock()
            mock_response.json = {'status': 'success', 'message': 'Ganado actualizado exitosamente', 'data': {'id': 1, 'nombre': 'Updated Animal'}}
            mock_jsonify.return_value = (mock_response, 200)

            result, status = GanadoController.actualizar_ganado(1)

            assert status == 200

    @patch('src.controllers.animal_controller.token_required')
    @patch('src.controllers.animal_controller.tenant_required')
    @patch.object(GanadoService, 'obtener_ganado')
    @patch('src.controllers.animal_controller.jsonify')
    def test_actualizar_ganado_not_found(self, mock_jsonify, mock_obtener, mock_tenant_required, mock_token_required):
        """Test actualizar_ganado cuando no existe."""
        mock_token_required.return_value = lambda f: f
        mock_tenant_required.return_value = lambda f: f

        app = Flask(__name__)
        with app.test_request_context(json={'nombre': 'Updated Animal'}):
            mock_obtener.return_value = None

            mock_response = Mock()
            mock_response.json = {'status': 'error', 'message': 'Ganado no encontrado'}
            mock_jsonify.return_value = (mock_response, 404)

            result, status = GanadoController.actualizar_ganado(999)

            assert status == 404

    @patch('src.controllers.animal_controller.token_required')
    @patch('src.controllers.animal_controller.tenant_required')
    @patch.object(GanadoService, 'eliminar_ganado')
    @patch('src.controllers.animal_controller.emit_update')
    @patch('src.controllers.animal_controller.jsonify')
    def test_eliminar_ganado_success(self, mock_jsonify, mock_emit, mock_eliminar, mock_tenant_required, mock_token_required):
        """Test eliminar_ganado exitoso."""
        mock_token_required.return_value = lambda f: f
        mock_tenant_required.return_value = lambda f: f

        app = Flask(__name__)
        with app.test_request_context():
            mock_eliminar.return_value = True

            mock_response = Mock()
            mock_response.json = {'status': 'success', 'message': 'Ganado eliminado exitosamente'}
            mock_jsonify.return_value = (mock_response, 200)

            result, status = GanadoController.eliminar_ganado(1)

            assert status == 200

    @patch('src.controllers.animal_controller.token_required')
    @patch('src.controllers.animal_controller.tenant_required')
    @patch.object(GanadoService, 'eliminar_ganado')
    @patch('src.controllers.animal_controller.jsonify')
    def test_eliminar_ganado_error_message(self, mock_jsonify, mock_eliminar, mock_tenant_required, mock_token_required):
        """Test eliminar_ganado con mensaje de error."""
        mock_token_required.return_value = lambda f: f
        mock_tenant_required.return_value = lambda f: f

        app = Flask(__name__)
        with app.test_request_context():
            mock_eliminar.return_value = "Error message"

            mock_response = Mock()
            mock_response.json = {'status': 'error', 'message': 'Error message'}
            mock_jsonify.return_value = (mock_response, 400)

            result, status = GanadoController.eliminar_ganado(1)

            assert status == 400

    @patch('src.controllers.animal_controller.token_required')
    @patch('src.controllers.animal_controller.tenant_required')
    @patch.object(GanadoService, 'eliminar_ganado')
    @patch('src.controllers.animal_controller.jsonify')
    def test_eliminar_ganado_not_found(self, mock_jsonify, mock_eliminar, mock_tenant_required, mock_token_required):
        """Test eliminar_ganado cuando no existe."""
        mock_token_required.return_value = lambda f: f
        mock_tenant_required.return_value = lambda f: f

        app = Flask(__name__)
        with app.test_request_context():
            mock_eliminar.return_value = False

            mock_response = Mock()
            mock_response.json = {'status': 'error', 'message': 'Ganado no encontrado o error al eliminar'}
            mock_jsonify.return_value = (mock_response, 404)

            result, status = GanadoController.eliminar_ganado(999)

            assert status == 404

    @patch('src.controllers.animal_controller.token_required')
    @patch('src.controllers.animal_controller.tenant_required')
    @patch.object(GanadoService, 'buscar_por_potrero')
    @patch('src.controllers.animal_controller.jsonify')
    def test_obtener_ganados_por_potrero_success(self, mock_jsonify, mock_buscar, mock_tenant_required, mock_token_required):
        """Test obtener_ganados_por_potrero exitoso."""
        mock_token_required.return_value = lambda f: f
        mock_tenant_required.return_value = lambda f: f

        app = Flask(__name__)
        with app.test_request_context():
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

    @patch('src.controllers.animal_controller.token_required')
    @patch('src.controllers.animal_controller.tenant_required')
    @patch.object(GanadoService, 'buscar_por_codigo_qr')
    @patch.object(GanadoService, 'obtener_ganado_detallado')
    @patch('src.controllers.animal_controller.jsonify')
    def test_buscar_por_codigo_qr_success(self, mock_jsonify, mock_detalle, mock_buscar, mock_tenant_required, mock_token_required):
        """Test buscar_por_codigo_qr exitoso."""
        mock_token_required.return_value = lambda f: f
        mock_tenant_required.return_value = lambda f: f

        app = Flask(__name__)
        with app.test_request_context():
            mock_ganado = Mock()
            mock_ganado.id = 1
            mock_buscar.return_value = mock_ganado
            mock_detalle.return_value = {'id': 1, 'nombre': 'Test Animal'}

            mock_response = Mock()
            mock_response.json = {'status': 'success', 'data': {'id': 1, 'nombre': 'Test Animal'}}
            mock_jsonify.return_value = (mock_response, 200)

            result, status = GanadoController.buscar_por_codigo_qr('QR_1_Test')

            assert status == 200

    @patch('src.controllers.animal_controller.token_required')
    @patch('src.controllers.animal_controller.tenant_required')
    @patch.object(GanadoService, 'buscar_por_codigo_qr')
    @patch('src.controllers.animal_controller.jsonify')
    def test_buscar_por_codigo_qr_not_found(self, mock_jsonify, mock_buscar, mock_tenant_required, mock_token_required):
        """Test buscar_por_codigo_qr cuando no existe."""
        mock_token_required.return_value = lambda f: f
        mock_tenant_required.return_value = lambda f: f

        app = Flask(__name__)
        with app.test_request_context():
            mock_buscar.return_value = None

            mock_response = Mock()
            mock_response.json = {'status': 'error', 'message': 'Ganado no encontrado'}
            mock_jsonify.return_value = (mock_response, 404)

            result, status = GanadoController.buscar_por_codigo_qr('QR_INVALID')

            assert status == 404

