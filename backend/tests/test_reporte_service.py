"""Pruebas para ReporteService."""

from __future__ import annotations

from io import BytesIO
from unittest.mock import Mock

from .helpers import import_module, prepare_environment


def test_safe_close():
    """Test _safe_close method with various scenarios"""
    reporte_module = import_module("src.services.reporte_service")

    # Test with None conn and cursor
    reporte_module.ReporteService._safe_close(None, None)

    # Test with valid conn and cursor
    mock_conn = Mock()
    mock_cursor = Mock()
    reporte_module.ReporteService._safe_close(mock_conn, mock_cursor)
    mock_conn.close.assert_called_once()
    mock_cursor.close.assert_called_once()

    # Test with conn close raising exception
    mock_conn.reset_mock()
    mock_cursor.reset_mock()
    mock_conn.close.side_effect = Exception("Close error")
    reporte_module.ReporteService._safe_close(mock_conn, mock_cursor)
    # Should not raise exception

    # Test with cursor close raising exception
    mock_conn.close.side_effect = None
    mock_cursor.close.side_effect = Exception("Cursor close error")
    reporte_module.ReporteService._safe_close(mock_conn, mock_cursor)
    # Should not raise exception


def test_generar_pdf_crea_documento(monkeypatch):
    """El PDF generado debe contener datos binarios válidos."""
    prepare_environment(monkeypatch)
    reporte_module = import_module("src.services.reporte_service")

    resumen = {
        "generado_en": "2025-11-11T10:00:00Z",
        "usuarios": {"totales": {"total": 1, "activos": 1, "inactivos": 0}, "por_estado": []},
        "ganado": {"totales": {"total": 2}, "por_estado": []},
        "potreros": {"totales": {"total": 1}, "por_estado": []},
        "vacunaciones": {"totales": {"total": 3}, "por_estado": [], "proximas": 1},
    }

    pdf_stream = reporte_module.ReporteService.generar_pdf(resumen)

    assert isinstance(pdf_stream, BytesIO)
    contenido = pdf_stream.read(5)
    assert contenido.startswith(b"%PDF")

