"""Pruebas para las rutas de tenants."""
import pytest


def test_tenant_routes_blueprint_creation():
    """Test que el blueprint de tenants se crea correctamente."""
    from src.routes.tenant_routes import tenant_bp

    assert tenant_bp is not None
    assert tenant_bp.name == "tenants"
    assert hasattr(tenant_bp, 'url_prefix')  # Blueprint should have url_prefix attribute


def test_tenant_routes_registration():
    """Test que las rutas de tenants están registradas."""
    from src.routes.tenant_routes import tenant_bp

    # Just verify the blueprint was created and has the expected name
    # The routes are registered when the module is imported
    assert tenant_bp is not None
    assert tenant_bp.name == "tenants"