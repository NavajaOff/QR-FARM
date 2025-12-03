import pytest
from unittest.mock import Mock, patch

from src.services.tenant_service import TenantService


class TestTenantService:
    @patch('src.services.tenant_service.get_connection')
    def test_listar_tenants_inactivos_only(self, mock_get_conn):
        """Test listar_tenants with activos_only=False returns only inactive tenants"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            {'id': 2, 'nombre': 'Tenant 2', 'codigo_tenant': 'code2', 'estado': 'inactivo'}
        ]

        result = TenantService.listar_tenants(activos_only=False)

        assert len(result) == 1
        assert result[0].id == 2
        assert result[0].nombre == 'Tenant 2'
        assert result[0].estado.value == 'inactivo'
        mock_cursor.execute.assert_called_once()
        # Verificar que la query incluye el filtro WHERE estado = 'inactivo'
        call_args = mock_cursor.execute.call_args[0][0]
        assert "WHERE estado = 'inactivo'" in call_args
        mock_get_conn.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('src.services.tenant_service.get_connection')
    def test_listar_tenants_activos_only(self, mock_get_conn):
        """Test listar_tenants with activos_only=True returns only active tenants"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            {'id': 1, 'nombre': 'Tenant 1', 'codigo_tenant': 'code1', 'estado': 'activo'}
        ]

        result = TenantService.listar_tenants(activos_only=True)

        assert len(result) == 1
        assert result[0].id == 1
        assert result[0].nombre == 'Tenant 1'
        assert result[0].estado.value == 'activo'
        mock_cursor.execute.assert_called_once()
        # Verificar que la query incluye el filtro WHERE estado = 'activo'
        call_args = mock_cursor.execute.call_args[0][0]
        assert "WHERE estado = 'activo'" in call_args
        mock_get_conn.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('src.services.tenant_service.get_connection')
    def test_listar_tenants_exception(self, mock_get_conn):
        """Test listar_tenants with database exception"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.side_effect = Exception("DB Error")

        result = TenantService.listar_tenants()

        assert result == []
        # Note: close is not called due to exception before reaching close() calls

    @patch('src.services.tenant_service.get_connection')
    def test_obtener_tenant_success(self, mock_get_conn):
        """Test obtener_tenant with existing tenant"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {'id': 1, 'nombre': 'Tenant 1', 'codigo_tenant': 'code1', 'estado': 'activo'}

        result = TenantService.obtener_tenant(1)

        assert result is not None
        assert result.id == 1
        assert result.nombre == 'Tenant 1'
        mock_conn.close.assert_called_once()

    @patch('src.services.tenant_service.get_connection')
    def test_obtener_tenant_not_found(self, mock_get_conn):
        """Test obtener_tenant with non-existing tenant"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        result = TenantService.obtener_tenant(999)

        assert result is None
        mock_conn.close.assert_called_once()

    @patch('src.services.tenant_service.get_connection')
    def test_crear_tenant_success(self, mock_get_conn):
        """Test crear_tenant with successful creation"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 123

        # Mock the obtener_tenant call
        with patch.object(TenantService, 'obtener_tenant', return_value=Mock(id=123, nombre='New Tenant')):
            result = TenantService.crear_tenant('New Tenant', 'code123')

        assert result is not None
        assert result.id == 123
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('src.services.tenant_service.get_connection')
    def test_crear_tenant_exception(self, mock_get_conn):
        """Test crear_tenant with database exception"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        result = TenantService.crear_tenant('New Tenant', 'code123')

        assert result is None
        # Note: close is not called due to exception before reaching close() calls

    @patch('src.services.tenant_service.get_connection')
    def test_actualizar_tenant_success(self, mock_get_conn):
        """Test actualizar_tenant with successful update"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1

        # Mock the obtener_tenant call
        with patch.object(TenantService, 'obtener_tenant', return_value=Mock(id=1, nombre='Updated Tenant')):
            result = TenantService.actualizar_tenant(1, nombre='Updated Tenant')

        assert result is not None
        assert result.nombre == 'Updated Tenant'
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('src.services.tenant_service.get_connection')
    def test_actualizar_tenant_not_found(self, mock_get_conn):
        """Test actualizar_tenant with non-existing tenant"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 0

        # Mock the obtener_tenant call
        with patch.object(TenantService, 'obtener_tenant', return_value=None):
            result = TenantService.actualizar_tenant(999, nombre='Updated Tenant')

        assert result is None
        mock_conn.close.assert_called_once()
