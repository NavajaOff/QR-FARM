"""Tests for routes module initialization."""

from __future__ import annotations

import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from datetime import datetime

from .helpers import prepare_environment


class TestCreateApp:
    """Test suite for create_app function."""

    @patch('src.routes.init_db')
    @patch('flask_cors.CORS')
    def test_create_app_with_default_config(self, mock_cors, mock_init_db, monkeypatch):
        """Test create_app with default configuration."""
        prepare_environment(monkeypatch)
        mock_init_db.return_value = Mock()
        mock_cors_instance = Mock()
        mock_cors.return_value = mock_cors_instance

        from src.routes import create_app
        app = create_app()

        assert isinstance(app, Flask)
        assert app.name == 'src.routes'
        mock_init_db.assert_called_once()
        mock_cors.assert_called_once()

    @patch('src.routes.init_db')
    @patch('flask_cors.CORS')
    def test_create_app_with_custom_config(self, mock_cors, mock_init_db, monkeypatch):
        """Test create_app with custom configuration class."""
        prepare_environment(monkeypatch)
        mock_init_db.return_value = Mock()
        mock_cors_instance = Mock()
        mock_cors.return_value = mock_cors_instance

        class TestConfig:
            """Test configuration class."""
            TESTING = True
            SECRET_KEY = 'test-secret-key'

        from src.routes import create_app
        app = create_app(config_class=TestConfig)

        assert isinstance(app, Flask)
        assert app.config['TESTING'] is True
        assert app.config['SECRET_KEY'] == 'test-secret-key'
        mock_init_db.assert_called_once()
        mock_cors.assert_called_once()

    @patch('src.routes.init_db')
    @patch('flask_cors.CORS')
    def test_create_app_cors_configuration(self, mock_cors, mock_init_db, monkeypatch):
        """Test CORS configuration in create_app."""
        prepare_environment(monkeypatch)
        mock_init_db.return_value = Mock()
        mock_cors_instance = Mock()
        mock_cors.return_value = mock_cors_instance

        from src.routes import create_app
        app = create_app()

        mock_cors.assert_called_once()
        call_args = mock_cors.call_args
        assert call_args[0][0] == app
        assert 'resources' in call_args[1]
        cors_resources = call_args[1]['resources']
        assert r'/api/*' in cors_resources
        assert cors_resources[r'/api/*']['origins'] == [
            'http://localhost:5173',
            'http://localhost:5174'
        ]
        assert set(cors_resources[r'/api/*']['methods']) == {
            'GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'
        }
        assert cors_resources[r'/api/*']['supports_credentials'] is True

    @patch('src.routes.init_db')
    @patch('flask_cors.CORS')
    def test_create_app_after_request_headers(self, mock_cors, mock_init_db, monkeypatch):
        """Test after_request decorator adds correct headers."""
        prepare_environment(monkeypatch)
        mock_init_db.return_value = Mock()
        mock_cors_instance = Mock()
        mock_cors.return_value = mock_cors_instance

        from src.routes import create_app
        app = create_app()
        client = app.test_client()

        response = client.get('/api/health')

        assert response.status_code == 200
        assert 'Access-Control-Allow-Origin' in response.headers
        origins = response.headers.get_all('Access-Control-Allow-Origin')
        assert 'http://localhost:5173' in origins
        assert 'http://localhost:5174' in origins
        assert 'Access-Control-Allow-Headers' in response.headers
        assert 'Access-Control-Allow-Methods' in response.headers

    @patch('src.routes.init_db')
    @patch('flask_cors.CORS')
    def test_create_app_registers_blueprints(self, mock_cors, mock_init_db, monkeypatch):
        """Test that all blueprints are registered correctly."""
        prepare_environment(monkeypatch)
        mock_init_db.return_value = Mock()
        mock_cors_instance = Mock()
        mock_cors.return_value = mock_cors_instance

        from src.routes import create_app
        app = create_app()

        registered_urls = [rule.rule for rule in app.url_map.iter_rules()]
        assert '/api/potreros' in str(registered_urls)
        assert '/api/usuarios' in str(registered_urls)
        assert '/api/animales' in str(registered_urls)

    @patch('src.routes.init_db')
    @patch('flask_cors.CORS')
    def test_favicon_route_returns_204(self, mock_cors, mock_init_db, monkeypatch):
        """Test favicon route returns 204 status."""
        prepare_environment(monkeypatch)
        mock_init_db.return_value = Mock()
        mock_cors_instance = Mock()
        mock_cors.return_value = mock_cors_instance

        from src.routes import create_app
        app = create_app()
        client = app.test_client()

        response = client.get('/favicon.ico')

        assert response.status_code == 204
        assert response.data == b''

    @patch('src.routes.init_db')
    @patch('flask_cors.CORS')
    @patch('builtins.print')
    def test_health_check_route(self, mock_print, mock_cors, mock_init_db, monkeypatch):
        """Test health check route returns correct response."""
        prepare_environment(monkeypatch)
        mock_init_db.return_value = Mock()
        mock_cors_instance = Mock()
        mock_cors.return_value = mock_cors_instance

        from src.routes import create_app
        app = create_app()
        client = app.test_client()

        response = client.get('/api/health')

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
        assert data['message'] == 'Backend QR Farm funcionando correctamente'
        assert 'timestamp' in data
        assert isinstance(data['timestamp'], str)
        mock_print.assert_called_once_with("INFO: Health check solicitado")

    @patch('src.routes.init_db')
    @patch('flask_cors.CORS')
    def test_health_check_timestamp_format(self, mock_cors, mock_init_db, monkeypatch):
        """Test health check timestamp is in ISO format."""
        prepare_environment(monkeypatch)
        mock_init_db.return_value = Mock()
        mock_cors_instance = Mock()
        mock_cors.return_value = mock_cors_instance

        from src.routes import create_app
        app = create_app()
        client = app.test_client()

        response = client.get('/api/health')
        data = response.get_json()

        try:
            datetime.fromisoformat(data['timestamp'])
        except ValueError:
            pytest.fail("Timestamp is not in valid ISO format")

    @patch('src.routes.init_db')
    @patch('flask_cors.CORS')
    def test_create_app_handles_init_db_exception(self, mock_cors, mock_init_db, monkeypatch):
        """Test create_app handles init_db exceptions gracefully."""
        prepare_environment(monkeypatch)
        mock_init_db.side_effect = Exception("Database initialization failed")
        mock_cors_instance = Mock()
        mock_cors.return_value = mock_cors_instance

        from src.routes import create_app
        with pytest.raises(Exception) as exc_info:
            create_app()

        assert "Database initialization failed" in str(exc_info.value)
        mock_init_db.assert_called_once()

    @patch('src.routes.init_db')
    @patch('flask_cors.CORS')
    def test_after_request_returns_response(self, mock_cors, mock_init_db, monkeypatch):
        """Test after_request function returns the response object."""
        prepare_environment(monkeypatch)
        mock_init_db.return_value = Mock()
        mock_cors_instance = Mock()
        mock_cors.return_value = mock_cors_instance

        from src.routes import create_app
        app = create_app()
        client = app.test_client()

        response = client.get('/api/health')

        assert response is not None
        assert hasattr(response, 'headers')
        assert hasattr(response, 'status_code')

