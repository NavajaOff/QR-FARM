"""Tests para el controlador de animales."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from flask import Flask

from src.controllers.animal_controller import GanadoController
from src.models.animal import Ganado, EstadoGanado
from src.services.animal_service import GanadoService


class TestGanadoController:
    """Tests para GanadoController."""

    @patch.object(GanadoService, 'crear_ganado')
    @patch('src.controllers.animal_controller.emit_update')
    @patch('src.controllers.animal_controller.jsonify')
    @patch('src.controllers.animal_controller.request')
    def test_crear_ganado_success(self, mock_request, mock_jsonify, mock_emit, mock_crear):
        """Test crear_ganado exitoso."""
        app = Flask(__name__)
        with app.test_request_context():
            mock_request.get_json.return_value = {
                'nombre': 'Test Animal',
                'fecha_nacimiento': '2020-01-01',
                'estado': 'activo'
            }

            mock_ganado = Mock()
            mock_ganado.to_dict.return_value = {'id': 1, 'nombre': 'Test Animal'}
            mock_crear.return_value = mock_ganado

            mock_response = Mock()
            mock_response.json = {'status': 'success', 'message': 'Ganado creado exitosamente', 'data': {'id': 1, 'nombre': 'Test Animal'}}
            mock_jsonify.return_value = (mock_response, 201)

            result, status = GanadoController.crear_ganado()

            assert status == 201
            mock_crear.assert_called_once()

    @patch.object(GanadoService, 'crear_ganado')
    @patch('src.controllers.animal_controller.jsonify')
    @patch('src.controllers.animal_controller.request')
    def test_crear_ganado_error(self, mock_request, mock_jsonify, mock_crear):
        """Test crear_ganado con error."""
        app = Flask(__name__)
        with app.test_request_context():
            mock_request.get_json.return_value = {
                'nombre': 'Test Animal'
            }

            mock_crear.return_value = None

            mock_response = Mock()
            mock_response.json = {'status': 'error', 'message': 'Error al crear el ganado'}
            mock_jsonify.return_value = (mock_response, 400)

            result, status = GanadoController.crear_ganado()

            assert status == 400

    @patch('src.controllers.animal_controller.request')
    @patch('src.controllers.animal_controller.jsonify')
    def test_crear_ganado_value_error(self, mock_jsonify, mock_request):
        """Test crear_ganado con ValueError."""
        app = Flask(__name__)
        with app.test_request_context():
            mock_request.get_json.return_value = {
                'nombre': 'Test Animal',
                'fecha_nacimiento': 'invalid-date'
            }

            mock_response = Mock()
            mock_response.json = {'status': 'error', 'message': 'Invalid date'}
            mock_jsonify.return_value = (mock_response, 400)

            with patch.object(Ganado, 'from_dict', side_effect=ValueError("Invalid date")):
                result, status = GanadoController.crear_ganado()

                assert status == 400

    @patch.object(GanadoService, 'obtener_ganado_detallado')
    @patch('src.controllers.animal_controller.jsonify')
    def test_obtener_ganado_success(self, mock_jsonify, mock_obtener):
        """Test obtener_ganado exitoso."""
        app = Flask(__name__)
        with app.test_request_context():
            mock_obtener.return_value = {'id': 1, 'nombre': 'Test Animal'}

            mock_response = Mock()
            mock_response.json = {'status': 'success', 'data': {'id': 1, 'nombre': 'Test Animal'}}
            mock_jsonify.return_value = (mock_response, 200)

            result, status = GanadoController.obtener_ganado(1)

            assert status == 200

    @patch.object(GanadoService, 'obtener_ganado_detallado')
    @patch('src.controllers.animal_controller.jsonify')
    def test_obtener_ganado_not_found(self, mock_jsonify, mock_obtener):
        """Test obtener_ganado cuando no existe."""
        app = Flask(__name__)
        with app.test_request_context():
            mock_obtener.return_value = None

            mock_response = Mock()
            mock_response.json = {'status': 'error', 'message': 'Ganado no encontrado'}
            mock_jsonify.return_value = (mock_response, 404)

            result, status = GanadoController.obtener_ganado(999)

            assert status == 404

    @patch.object(GanadoService, 'obtener_todos_ganados')
    @patch('src.controllers.animal_controller.jsonify')
    def test_obtener_todos_ganados_success(self, mock_jsonify, mock_obtener):
        """Test obtener_todos_ganados exitoso."""
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

    @patch.object(GanadoService, 'obtener_estados_ganado')
    @patch('src.controllers.animal_controller.jsonify')
    def test_obtener_estados_ganado_success(self, mock_jsonify, mock_obtener):
        """Test obtener_estados_ganado exitoso."""
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

    @patch.object(GanadoService, 'obtener_ganado')
    @patch.object(GanadoService, 'actualizar_ganado')
    @patch('src.controllers.animal_controller.emit_update')
    @patch('src.controllers.animal_controller.jsonify')
    @patch('src.controllers.animal_controller.request')
    def test_actualizar_ganado_success(self, mock_request, mock_jsonify, mock_emit, mock_actualizar, mock_obtener):
        """Test actualizar_ganado exitoso."""
        app = Flask(__name__)
        with app.test_request_context():
            mock_request.get_json.return_value = {
                'nombre': 'Updated Animal'
            }

            mock_ganado = Mock()
            mock_ganado.to_dict.return_value = {'id': 1, 'nombre': 'Updated Animal'}
            mock_obtener.return_value = mock_ganado
            mock_actualizar.return_value = True

            mock_response = Mock()
            mock_response.json = {'status': 'success', 'message': 'Ganado actualizado exitosamente', 'data': {'id': 1, 'nombre': 'Updated Animal'}}
            mock_jsonify.return_value = (mock_response, 200)

            result, status = GanadoController.actualizar_ganado(1)

            assert status == 200

    @patch.object(GanadoService, 'obtener_ganado')
    @patch('src.controllers.animal_controller.request')
    @patch('src.controllers.animal_controller.jsonify')
    def test_actualizar_ganado_not_found(self, mock_jsonify, mock_request, mock_obtener):
        """Test actualizar_ganado cuando no existe."""
        app = Flask(__name__)
        with app.test_request_context():
            mock_obtener.return_value = None
            mock_request.get_json.return_value = {'nombre': 'Updated Animal'}

            mock_response = Mock()
            mock_response.json = {'status': 'error', 'message': 'Ganado no encontrado'}
            mock_jsonify.return_value = (mock_response, 404)

            result, status = GanadoController.actualizar_ganado(999)

            assert status == 404

    @patch.object(GanadoService, 'eliminar_ganado')
    @patch('src.controllers.animal_controller.emit_update')
    @patch('src.controllers.animal_controller.jsonify')
    def test_eliminar_ganado_success(self, mock_jsonify, mock_emit, mock_eliminar):
        """Test eliminar_ganado exitoso."""
        app = Flask(__name__)
        with app.test_request_context():
            mock_eliminar.return_value = True

            mock_response = Mock()
            mock_response.json = {'status': 'success', 'message': 'Ganado eliminado exitosamente'}
            mock_jsonify.return_value = (mock_response, 200)

            result, status = GanadoController.eliminar_ganado(1)

            assert status == 200

    @patch.object(GanadoService, 'eliminar_ganado')
    @patch('src.controllers.animal_controller.jsonify')
    def test_eliminar_ganado_error_message(self, mock_jsonify, mock_eliminar):
        """Test eliminar_ganado con mensaje de error."""
        app = Flask(__name__)
        with app.test_request_context():
            mock_eliminar.return_value = "Error message"

            mock_response = Mock()
            mock_response.json = {'status': 'error', 'message': 'Error message'}
            mock_jsonify.return_value = (mock_response, 400)

            result, status = GanadoController.eliminar_ganado(1)

            assert status == 400

    @patch.object(GanadoService, 'eliminar_ganado')
    @patch('src.controllers.animal_controller.jsonify')
    def test_eliminar_ganado_not_found(self, mock_jsonify, mock_eliminar):
        """Test eliminar_ganado cuando no existe."""
        app = Flask(__name__)
        with app.test_request_context():
            mock_eliminar.return_value = False

            mock_response = Mock()
            mock_response.json = {'status': 'error', 'message': 'Ganado no encontrado o error al eliminar'}
            mock_jsonify.return_value = (mock_response, 404)

            result, status = GanadoController.eliminar_ganado(999)

            assert status == 404

    @patch.object(GanadoService, 'buscar_por_potrero')
    @patch('src.controllers.animal_controller.jsonify')
    def test_obtener_ganados_por_potrero_success(self, mock_jsonify, mock_buscar):
        """Test obtener_ganados_por_potrero exitoso."""
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

    @patch.object(GanadoService, 'buscar_por_codigo_qr')
    @patch.object(GanadoService, 'obtener_ganado_detallado')
    @patch('src.controllers.animal_controller.jsonify')
    def test_buscar_por_codigo_qr_success(self, mock_jsonify, mock_detalle, mock_buscar):
        """Test buscar_por_codigo_qr exitoso."""
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

    @patch.object(GanadoService, 'buscar_por_codigo_qr')
    @patch('src.controllers.animal_controller.jsonify')
    def test_buscar_por_codigo_qr_not_found(self, mock_jsonify, mock_buscar):
        """Test buscar_por_codigo_qr cuando no existe."""
        app = Flask(__name__)
        with app.test_request_context():
            mock_buscar.return_value = None

            mock_response = Mock()
            mock_response.json = {'status': 'error', 'message': 'Ganado no encontrado'}
            mock_jsonify.return_value = (mock_response, 404)

            result, status = GanadoController.buscar_por_codigo_qr('QR_INVALID')

            assert status == 404

