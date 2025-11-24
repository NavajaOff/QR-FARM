import pytest
from unittest.mock import Mock, patch
from flask import Flask
from src.routes.animal_routes import animal_bp


class TestAnimalRoutes:
    def setup_method(self):
        """Setup test client and app context"""
        self.app = Flask(__name__)
        self.app.register_blueprint(animal_bp)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def teardown_method(self):
        """Clean up after each test"""
        self.app_context.pop()

    @patch('src.routes.animal_routes.GanadoService')
    def test_get_estados_ganado_sin_parametros(self, mock_service):
        """Test get_estados_ganado without query parameters"""
        mock_service.obtener_estados_ganado.return_value = [
            {'id': 1, 'estado': 'saludable', 'nombre_estado': 'saludable'},
            {'id': 2, 'estado': 'revision', 'nombre_estado': 'revision'}
        ]

        response = self.client.get('/api/animales/estados-ganado')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) == 2
        mock_service.obtener_estados_ganado.assert_called_once_with(solo_activos=False, solo_bajas=False)

    @patch('src.routes.animal_routes.GanadoService')
    def test_get_estados_ganado_solo_activos(self, mock_service):
        """Test get_estados_ganado with solo_activos=true"""
        mock_service.obtener_estados_ganado.return_value = [
            {'id': 1, 'estado': 'saludable', 'nombre_estado': 'saludable'},
            {'id': 2, 'estado': 'revision', 'nombre_estado': 'revision'},
            {'id': 3, 'estado': 'enfermo', 'nombre_estado': 'enfermo'}
        ]

        response = self.client.get('/api/animales/estados-ganado?solo_activos=true')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) == 3
        mock_service.obtener_estados_ganado.assert_called_once_with(solo_activos=True, solo_bajas=False)

    @patch('src.routes.animal_routes.GanadoService')
    def test_get_estados_ganado_solo_bajas(self, mock_service):
        """Test get_estados_ganado with solo_bajas=true"""
        mock_service.obtener_estados_ganado.return_value = [
            {'id': 4, 'estado': 'dado_de_baja', 'nombre_estado': 'dado_de_baja'},
            {'id': 5, 'estado': 'muerte', 'nombre_estado': 'muerte'}
        ]

        response = self.client.get('/api/animales/estados-ganado?solo_bajas=true')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) == 2
        mock_service.obtener_estados_ganado.assert_called_once_with(solo_activos=False, solo_bajas=True)

    @patch('src.routes.animal_routes.GanadoService')
    def test_get_estados_ganado_service_returns_empty(self, mock_service):
        """Test get_estados_ganado when service returns empty list"""
        mock_service.obtener_estados_ganado.return_value = []

        response = self.client.get('/api/animales/estados-ganado')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        # Should return default states when service returns empty
        assert len(data['data']) == 5  # ESTADOS_DEFAULT length

    @patch('src.routes.animal_routes.GanadoService')
    def test_get_estados_ganado_service_exception(self, mock_service):
        """Test get_estados_ganado when service raises exception"""
        mock_service.obtener_estados_ganado.side_effect = Exception("Database error")

        response = self.client.get('/api/animales/estados-ganado')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        # Should return default states on exception
        assert len(data['data']) == 5  # ESTADOS_DEFAULT length