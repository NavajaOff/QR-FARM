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


def test_obtener_resumen_success(monkeypatch):
    """Test obtener_resumen exitoso."""
    prepare_environment(monkeypatch)
    reporte_module = import_module("src.services.reporte_service")
    
    from unittest.mock import Mock, patch
    
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_cursor.fetchone.side_effect = [
        {"total": 5, "activos": 4, "inactivos": 1},
        {"total": 10},
        {"total": 3},
        {"total": 8},
        {"proximas": 2}
    ]
    mock_cursor.fetchall.side_effect = [
        [{"estado": "activo", "cantidad": 4}],
        [{"estado": "saludable", "cantidad": 8}],
        [{"estado": "disponible", "cantidad": 2}],
        [{"estado": "completa", "cantidad": 6}]
    ]
    
    with patch('src.services.reporte_service.get_connection', return_value=mock_conn), \
         patch('src.utils.tenant.get_current_tenant_id', return_value=1):
        mock_conn.cursor.return_value = mock_cursor
        
        result = reporte_module.ReporteService.obtener_resumen()
        
        assert result is not None
        assert 'usuarios' in result
        assert 'ganado' in result
        assert 'potreros' in result
        assert 'vacunaciones' in result


def test_obtener_resumen_exception(monkeypatch):
    """Test obtener_resumen con excepción."""
    prepare_environment(monkeypatch)
    reporte_module = import_module("src.services.reporte_service")
    
    from unittest.mock import patch
    
    with patch('src.services.reporte_service.get_connection', side_effect=Exception("DB Error")):
        result = reporte_module.ReporteService.obtener_resumen()
        
        assert result is not None
        assert 'error' in result


def test_obtener_usuarios_metricas(monkeypatch):
    """Test _obtener_usuarios_metricas."""
    prepare_environment(monkeypatch)
    reporte_module = import_module("src.services.reporte_service")
    
    from unittest.mock import Mock
    
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = {"total": 5, "activos": 4, "inactivos": 1}
    mock_cursor.fetchall.return_value = [{"estado": "activo", "cantidad": 4}]
    
    usuarios, breakdown = reporte_module.ReporteService._obtener_usuarios_metricas(mock_cursor, 1)
    
    assert usuarios is not None
    assert breakdown is not None


def test_obtener_ganado_metricas(monkeypatch):
    """Test _obtener_ganado_metricas."""
    prepare_environment(monkeypatch)
    reporte_module = import_module("src.services.reporte_service")
    
    from unittest.mock import Mock
    
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = {"total": 10}
    mock_cursor.fetchall.return_value = [{"estado": "saludable", "cantidad": 8}]
    
    ganado_total, breakdown = reporte_module.ReporteService._obtener_ganado_metricas(mock_cursor, 1)
    
    assert ganado_total is not None
    assert breakdown is not None


def test_obtener_potreros_metricas(monkeypatch):
    """Test _obtener_potreros_metricas."""
    prepare_environment(monkeypatch)
    reporte_module = import_module("src.services.reporte_service")
    
    from unittest.mock import Mock
    
    mock_cursor = Mock()
    mock_cursor.fetchone.return_value = {"total": 3}
    mock_cursor.fetchall.return_value = [{"estado": "disponible", "cantidad": 2}]
    
    potreros_total, breakdown = reporte_module.ReporteService._obtener_potreros_metricas(mock_cursor, 1)
    
    assert potreros_total is not None
    assert breakdown is not None


def test_obtener_vacunaciones_metricas(monkeypatch):
    """Test _obtener_vacunaciones_metricas."""
    prepare_environment(monkeypatch)
    reporte_module = import_module("src.services.reporte_service")
    
    from unittest.mock import Mock
    
    mock_cursor = Mock()
    mock_cursor.fetchone.side_effect = [
        {"total": 8},
        {"proximas": 2}
    ]
    mock_cursor.fetchall.return_value = [{"estado": "completa", "cantidad": 6}]
    
    vacunacion_total, breakdown, proximas = reporte_module.ReporteService._obtener_vacunaciones_metricas(mock_cursor, 1)
    
    assert vacunacion_total is not None
    assert breakdown is not None
    assert proximas is not None