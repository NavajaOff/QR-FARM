"""Tests para el servicio de vacunación."""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from src.services.vacunacion_service import VacunacionService
from src.models.vacunacion import Vacunacion, EstadoVacunacion


class TestVacunacionService:
    """Tests para VacunacionService."""

    @patch('src.services.vacunacion_service.get_connection')
    def test_obtener_todas_vacunaciones_success(self, mock_get_connection):
        """Test obtener_todas_vacunaciones exitoso."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True

        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'id_animal': 1,
                'nombre_animal': 'Animal 1',
                'fecha_aplicacion': datetime(2024, 1, 1),
                'proxima_dosis': datetime(2024, 7, 1),
                'responsable': 1,
                'nombre_responsable': 'John Doe',
                'estado': 'aplicado',
                'id_tipo_vacuna': 1,
                'nombre_tipo_vacuna': 'Vacuna A'
            }
        ]

        with patch.object(Vacunacion, 'from_dict') as mock_from_dict:
            mock_vacunacion = Mock()
            mock_from_dict.return_value = mock_vacunacion

            result = VacunacionService.obtener_todas_vacunaciones()

            assert len(result) == 1
            mock_from_dict.assert_called_once()
            mock_cursor.execute.assert_called_once()
            mock_conn.close.assert_called_once()

    @patch('src.services.vacunacion_service.get_connection')
    def test_obtener_todas_vacunaciones_exception(self, mock_get_connection):
        """Test obtener_todas_vacunaciones con excepción."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True
        mock_cursor.execute.side_effect = Exception("Database error")

        result = VacunacionService.obtener_todas_vacunaciones()

        assert result == []

    @patch('src.services.vacunacion_service.get_connection')
    def test_obtener_vacunacion_por_id_success(self, mock_get_connection):
        """Test obtener_vacunacion_por_id exitoso."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True

        mock_cursor.fetchone.return_value = {
            'id': 1,
            'id_animal': 1,
            'nombre_animal': 'Animal 1',
            'fecha_aplicacion': datetime(2024, 1, 1),
            'estado': 'completa'
        }

        with patch.object(Vacunacion, 'from_dict') as mock_from_dict:
            mock_vacunacion = Mock()
            mock_from_dict.return_value = mock_vacunacion

            result = VacunacionService.obtener_vacunacion_por_id(1)

            assert result == mock_vacunacion
            mock_from_dict.assert_called_once()

    @patch('src.services.vacunacion_service.get_connection')
    def test_obtener_vacunacion_por_id_not_found(self, mock_get_connection):
        """Test obtener_vacunacion_por_id cuando no existe."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True

        mock_cursor.fetchone.return_value = None

        result = VacunacionService.obtener_vacunacion_por_id(999)

        assert result is None

    @patch('src.services.vacunacion_service.get_connection')
    def test_crear_vacunacion_success(self, mock_get_connection):
        """Test crear_vacunacion exitoso."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True

        fecha_aplicacion = datetime(2024, 1, 1)
        vacunacion = Vacunacion(
            id_animal=1,
            fecha_aplicacion=fecha_aplicacion,
            responsable=1,
            estado=EstadoVacunacion.aplicado,
            id_tipo_vacuna=1
        )

        result = VacunacionService.crear_vacunacion(vacunacion)

        assert result is True
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    @patch('src.services.vacunacion_service.get_connection')
    def test_crear_vacunacion_with_string_date(self, mock_get_connection):
        """Test crear_vacunacion con fecha como string."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True

        vacunacion = Vacunacion(
            id_animal=1,
            fecha_aplicacion='2024-01-01T00:00:00Z',
            responsable=1,
            estado=EstadoVacunacion.aplicado,
            id_tipo_vacuna=1
        )

        result = VacunacionService.crear_vacunacion(vacunacion)

        assert result is True

    @patch('src.services.vacunacion_service.get_connection')
    def test_crear_vacunacion_exception(self, mock_get_connection):
        """Test crear_vacunacion con excepción."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True
        mock_cursor.execute.side_effect = Exception("Database error")

        vacunacion = Vacunacion(
            id_animal=1,
            fecha_aplicacion=datetime(2024, 1, 1),
            responsable=1,
            estado=EstadoVacunacion.aplicado,
            id_tipo_vacuna=1
        )

        result = VacunacionService.crear_vacunacion(vacunacion)

        assert result is False

    @patch('src.services.vacunacion_service.get_connection')
    def test_actualizar_vacunacion_success(self, mock_get_connection):
        """Test actualizar_vacunacion exitoso."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True
        mock_cursor.rowcount = 1

        vacunacion = Vacunacion(
            id_animal=1,
            fecha_aplicacion=datetime(2024, 1, 1),
            proxima_dosis=datetime(2024, 7, 1),
            responsable=1,
            estado=EstadoVacunacion.aplicado,
            id_tipo_vacuna=1
        )

        result = VacunacionService.actualizar_vacunacion(1, vacunacion)

        assert result is True
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    @patch('src.services.vacunacion_service.get_connection')
    def test_actualizar_vacunacion_not_found(self, mock_get_connection):
        """Test actualizar_vacunacion cuando no existe."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True
        mock_cursor.rowcount = 0

        vacunacion = Vacunacion(
            id_animal=1,
            fecha_aplicacion=datetime(2024, 1, 1),
            responsable=1,
            estado=EstadoVacunacion.aplicado,
            id_tipo_vacuna=1
        )

        result = VacunacionService.actualizar_vacunacion(999, vacunacion)

        assert result is False

    @patch('src.services.vacunacion_service.get_connection')
    def test_eliminar_vacunacion_success(self, mock_get_connection):
        """Test eliminar_vacunacion exitoso."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True
        mock_cursor.rowcount = 1

        result = VacunacionService.eliminar_vacunacion(1)

        assert result is True
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    @patch('src.services.vacunacion_service.get_connection')
    def test_eliminar_vacunacion_not_found(self, mock_get_connection):
        """Test eliminar_vacunacion cuando no existe."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True
        mock_cursor.rowcount = 0

        result = VacunacionService.eliminar_vacunacion(999)

        assert result is False

    @patch('src.services.vacunacion_service.get_connection')
    def test_obtener_tipos_vacuna_success(self, mock_get_connection):
        """Test obtener_tipos_vacuna exitoso."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True

        mock_cursor.fetchall.return_value = [
            {'id': 1, 'nombre': 'Vacuna A'},
            {'id': 2, 'nombre': 'Vacuna B'}
        ]

        result = VacunacionService.obtener_tipos_vacuna()

        assert len(result) == 2
        assert result[0]['nombre'] == 'Vacuna A'
        mock_cursor.execute.assert_called_once()

    @patch('src.services.vacunacion_service.get_connection')
    def test_obtener_tipos_vacuna_exception(self, mock_get_connection):
        """Test obtener_tipos_vacuna con excepción."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True
        mock_cursor.execute.side_effect = Exception("Database error")

        result = VacunacionService.obtener_tipos_vacuna()

        assert result == []

