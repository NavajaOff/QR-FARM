import pytest
from unittest.mock import Mock, patch, mock_open
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from update_qr import (
    slugify_animal_name,
    ensure_directory_exists,
    _build_datos_extra,
    _generate_qr_filename_from_code,
    get_animal_data,
    persist_qr_code,
    update_qr_for_animal
)


class TestUpdateQR:
    def test_slugify_animal_name_basic(self):
        """Test slugify_animal_name with basic input"""
        result = slugify_animal_name("Test Animal")
        assert result == "test_animal"

    def test_slugify_animal_name_special_chars(self):
        """Test slugify_animal_name with special characters"""
        result = slugify_animal_name("Test@Animal#123")
        assert result == "test_animal_123"

    def test_slugify_animal_name_empty(self):
        """Test slugify_animal_name with empty string"""
        result = slugify_animal_name("")
        assert result == "animal"

    def test_slugify_animal_name_only_special(self):
        """Test slugify_animal_name with only special characters"""
        result = slugify_animal_name("!@#$%")
        assert result == "animal"

    @patch('update_qr.Path.mkdir')
    def test_ensure_directory_exists(self, mock_mkdir):
        """Test ensure_directory_exists"""
        mock_path = Mock()
        ensure_directory_exists(mock_path)
        mock_path.mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_build_datos_extra_complete(self):
        """Test _build_datos_extra with complete data"""
        data = {
            'estado': 'saludable',
            'estado_salud': 'bueno',
            'potrero_nombre': 'Campo 1',
            'peso': 450.5,
            'sexo': 'hembra',
            'fecha_nacimiento': '2020-01-01'
        }
        result = _build_datos_extra(data)
        expected = {
            'estado': 'saludable',
            'estado_salud': 'bueno',
            'potrero': {'nombre': 'Campo 1'},
            'peso': 450.5,
            'sexo': 'hembra',
            'fecha_nacimiento': '2020-01-01'
        }
        assert result == expected

    def test_build_datos_extra_minimal(self):
        """Test _build_datos_extra with minimal data"""
        data = {}
        result = _build_datos_extra(data)
        expected = {
            'estado': None,
            'estado_salud': None,
            'potrero': None,
            'peso': None,
            'sexo': None,
            'fecha_nacimiento': None
        }
        assert result == expected

    @patch('update_qr.QR_DIR', Path('/tmp/qr'))
    def test_generate_qr_filename_from_code(self):
        """Test _generate_qr_filename_from_code"""
        with patch('update_qr.ensure_directory_exists'):
            result = _generate_qr_filename_from_code('test123')
            assert str(result).endswith('test123.png')

    @patch('update_qr.GanadoService.obtener_ganado_detallado')
    def test_get_animal_data_success(self, mock_obtener):
        """Test get_animal_data with success"""
        mock_obtener.return_value = {'id': 1, 'nombre': 'Test'}
        result = get_animal_data(1)
        assert result == {'id': 1, 'nombre': 'Test'}
        mock_obtener.assert_called_once_with(1)

    @patch('update_qr.GanadoService.obtener_ganado_detallado')
    def test_get_animal_data_exception(self, mock_obtener):
        """Test get_animal_data with exception"""
        mock_obtener.side_effect = Exception("DB Error")
        result = get_animal_data(1)
        assert result is None

    @patch('update_qr.get_connection')
    def test_persist_qr_code_success(self, mock_get_conn):
        """Test persist_qr_code with success"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 0  # First update fails, insert succeeds
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)

        persist_qr_code(1, 'test123')

        assert mock_cursor.execute.call_count == 3  # UPDATE qr, INSERT qr, UPDATE ganado
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('update_qr.get_connection')
    def test_persist_qr_code_exception(self, mock_get_conn):
        """Test persist_qr_code with exception"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        with pytest.raises(Exception):
            persist_qr_code(1, 'test123')

        mock_conn.rollback.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('update_qr.get_animal_data')
    @patch('update_qr.QRService.obtener_qr_por_ganado')
    @patch('update_qr.move_old_qr')
    @patch('update_qr.generate_new_qr')
    @patch('update_qr.persist_qr_code')
    def test_update_qr_for_animal_success(self, mock_persist, mock_generate, mock_move, mock_obtener_qr, mock_get_data):
        """Test update_qr_for_animal with success"""
        mock_get_data.return_value = {
            'id': 1,
            'nombre': 'Test Animal',
            'codigo_qr': 'old123'
        }
        mock_obtener_qr.return_value = {'codigo_qr': 'old123'}
        mock_generate.return_value = Path('/tmp/qr/new123.png')
        mock_persist.return_value = None
        mock_move.return_value = None

        result = update_qr_for_animal(1)

        assert result is True
        mock_get_data.assert_called_once_with(1)
        mock_obtener_qr.assert_called_once_with(1)
        mock_move.assert_called_once()
        mock_generate.assert_called_once()
        mock_persist.assert_called_once_with(1, 'new123')

    @patch('update_qr.get_animal_data')
    def test_update_qr_for_animal_no_data(self, mock_get_data):
        """Test update_qr_for_animal when no animal data"""
        mock_get_data.return_value = None

        result = update_qr_for_animal(1)

        assert result is False

    @patch('update_qr.get_animal_data')
    @patch('update_qr.QRService.obtener_qr_por_ganado')
    @patch('update_qr.move_old_qr')
    def test_update_qr_for_animal_move_fails(self, mock_move, mock_obtener_qr, mock_get_data):
        """Test update_qr_for_animal when moving old QR fails"""
        mock_get_data.return_value = {
            'id': 1,
            'nombre': 'Test Animal',
            'codigo_qr': 'old123'
        }
        mock_obtener_qr.return_value = {'codigo_qr': 'old123'}
        mock_move.side_effect = OSError("Move failed")

        result = update_qr_for_animal(1)

        assert result is False