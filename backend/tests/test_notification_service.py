import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from src.services.notification_service import NotificationService


class TestNotificationService:
    @patch("src.services.notification_service.get_connection")
    def test_obtener_potreros_con_limpieza_proxima_success(self, mock_get_connection):
        """Should return formatted cleaning notifications."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True
        mock_get_connection.return_value = mock_conn

        fecha = datetime(2025, 12, 15, 10, 0, 0)
        mock_cursor.fetchall.return_value = [{
            "potrero_id": 42,
            "potrero_nombre": "Potrero Norte",
            "fecha_proxima_limpieza": fecha,
            "responsable_nombre": "Laura Gómez"
        }]

        result = NotificationService._obtener_potreros_con_limpieza_proxima(None)

        assert len(result) == 1
        assert result[0]["tipo"] == "limpieza"
        assert result[0]["titulo"].startswith("Limpieza próxima")
        assert result[0]["responsable"] == "Laura Gómez"
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchall.assert_called_once()

    @patch("src.services.notification_service.get_connection")
    def test_obtener_vacunaciones_con_dosis_proxima_success(self, mock_get_connection):
        """Should return formatted vaccination notifications."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True
        mock_get_connection.return_value = mock_conn

        fecha = datetime(2025, 12, 20, 12, 0, 0)
        mock_cursor.fetchall.return_value = [{
            "vacunacion_id": 5,
            "animal_id": 10,
            "nombre_animal": "Rosa",
            "proxima_dosis": fecha,
            "responsable_nombre": "Andrés López",
            "nombre_tipo_vacuna": "Brucelosis"
        }]

        result = NotificationService._obtener_vacunaciones_con_dosis_proxima(None)

        assert len(result) == 1
        assert result[0]["tipo"] == "vacunacion"
        assert "Rosa" in result[0]["titulo"]
        assert result[0]["responsable"] == "Andrés López"
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchall.assert_called_once()

    def test_obtener_notificaciones_proximas_ordenadas(self):
        """Should combine and sort the notification lists."""
        limpieza = [
            {"fecha": "2025-12-10T01:00:00", "tipo": "limpieza"},
            {"fecha": "2025-12-12T01:00:00", "tipo": "limpieza"}
        ]
        vacunacion = [
            {"fecha": "2025-12-08T01:00:00", "tipo": "vacunacion"}
        ]

        with patch.object(
            NotificationService,
            "_obtener_potreros_con_limpieza_proxima",
            return_value=limpieza
        ), patch.object(
            NotificationService,
            "_obtener_vacunaciones_con_dosis_proxima",
            return_value=vacunacion
        ):
            resultado = NotificationService.obtener_notificaciones_proximas(None)

        assert len(resultado) == 3
        assert resultado[0]["tipo"] == "vacunacion"
        assert resultado[2]["fecha"] == "2025-12-12T01:00:00"

