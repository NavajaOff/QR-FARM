import pytest
from unittest.mock import Mock, patch

from src.services.tenant_service import TenantService


class TestTenantService:
    @patch('src.services.tenant_service.get_connection')
    def test_obtener_todos_tenants_success(self, mock_get_conn):
        """Test obtener_todos_tenants with successful database call"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            {'id': 1, 'nombre': 'Tenant 1', 'activo': True},
            {'id': 2, 'nombre': 'Tenant 2', 'activo': False}
        ]

        result = TenantService.obtener_todos_tenants()

        assert len(result) == 2
        assert result[0]['id'] == 1
        assert result[0]['nombre'] == 'Tenant 1'
        mock_get_conn.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('src.services.tenant_service.get_connection')
    def test_obtener_todos_tenants_exception(self, mock_get_conn):
        """Test obtener_todos_tenants with database exception"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.side_effect = Exception("DB Error")

        result = TenantService.obtener_todos_tenants()

        assert result == []
        mock_conn.close.assert_called_once()

    @patch('src.services.tenant_service.get_connection')
    def test_obtener_tenant_por_id_success(self, mock_get_conn):
        """Test obtener_tenant_por_id with existing tenant"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = {'id': 1, 'nombre': 'Tenant 1', 'activo': True}

        result = TenantService.obtener_tenant_por_id(1)

        assert result is not None
        assert result['id'] == 1
        assert result['nombre'] == 'Tenant 1'
        mock_conn.close.assert_called_once()

    @patch('src.services.tenant_service.get_connection')
    def test_obtener_tenant_por_id_not_found(self, mock_get_conn):
        """Test obtener_tenant_por_id with non-existing tenant"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        result = TenantService.obtener_tenant_por_id(999)

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

        result = TenantService.crear_tenant('New Tenant')

        assert result == 123
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

        result = TenantService.crear_tenant('New Tenant')

        assert result is None
        mock_conn.close.assert_called_once()

    @patch('src.services.tenant_service.get_connection')
    def test_actualizar_tenant_success(self, mock_get_conn):
        """Test actualizar_tenant with successful update"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1

        result = TenantService.actualizar_tenant(1, 'Updated Tenant')

        assert result is True
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

        result = TenantService.actualizar_tenant(999, 'Updated Tenant')

        assert result is False
        mock_conn.close.assert_called_once()

    @patch('src.services.tenant_service.get_connection')
    def test_eliminar_tenant_success(self, mock_get_conn):
        """Test eliminar_tenant with successful deletion"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1

        result = TenantService.eliminar_tenant(1)

        assert result is True
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('src.services.tenant_service.get_connection')
    def test_eliminar_tenant_not_found(self, mock_get_conn):
        """Test eliminar_tenant with non-existing tenant"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 0

        result = TenantService.eliminar_tenant(999)

        assert result is False
        mock_conn.close.assert_called_once()

    @patch('src.services.tenant_service.get_connection')
    def test_tenant_tiene_usuarios_true(self, mock_get_conn):
        """Test tenant_tiene_usuarios when tenant has users"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {'count': 5}

        result = TenantService.tenant_tiene_usuarios(1)

        assert result is True
        mock_conn.close.assert_called_once()

    @patch('src.services.tenant_service.get_connection')
    def test_tenant_tiene_usuarios_false(self, mock_get_conn):
        """Test tenant_tiene_usuarios when tenant has no users"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {'count': 0}

        result = TenantService.tenant_tiene_usuarios(1)

        assert result is False
        mock_conn.close.assert_called_once()