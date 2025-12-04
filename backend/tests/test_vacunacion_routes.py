"""Tests para las rutas de vacunaciones."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask, g
from src.routes.vacunacion_routes import vacunacion_bp


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
    return mock_user


class TestVacunacionRoutes:
    """Tests para vacunacion_routes."""

    @pytest.fixture(autouse=True)
    def setup_app(self, app):
        """Setup test client and app context."""
        app.config['SECRET_KEY'] = 'test-secret-key'
        app.register_blueprint(vacunacion_bp, url_prefix='/api/vacunaciones')
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

    def teardown_method(self):
        """Clean up after each test."""
        if hasattr(self, 'app_context'):
            self.app_context.pop()

    def test_blueprint_creation(self):
        """Test que el blueprint de vacunaciones se crea correctamente."""
        assert vacunacion_bp is not None
        assert vacunacion_bp.name == "vacunacion"

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.routes.vacunacion_routes.VacunacionController')
    def test_get_vacunaciones_success(self, mock_controller_class, mock_jwt, mock_usuario_service):
        """Test GET /api/vacunaciones/ success."""
        from flask import jsonify
        
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        mock_response = jsonify({'data': [], 'success': True})
        mock_response.status_code = 200
        mock_controller_class.obtener_todas_vacunaciones.return_value = (mock_response, 200)

        response = self.client.get('/api/vacunaciones/', headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 200
        mock_controller_class.obtener_todas_vacunaciones.assert_called_once()

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.vacunacion_controller.VacunacionService')
    def test_get_vacunaciones_exception(self, mock_service, mock_jwt, mock_usuario_service):
        """Test GET /api/vacunaciones/ with exception."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        mock_service.obtener_todas_vacunaciones.side_effect = Exception("Service error")

        response = self.client.get('/api/vacunaciones/', headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 500

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.routes.vacunacion_routes.VacunacionController')
    def test_get_vacunacion_success(self, mock_controller_class, mock_jwt, mock_usuario_service):
        """Test GET /api/vacunaciones/<id> success."""
        from flask import jsonify
        
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        mock_response = jsonify({'data': {'id': 1, 'fecha_aplicacion': '2024-01-01'}, 'success': True})
        mock_response.status_code = 200
        mock_controller_class.obtener_vacunacion_por_id.return_value = (mock_response, 200)

        response = self.client.get('/api/vacunaciones/1', headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 200
        mock_controller_class.obtener_vacunacion_por_id.assert_called_once_with(1)

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.routes.vacunacion_routes.VacunacionController')
    def test_get_vacunacion_not_found(self, mock_controller_class, mock_jwt, mock_usuario_service):
        """Test GET /api/vacunaciones/<id> not found."""
        from flask import jsonify
        
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        mock_response = jsonify({'error': 'Vacunación no encontrada', 'success': False})
        mock_response.status_code = 404
        mock_controller_class.obtener_vacunacion_por_id.return_value = (mock_response, 404)

        response = self.client.get('/api/vacunaciones/999', headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 404

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.vacunacion_controller.VacunacionService')
    def test_get_vacunacion_exception(self, mock_service, mock_jwt, mock_usuario_service):
        """Test GET /api/vacunaciones/<id> with exception."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        mock_service.obtener_vacunacion_por_id.side_effect = Exception("Service error")

        response = self.client.get('/api/vacunaciones/1', headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 500

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.routes.vacunacion_routes.VacunacionController')
    def test_create_vacunacion_success(self, mock_controller_class, mock_jwt, mock_usuario_service):
        """Test POST /api/vacunaciones/ success."""
        from flask import jsonify
        
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        mock_response = jsonify({'data': {'id': 1, 'fecha_aplicacion': '2024-01-01'}, 'success': True})
        mock_response.status_code = 201
        mock_controller_class.crear_vacunacion.return_value = (mock_response, 201)

        response = self.client.post('/api/vacunaciones/', json={'fecha_aplicacion': '2024-01-01'}, headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 201
        mock_controller_class.crear_vacunacion.assert_called_once()

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.vacunacion_controller.Vacunacion')
    def test_create_vacunacion_exception(self, mock_vacunacion_class, mock_jwt, mock_usuario_service):
        """Test POST /api/vacunaciones/ with exception."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin', 'tenant_id': 1}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        # Make from_dict raise an exception
        mock_vacunacion_class.from_dict.side_effect = Exception("Validation error")

        response = self.client.post('/api/vacunaciones/', json={
            'id_animal': 1,
            'id_tipo_vacuna': 1,
            'responsable': 'Veterinario',
            'fecha_aplicacion': '2024-01-01'
        }, headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 500
        data = response.get_json()
        assert data['status'] == 'error'

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.routes.vacunacion_routes.VacunacionController')
    def test_update_vacunacion_success(self, mock_controller_class, mock_jwt, mock_usuario_service):
        """Test PUT /api/vacunaciones/<id> success."""
        from flask import jsonify
        
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        mock_response = jsonify({'data': {'id': 1, 'fecha_aplicacion': '2024-02-01'}, 'success': True})
        mock_response.status_code = 200
        mock_controller_class.actualizar_vacunacion.return_value = (mock_response, 200)

        response = self.client.put('/api/vacunaciones/1', json={'fecha_aplicacion': '2024-02-01'}, headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 200
        mock_controller_class.actualizar_vacunacion.assert_called_once_with(1)

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.routes.vacunacion_routes.VacunacionController')
    def test_update_vacunacion_not_found(self, mock_controller_class, mock_jwt, mock_usuario_service):
        """Test PUT /api/vacunaciones/<id> not found."""
        from flask import jsonify
        
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        mock_response = jsonify({'error': 'Vacunación no encontrada', 'success': False})
        mock_response.status_code = 404
        mock_controller_class.actualizar_vacunacion.return_value = (mock_response, 404)

        response = self.client.put('/api/vacunaciones/999', json={'fecha_aplicacion': '2024-02-01'}, headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 404

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.vacunacion_controller.VacunacionService')
    def test_update_vacunacion_exception(self, mock_service, mock_jwt, mock_usuario_service):
        """Test PUT /api/vacunaciones/<id> with exception."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        mock_service.actualizar_vacunacion.side_effect = Exception("Service error")

        response = self.client.put('/api/vacunaciones/1', json={'fecha_aplicacion': '2024-02-01'}, headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 500

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.routes.vacunacion_routes.VacunacionController')
    def test_delete_vacunacion_success(self, mock_controller_class, mock_jwt, mock_usuario_service):
        """Test DELETE /api/vacunaciones/<id> success."""
        from flask import jsonify
        
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        mock_response = jsonify({'message': 'Vacunación eliminada', 'success': True})
        mock_response.status_code = 200
        mock_controller_class.eliminar_vacunacion.return_value = (mock_response, 200)

        response = self.client.delete('/api/vacunaciones/1', headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 200
        mock_controller_class.eliminar_vacunacion.assert_called_once_with(1)

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.routes.vacunacion_routes.VacunacionController')
    def test_delete_vacunacion_not_found(self, mock_controller_class, mock_jwt, mock_usuario_service):
        """Test DELETE /api/vacunaciones/<id> not found."""
        from flask import jsonify
        
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        mock_response = jsonify({'error': 'Vacunación no encontrada', 'success': False})
        mock_response.status_code = 404
        mock_controller_class.eliminar_vacunacion.return_value = (mock_response, 404)

        response = self.client.delete('/api/vacunaciones/999', headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 404

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.vacunacion_controller.VacunacionService')
    def test_delete_vacunacion_exception(self, mock_service, mock_jwt, mock_usuario_service):
        """Test DELETE /api/vacunaciones/<id> with exception."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        mock_service.eliminar_vacunacion.side_effect = Exception("Service error")

        response = self.client.delete('/api/vacunaciones/1', headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 500

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.routes.vacunacion_routes.VacunacionController')
    def test_get_tipos_vacuna_success(self, mock_controller_class, mock_jwt, mock_usuario_service):
        """Test GET /api/vacunaciones/tipos-vacuna success."""
        from flask import jsonify
        
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        mock_response = jsonify({'data': [{'id': 1, 'nombre_vacuna': 'Vacuna A'}], 'success': True})
        mock_response.status_code = 200
        mock_controller_class.obtener_tipos_vacuna.return_value = (mock_response, 200)

        response = self.client.get('/api/vacunaciones/tipos-vacuna', headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 200
        mock_controller_class.obtener_tipos_vacuna.assert_called_once()

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.vacunacion_controller.VacunacionService')
    def test_get_tipos_vacuna_exception(self, mock_service, mock_jwt, mock_usuario_service):
        """Test GET /api/vacunaciones/tipos-vacuna with exception."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        mock_service.obtener_tipos_vacuna.side_effect = Exception("Service error")

        response = self.client.get('/api/vacunaciones/tipos-vacuna', headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 500
