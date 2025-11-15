import pytest
from unittest.mock import Mock, patch
from src.services.animal_service import GanadoService
from src.models.animal import Ganado, EstadoGanado, SexoGanado


class TestGanadoService:
    def test_mapear_estado_a_id_saludable(self):
        """Test mapping EstadoGanado.SALUDABLE to ID"""
        result = GanadoService._mapear_estado_a_id(EstadoGanado.SALUDABLE)
        assert result == 1

    def test_mapear_estado_a_id_revision(self):
        """Test mapping EstadoGanado.REVISION to ID"""
        result = GanadoService._mapear_estado_a_id(EstadoGanado.REVISION)
        assert result == 2

    def test_mapear_estado_a_id_enfermo(self):
        """Test mapping EstadoGanado.ENFERMO to ID"""
        result = GanadoService._mapear_estado_a_id(EstadoGanado.ENFERMO)
        assert result == 3

    def test_mapear_estado_a_id_default(self):
        """Test mapping unknown estado returns default"""
        # Create a mock estado not in mapping
        mock_estado = Mock()
        result = GanadoService._mapear_estado_a_id(mock_estado)
        assert result == 1

    def test_convertir_fecha_nacimiento_datetime(self):
        """Test converting datetime to isoformat"""
        from datetime import datetime
        dt = datetime(2023, 1, 1, 10, 0, 0)
        result = GanadoService._convertir_fecha_nacimiento(dt)
        assert result == '2023-01-01T10:00:00'

    def test_convertir_fecha_nacimiento_string(self):
        """Test converting string fecha"""
        fecha_str = '2023-01-01'
        result = GanadoService._convertir_fecha_nacimiento(fecha_str)
        assert result == '2023-01-01'

    def test_convertir_fecha_nacimiento_none(self):
        """Test converting None fecha"""
        result = GanadoService._convertir_fecha_nacimiento(None)
        assert result is None

    @patch('src.services.animal_service.get_connection')
    def test_obtener_estados_ganado_success(self, mock_get_connection):
        """Test obtener_estados_ganado with successful database call"""
        # Mock the connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock the fetchall result
        mock_cursor.fetchall.return_value = [
            {'id': 1, 'tipo_estado': 'activo'},
            {'id': 2, 'tipo_estado': 'saludable'}
        ]

        result = GanadoService.obtener_estados_ganado()

        # Verify the result
        assert len(result) == 2
        assert result[0]['id'] == 1
        assert result[0]['estado'] == 'activo'
        assert result[0]['nombre_estado'] == 'activo'

        # Verify database calls
        mock_get_connection.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with("SELECT id, tipo_estado FROM estado_ganado ORDER BY tipo_estado")
        mock_conn.close.assert_called_once()

    @patch('src.services.animal_service.get_connection')
    def test_obtener_estados_ganado_connection_none(self, mock_get_connection):
        """Test obtener_estados_ganado when connection is None"""
        mock_get_connection.return_value = None

        result = GanadoService.obtener_estados_ganado()

        assert result == []

    @patch('src.services.animal_service.get_connection')
    def test_obtener_estados_ganado_exception(self, mock_get_connection):
        """Test obtener_estados_ganado with database exception"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.side_effect = Exception("Database error")

        result = GanadoService.obtener_estados_ganado()

        assert result == []
        mock_conn.close.assert_called_once()