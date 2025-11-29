"""Tests para ReporteController."""
import pytest
from unittest.mock import Mock, patch
from flask import Flask, g
from src.controllers.reporte_controller import ReporteController


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


class TestReporteController:
    """Tests para ReporteController."""

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.reporte_controller.ReporteService')
    def test_obtener_resumen_success(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test obtener_resumen exitoso."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            g.tenant_id = 1
            
            mock_service.obtener_resumen.return_value = {
                'usuarios': {'total': 5},
                'ganado': {'total': 10}
            }

            result = ReporteController.obtener_resumen()

            assert result[1] == 200
            mock_service.obtener_resumen.assert_called_once()

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.reporte_controller.ReporteService')
    def test_obtener_resumen_exception(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test obtener_resumen con excepción."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            g.tenant_id = 1
            
            mock_service.obtener_resumen.side_effect = Exception("Error")

            result = ReporteController.obtener_resumen()

            assert result[1] == 500

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.reporte_controller.ReporteService')
    @patch('src.controllers.reporte_controller.send_file')
    def test_descargar_resumen_pdf_success(self, mock_send_file, mock_service, mock_jwt, mock_usuario_service, app):
        """Test descargar_resumen_pdf exitoso."""
        from io import BytesIO
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            g.tenant_id = 1
            
            mock_pdf = BytesIO(b'%PDF-1.4')
            mock_service.obtener_resumen.return_value = {'usuarios': {'total': 5}}
            mock_service.generar_pdf.return_value = mock_pdf
            mock_send_file.return_value = (mock_pdf, 200)

            result = ReporteController.descargar_resumen_pdf()

            assert result[1] == 200
            mock_service.obtener_resumen.assert_called_once()
            mock_service.generar_pdf.assert_called_once()

    @patch('src.utils.auth.UsuarioService')
    @patch('src.utils.auth.jwt')
    @patch('src.controllers.reporte_controller.ReporteService')
    def test_descargar_resumen_pdf_exception(self, mock_service, mock_jwt, mock_usuario_service, app):
        """Test descargar_resumen_pdf con excepción."""
        mock_jwt.decode.return_value = {'user_id': 1, 'role': 'admin'}
        mock_user = _create_mock_user()
        mock_usuario_service.obtener_usuario.return_value = mock_user
        
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_request_context(
            headers={'Authorization': 'Bearer fake_token'}
        ):
            g.current_user = mock_user
            g.tenant_id = 1
            
            mock_service.obtener_resumen.side_effect = Exception("Error")

            result = ReporteController.descargar_resumen_pdf()

            assert result[1] == 500

