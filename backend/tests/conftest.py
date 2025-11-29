import pytest
from flask import Flask
from unittest.mock import Mock, patch

@pytest.fixture
def app():
    """Create and configure a test app instance."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['TESTING'] = True
    return app

@pytest.fixture
def app_context(app):
    """Provide Flask application context for tests."""
    with app.app_context():
        yield

@pytest.fixture
def mock_jsonify():
    """Mock jsonify to return a proper response object."""
    def _jsonify(data):
        mock_response = Mock()
        mock_response.get_json.return_value = data
        return mock_response

    with patch('src.controllers.usuario_controller.jsonify', side_effect=_jsonify):
        yield

@pytest.fixture
def mock_current_app(app):
    """Mock current_app to return our test app."""
    with patch('src.controllers.usuario_controller.current_app', app):
        yield

@pytest.fixture
def mock_request():
    """Mock Flask request object."""
    mock_req = Mock()
    mock_req.get_json.return_value = {}
    mock_req.headers = {}
    mock_req.args = {}
    with patch('src.controllers.usuario_controller.request', mock_req):
        yield mock_req

@pytest.fixture
def mock_g():
    """Mock Flask g object."""
    mock_g_obj = Mock()
    with patch('src.controllers.usuario_controller.g', mock_g_obj):
        yield mock_g_obj