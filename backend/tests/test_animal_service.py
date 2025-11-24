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

    @patch('src.services.animal_service.get_connection')
    def test_obtener_estados_ganado_solo_activos(self, mock_get_connection):
        """Test obtener_estados_ganado with solo_activos=True"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            {'id': 1, 'tipo_estado': 'saludable'},
            {'id': 2, 'tipo_estado': 'revision'},
            {'id': 3, 'tipo_estado': 'enfermo'}
        ]

        result = GanadoService.obtener_estados_ganado(solo_activos=True)

        assert len(result) == 3
        assert result[0]['estado'] == 'saludable'
        mock_cursor.execute.assert_called_once_with("SELECT id, tipo_estado FROM estado_ganado WHERE id BETWEEN 1 AND 3 ORDER BY tipo_estado")

    @patch('src.services.animal_service.get_connection')
    def test_obtener_estados_ganado_solo_bajas(self, mock_get_connection):
        """Test obtener_estados_ganado with solo_bajas=True"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            {'id': 4, 'tipo_estado': 'dado_de_baja'},
            {'id': 5, 'tipo_estado': 'muerte'},
            {'id': 6, 'tipo_estado': 'venta'}
        ]

        result = GanadoService.obtener_estados_ganado(solo_bajas=True)

        assert len(result) == 3
        assert result[0]['estado'] == 'dado_de_baja'
        mock_cursor.execute.assert_called_once_with("SELECT id, tipo_estado FROM estado_ganado WHERE id BETWEEN 4 AND 8 ORDER BY tipo_estado")

    @patch('src.services.animal_service.get_connection')
    def test_obtener_estados_ganado_ambos_parametros_true(self, mock_get_connection):
        """Test obtener_estados_ganado with both solo_activos and solo_bajas True (should prioritize solo_activos)"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            {'id': 1, 'tipo_estado': 'saludable'},
            {'id': 2, 'tipo_estado': 'revision'}
        ]

        result = GanadoService.obtener_estados_ganado(solo_activos=True, solo_bajas=True)

        # Should prioritize solo_activos when both are True
        mock_cursor.execute.assert_called_once_with("SELECT id, tipo_estado FROM estado_ganado WHERE id BETWEEN 1 AND 3 ORDER BY tipo_estado")


class TestGanadoModel:
    def test_ganado_init_with_id_estado(self):
        """Test Ganado model initialization with id_estado"""
        data = {
            'id': 1,
            'nombre': 'Test Animal',
            'id_estado': 2,
            'estado': 'revision'
        }
        ganado = Ganado(**data)

        assert ganado.id == 1
        assert ganado.nombre == 'Test Animal'
        assert ganado.id_estado == 2
        assert ganado.estado == 'revision'

    def test_ganado_from_dict_with_id_estado(self):
        """Test Ganado.from_dict with id_estado"""
        data = {
            'id': 1,
            'nombre': 'Test Animal',
            'id_estado': 3,
            'estado': 'enfermo',
            'sexo': 'macho'
        }
        ganado = Ganado.from_dict(data)

        assert ganado.id == 1
        assert ganado.nombre == 'Test Animal'
        assert ganado.id_estado == 3
        assert ganado.estado == 'enfermo'
        assert ganado.sexo == SexoGanado.MACHO

    def test_ganado_to_dict_includes_id_estado(self):
        """Test Ganado.to_dict includes id_estado"""
        ganado = Ganado(id=1, nombre='Test', id_estado=2, estado='revision')
        result = ganado.to_dict()

        assert result['id'] == 1
        assert result['nombre'] == 'Test'
        assert result['id_estado'] == 2
        assert result['estado'] == 'revision'

    def test_ganado_es_estado_baja_true(self):
        """Test es_estado_baja returns True for id_estado >= 4"""
        assert Ganado.es_estado_baja(4) is True
        assert Ganado.es_estado_baja(5) is True
        assert Ganado.es_estado_baja(8) is True

    def test_ganado_es_estado_baja_false(self):
        """Test es_estado_baja returns False for id_estado < 4"""
        assert Ganado.es_estado_baja(1) is False
        assert Ganado.es_estado_baja(2) is False
        assert Ganado.es_estado_baja(3) is False
        assert Ganado.es_estado_baja(None) is False

    def test_ganado_es_estado_activo_true(self):
        """Test es_estado_activo returns True for id_estado 1-3"""
        assert Ganado.es_estado_activo(1) is True
        assert Ganado.es_estado_activo(2) is True
        assert Ganado.es_estado_activo(3) is True

    def test_ganado_es_estado_activo_false(self):
        """Test es_estado_activo returns False for id_estado >= 4"""
        assert Ganado.es_estado_activo(4) is False
        assert Ganado.es_estado_activo(5) is False
        assert Ganado.es_estado_activo(None) is True  # Default to active