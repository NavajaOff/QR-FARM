import pytest
from unittest.mock import Mock, patch
from src.services.potrero_service import PotreroService


class TestPotreroService:
    @patch('src.services.potrero_service.db')
    def test_get_tipos_pasto_success(self, mock_db):
        """Test get_tipos_pasto with successful database call"""
        mock_cursor = Mock()
        mock_db.get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            {'id': 1, 'tipo_pasto': 'Césped'},
            {'id': 2, 'tipo_pasto': 'Pasto alto'}
        ]

        result = PotreroService.get_tipos_pasto()

        assert len(result) == 2
        assert result[0]['tipo_pasto'] == 'Césped'

    @patch('src.services.potrero_service.db')
    def test_get_tipos_pasto_exception(self, mock_db):
        """Test get_tipos_pasto with database exception"""
        mock_cursor = Mock()
        mock_db.get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.side_effect = Exception("DB Error")

        result = PotreroService.get_tipos_pasto()

        assert result == []

    @patch('src.services.potrero_service.db')
    def test_get_estados_potrero_success(self, mock_db):
        """Test get_estados_potrero with successful database call"""
        mock_cursor = Mock()
        mock_db.get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {'COLUMN_TYPE': "enum('disponible','ocupado','limpieza')"}

        result = PotreroService.get_estados_potrero()

        assert len(result) == 3
        assert result[0]['estado'] == 'disponible'
        assert result[0]['id'] == 1

    @patch('src.services.potrero_service.db')
    def test_get_estados_potrero_no_result(self, mock_db):
        """Test get_estados_potrero when no result"""
        mock_cursor = Mock()
        mock_db.get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        result = PotreroService.get_estados_potrero()

        assert result == []

    @patch('src.services.potrero_service.db')
    def test_get_estados_potrero_exception(self, mock_db):
        """Test get_estados_potrero with database exception"""
        mock_cursor = Mock()
        mock_db.get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.side_effect = Exception("DB Error")

        result = PotreroService.get_estados_potrero()

        assert result == []

    @patch('src.services.potrero_service.get_current_tenant_id')
    def test_obtener_tenant_id(self, mock_get_tenant):
        """Test _obtener_tenant_id"""
        mock_get_tenant.return_value = 1
        result = PotreroService._obtener_tenant_id()
        assert result == 1

    @patch('src.services.potrero_service.get_current_tenant_id')
    def test_obtener_tenant_id_exception(self, mock_get_tenant):
        """Test _obtener_tenant_id with exception"""
        mock_get_tenant.side_effect = Exception
        result = PotreroService._obtener_tenant_id()
        assert result is None

    @patch('src.services.potrero_service.db')
    def test_obtener_ocupacion_real(self, mock_db):
        """Test _obtener_ocupacion_real"""
        mock_cursor = Mock()
        mock_db.get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {'total': 5}

        result = PotreroService._obtener_ocupacion_real(1)

        assert result == 5

    @patch('src.services.potrero_service.db')
    def test_obtener_ocupacion_real_exception(self, mock_db):
        """Test _obtener_ocupacion_real with exception"""
        mock_cursor = Mock()
        mock_db.get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.side_effect = Exception

        result = PotreroService._obtener_ocupacion_real(1)

        assert result == 0