"""Tests para las rutas de potreros."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask, g
from src.routes.potrero_routes import potrero_bp


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


class TestPotreroRoutes:
    """Tests para potrero_routes."""

    @pytest.fixture(autouse=True)
    def setup_app(self, app):
        """Setup test client and app context."""
        app.config['SECRET_KEY'] = 'test-secret-key'
        app.register_blueprint(potrero_bp, url_prefix='/api/potreros')
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

    def teardown_method(self):
        """Clean up after each test."""
        if hasattr(self, 'app_context'):
            self.app_context.pop()

    def test_blueprint_creation(self):
        """Test que el blueprint de potreros se crea correctamente."""
        assert potrero_bp is not None
        assert potrero_bp.name == "potrero"

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_get_all_success(self, mock_service, mock_jwt, mock_usuario_service):
        """Test GET /api/potreros/ success."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin', 'tenant_id': 1}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        mock_service.get_all.return_value = []

        response = self.client.get('/api/potreros/', headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_get_all_exception(self, mock_service, mock_jwt, mock_usuario_service):
        """Test GET /api/potreros/ with exception."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin', 'tenant_id': 1}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        mock_service.get_all.side_effect = Exception("Service error")

        response = self.client.get('/api/potreros/', headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 500
        data = response.get_json()
        assert data['success'] is False

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_get_by_id_success(self, mock_service, mock_jwt, mock_usuario_service):
        """Test GET /api/potreros/<id> success."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin', 'tenant_id': 1}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        mock_service.get_by_id.return_value = {'id': 1, 'nombre': 'Potrero 1'}

        response = self.client.get('/api/potreros/1', headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['id'] == 1

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_get_by_id_not_found(self, mock_service, mock_jwt, mock_usuario_service):
        """Test GET /api/potreros/<id> not found."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin', 'tenant_id': 1}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        mock_service.get_by_id.side_effect = ValueError("Potrero no encontrado")

        response = self.client.get('/api/potreros/999', headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_create_success(self, mock_service, mock_jwt, mock_usuario_service):
        """Test POST /api/potreros/ success."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin', 'tenant_id': 1}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        mock_service.create.return_value = {'id': 1, 'nombre': 'Nuevo Potrero'}

        response = self.client.post('/api/potreros/', json={'nombre': 'Nuevo Potrero'}, headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.routes.potrero_routes.PotreroController')
    def test_create_exception(self, mock_controller_class, mock_jwt, mock_usuario_service):
        """Test POST /api/potreros/ with exception."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        mock_controller_class.create.side_effect = Exception("Controller error")

        response = self.client.post('/api/potreros/', json={'nombre': 'Potrero'}, headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 500

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_update_success(self, mock_service, mock_jwt, mock_usuario_service):
        """Test PUT /api/potreros/<id> success."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin', 'tenant_id': 1}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        mock_service.update.return_value = {'id': 1, 'nombre': 'Potrero Actualizado'}

        response = self.client.put('/api/potreros/1', json={'nombre': 'Potrero Actualizado'}, headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.routes.potrero_routes.PotreroController')
    def test_update_exception(self, mock_controller_class, mock_jwt, mock_usuario_service):
        """Test PUT /api/potreros/<id> with exception."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        mock_controller_class.update.side_effect = Exception("Controller error")

        response = self.client.put('/api/potreros/1', json={'nombre': 'Potrero'}, headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 500

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_delete_success(self, mock_service, mock_jwt, mock_usuario_service):
        """Test DELETE /api/potreros/<id> success."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin', 'tenant_id': 1}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        mock_service.delete.return_value = True

        response = self.client.delete('/api/potreros/1', headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.routes.potrero_routes.PotreroController')
    def test_delete_exception(self, mock_controller_class, mock_jwt, mock_usuario_service):
        """Test DELETE /api/potreros/<id> with exception."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        mock_controller_class.delete.side_effect = Exception("Controller error")

        response = self.client.delete('/api/potreros/1', headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 500

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_get_by_estado_success(self, mock_service, mock_jwt, mock_usuario_service):
        """Test GET /api/potreros/estado/<estado> success."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin', 'tenant_id': 1}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        mock_service.get_by_estado.return_value = [{'id': 1, 'estado': 'disponible'}]

        response = self.client.get('/api/potreros/estado/disponible', headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.routes.potrero_routes.PotreroController')
    def test_get_by_estado_exception(self, mock_controller_class, mock_jwt, mock_usuario_service):
        """Test GET /api/potreros/estado/<estado> with exception."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        mock_controller_class.get_by_estado.side_effect = Exception("Controller error")

        response = self.client.get('/api/potreros/estado/disponible', headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 500

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_actualizar_ocupacion_success(self, mock_service, mock_jwt, mock_usuario_service):
        """Test PATCH /api/potreros/<id>/ocupacion success."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin', 'tenant_id': 1}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        mock_service.actualizar_ocupacion.return_value = {'id': 1, 'ocupacion': 50}

        response = self.client.patch('/api/potreros/1/ocupacion', json={'delta': 10}, headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_actualizar_ocupacion_exception(self, mock_service, mock_jwt, mock_usuario_service):
        """Test PATCH /api/potreros/<id>/ocupacion with exception."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin', 'tenant_id': 1}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        mock_service.actualizar_ocupacion.side_effect = Exception("Service error")

        response = self.client.patch('/api/potreros/1/ocupacion', json={'delta': 10}, headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 500
        data = response.get_json()
        assert data['success'] is False

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_get_tipos_pasto_success(self, mock_service, mock_jwt, mock_usuario_service):
        """Test GET /api/potreros/tipos-pasto success."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        mock_service.get_tipos_pasto.return_value = [{'id': 1, 'tipo_pasto': 'Bermuda'}]

        response = self.client.get('/api/potreros/tipos-pasto', headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 200

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_get_tipos_pasto_exception(self, mock_service, mock_jwt, mock_usuario_service):
        """Test GET /api/potreros/tipos-pasto with exception."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        mock_service.get_tipos_pasto.side_effect = Exception("Service error")

        response = self.client.get('/api/potreros/tipos-pasto', headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 500

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_get_personas_usuario_success(self, mock_service, mock_jwt, mock_usuario_service):
        """Test GET /api/potreros/personas-usuario success."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        mock_service.get_personas_usuario.return_value = [{'id': 1, 'nombre': 'Persona 1'}]

        response = self.client.get('/api/potreros/personas-usuario', headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 200

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_get_personas_usuario_exception(self, mock_service, mock_jwt, mock_usuario_service):
        """Test GET /api/potreros/personas-usuario with exception."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        mock_service.get_personas_usuario.side_effect = Exception("Service error")

        response = self.client.get('/api/potreros/personas-usuario', headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 500

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_get_estados_potrero_success(self, mock_service, mock_jwt, mock_usuario_service):
        """Test GET /api/potreros/estados success."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        mock_service.get_estados_potrero.return_value = [{'id': 1, 'estado': 'disponible'}]

        response = self.client.get('/api/potreros/estados', headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 200

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.potrero_controller.PotreroService')
    def test_get_estados_potrero_exception(self, mock_service, mock_jwt, mock_usuario_service):
        """Test GET /api/potreros/estados with exception."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        mock_service.get_estados_potrero.side_effect = Exception("Service error")

        response = self.client.get('/api/potreros/estados', headers={'Authorization': 'Bearer fake_token'})

        assert response.status_code == 500
