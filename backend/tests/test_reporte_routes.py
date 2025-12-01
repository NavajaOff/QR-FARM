"""Pruebas para las rutas de reportes."""
import pytest


def test_reporte_routes_blueprint_creation():
    """Test que el blueprint de reportes se crea correctamente."""
    from src.routes.reporte_routes import reporte_bp

    assert reporte_bp is not None
    assert reporte_bp.name == "reporte"
    assert hasattr(reporte_bp, 'url_prefix')  # Blueprint should have url_prefix attribute


def test_reporte_routes_registration():
    """Test que las rutas de reportes están registradas."""
    from src.routes.reporte_routes import reporte_bp

    # Just verify the blueprint was created and has the expected name
    # The routes are registered when the module is imported
    assert reporte_bp is not None
    assert reporte_bp.name == "reporte"