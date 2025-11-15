"""Tests para el servicio QR."""
import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import json
from datetime import datetime, timezone

from src.services.qr_service import QRService
from src.services.animal_service import GanadoService


class TestQRService:
    """Tests para QRService."""

    @patch.dict(os.environ, {'QR_FARM_WEB_URL': 'https://example.com'})
    def test_build_base_url_from_web_url(self):
        """Test _build_base_url con QR_FARM_WEB_URL."""
        result = QRService._build_base_url()
        assert result == 'https://example.com'

    @patch.dict(os.environ, {'QR_FARM_FRONTEND_URL': 'https://frontend.com'})
    def test_build_base_url_from_frontend_url(self):
        """Test _build_base_url con QR_FARM_FRONTEND_URL."""
        result = QRService._build_base_url()
        assert result == 'https://frontend.com'

    @patch.dict(os.environ, {}, clear=True)
    def test_build_base_url_default(self):
        """Test _build_base_url sin variables de entorno."""
        result = QRService._build_base_url()
        assert result == "https://github.com/NavajaOff/QR-FARM/tree/develop"

    @patch.dict(os.environ, {'QR_FARM_WEB_URL': 'https://example.com/'})
    def test_build_base_url_strips_trailing_slash(self):
        """Test _build_base_url elimina slash final."""
        result = QRService._build_base_url()
        assert result == 'https://example.com'

    def test_build_offline_payload_basic(self):
        """Test _build_offline_payload con datos básicos."""
        with patch.object(QRService, '_build_base_url', return_value='https://example.com'):
            payload = QRService._build_offline_payload(
                codigo_qr='QR_1_Test',
                id_ganado=1,
                nombre_ganado='Test Animal',
                nombre_propietario='John Doe',
                contacto='123456789'
            )

            assert payload['schema'] == 'qr-farm.v1'
            assert payload['type'] == 'ganado'
            assert payload['id'] == 1
            assert payload['codigo'] == 'QR_1_Test'
            assert payload['nombre'] == 'Test Animal'
            assert payload['propietario']['nombre'] == 'John Doe'
            assert payload['propietario']['contacto'] == '123456789'
            assert 'generado_en' in payload
            assert 'resumen' in payload

    def test_build_offline_payload_with_extra_data(self):
        """Test _build_offline_payload con datos extra."""
        with patch.object(QRService, '_build_base_url', return_value='https://example.com'):
            datos_extra = {
                'estado': 'activo',
                'estado_salud': 'saludable',
                'peso': 500.5,
                'sexo': 'macho',
                'fecha_nacimiento': '2020-01-01',
                'potrero': {'nombre': 'Potrero 1'}
            }
            payload = QRService._build_offline_payload(
                codigo_qr='QR_1_Test',
                id_ganado=1,
                nombre_ganado='Test Animal',
                nombre_propietario='John Doe',
                contacto='123456789',
                datos_extra=datos_extra
            )

            assert payload['estado'] == 'activo'
            assert payload['estado_salud'] == 'saludable'
            assert payload['peso'] == 500.5
            assert payload['sexo'] == 'macho'
            assert payload['fecha_nacimiento'] == '2020-01-01'
            assert payload['potrero'] == {'nombre': 'Potrero 1'}

    def test_build_offline_payload_with_url_in_extra(self):
        """Test _build_offline_payload con URL en datos extra."""
        with patch.object(QRService, '_build_base_url', return_value='https://example.com'):
            datos_extra = {'url': 'https://custom.com/animal/1'}
            payload = QRService._build_offline_payload(
                codigo_qr='QR_1_Test',
                id_ganado=1,
                nombre_ganado='Test Animal',
                nombre_propietario='John Doe',
                contacto='123456789',
                datos_extra=datos_extra
            )

            assert payload['url'] == 'https://custom.com/animal/1'

    @patch('src.services.qr_service.qrcode')
    @patch('src.services.qr_service.os.makedirs')
    @patch('src.services.qr_service.os.path.join')
    @patch('src.services.qr_service.os.getcwd')
    def test_generar_codigo_qr_success(self, mock_getcwd, mock_join, mock_makedirs, mock_qrcode):
        """Test generar_codigo_qr exitoso."""
        mock_getcwd.return_value = '/test'
        mock_join.side_effect = lambda *args: '/'.join(args)
        
        mock_qr_instance = MagicMock()
        mock_qrcode.QRCode.return_value = mock_qr_instance
        mock_img = MagicMock()
        mock_qr_instance.make_image.return_value = mock_img

        with patch.object(QRService, '_build_offline_payload', return_value={'test': 'data'}):
            result = QRService.generar_codigo_qr(
                id_ganado=1,
                nombre_ganado='Test Animal'
            )

            assert result == 'QR_1_Test_Animal'
            mock_qrcode.QRCode.assert_called_once()
            mock_qr_instance.add_data.assert_called_once()
            mock_qr_instance.make.assert_called_once_with(fit=True)
            mock_img.save.assert_called_once()

    @patch('src.services.qr_service.get_connection')
    @patch.object(GanadoService, 'obtener_ganado_detallado')
    def test_crear_qr_ganado_success(self, mock_obtener_detalle, mock_get_connection):
        """Test crear_qr_ganado exitoso."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {
            'nombre': 'Test Animal',
            'primer_nombre': 'John',
            'segundo_nombre': None,
            'primer_apellido': 'Doe',
            'segundo_apellido': None,
            'telefono': '123456789'
        }

        mock_obtener_detalle.return_value = {
            'estado': 'activo',
            'potrero': {'nombre': 'Potrero 1'}
        }

        with patch.object(QRService, 'generar_codigo_qr', return_value='QR_1_Test'):
            result = QRService.crear_qr_ganado(id_ganado=1)

            assert result is True
            mock_cursor.execute.assert_called()
            mock_conn.commit.assert_called_once()

    @patch('src.services.qr_service.get_connection')
    def test_crear_qr_ganado_not_found(self, mock_get_connection):
        """Test crear_qr_ganado cuando el ganado no existe."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = None

        result = QRService.crear_qr_ganado(id_ganado=999)

        assert result is False

    @patch('src.services.qr_service.get_connection')
    def test_crear_qr_ganado_exception(self, mock_get_connection):
        """Test crear_qr_ganado con excepción."""
        mock_get_connection.side_effect = Exception("Database error")

        result = QRService.crear_qr_ganado(id_ganado=1)

        assert result is False

    @patch('src.services.qr_service.get_connection')
    def test_obtener_qr_por_ganado_success(self, mock_get_connection):
        """Test obtener_qr_por_ganado exitoso."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        expected_result = {
            'id': 1,
            'id_ganado': 1,
            'codigo_qr': 'QR_1_Test',
            'nombre_ganado': 'Test Animal'
        }
        mock_cursor.fetchone.return_value = expected_result

        result = QRService.obtener_qr_por_ganado(id_ganado=1)

        assert result == expected_result
        mock_cursor.execute.assert_called_once()

    @patch('src.services.qr_service.get_connection')
    def test_obtener_qr_por_ganado_not_found(self, mock_get_connection):
        """Test obtener_qr_por_ganado cuando no existe."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = None

        result = QRService.obtener_qr_por_ganado(id_ganado=999)

        assert result is None

    @patch('src.services.qr_service.get_connection')
    def test_obtener_qr_por_ganado_exception(self, mock_get_connection):
        """Test obtener_qr_por_ganado con excepción."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Database error")

        result = QRService.obtener_qr_por_ganado(id_ganado=1)

        assert result is None

