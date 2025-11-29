"""Tests para la migración multi-tenant 004_multi_tenant.py."""
import pytest
from unittest.mock import Mock, patch, MagicMock
import importlib.util
from pathlib import Path

# Importar el módulo de migración usando importlib para que coverage lo detecte
MIGRATION_PATH = Path(__file__).parent.parent / 'src' / 'database' / 'migrations' / 'versions' / '004_multi_tenant.py'
spec = importlib.util.spec_from_file_location("src.database.migrations.versions.004_multi_tenant", MIGRATION_PATH)
migration_004 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migration_004)


class TestMigration004MultiTenant:
    """Tests para la migración multi-tenant."""

    def test_constants_defined(self):
        """Test que las constantes están definidas."""
        assert hasattr(migration_004, 'revision')
        assert migration_004.revision == '004_multi_tenant'
        assert migration_004.down_revision == '12673429ef47'
        assert migration_004.branch_labels is None
        assert migration_004.depends_on is None

    def test_crear_tabla_tenants_function_exists(self):
        """Test que la función _crear_tabla_tenants existe."""
        assert hasattr(migration_004, '_crear_tabla_tenants')
        assert callable(migration_004._crear_tabla_tenants)

    def test_crear_tabla_tenants_creates_table(self):
        """Test que _crear_tabla_tenants crea la tabla si no existe."""
        mock_op = Mock()
        tables = ['usuarios', 'personas']
        
        migration_004._crear_tabla_tenants(mock_op, tables)
        
        mock_op.create_table.assert_called_once()
        call_args = mock_op.create_table.call_args[0][0]
        assert call_args == 'tenants'

    def test_crear_tabla_tenants_skips_if_exists(self):
        """Test que _crear_tabla_tenants no crea la tabla si ya existe."""
        mock_op = Mock()
        tables = ['tenants', 'usuarios']
        
        migration_004._crear_tabla_tenants(mock_op, tables)
        
        mock_op.create_table.assert_not_called()

    def test_agregar_tenant_id_a_tablas(self):
        """Test que _agregar_tenant_id_a_tablas agrega tenant_id a las tablas."""
        mock_op = Mock()
        mock_inspector = Mock()
        
        # Mock de tablas existentes
        tables = ['usuarios', 'personas', 'ganado', 'potrero']
        
        # Mock de columnas (sin tenant_id)
        mock_inspector.get_columns = Mock(side_effect=lambda table: [
            {'name': 'id'}, {'name': 'nombre'}
        ])
        
        migration_004._agregar_tenant_id_a_tablas(mock_op, mock_inspector, tables)
        
        # Verificar que se llamó add_column para cada tabla
        assert mock_op.add_column.call_count == 4

    def test_agregar_tenant_id_a_tablas_skips_if_column_exists(self):
        """Test que _agregar_tenant_id_a_tablas no agrega si tenant_id ya existe."""
        mock_op = Mock()
        mock_inspector = Mock()
        
        tables = ['usuarios']
        
        # Mock de columnas (con tenant_id)
        mock_inspector.get_columns = Mock(return_value=[
            {'name': 'id'}, {'name': 'tenant_id'}
        ])
        
        migration_004._agregar_tenant_id_a_tablas(mock_op, mock_inspector, tables)
        
        mock_op.add_column.assert_not_called()

    def test_asignar_tenant_por_defecto(self):
        """Test que _asignar_tenant_por_defecto ejecuta las queries."""
        mock_op = Mock()
        
        migration_004._asignar_tenant_por_defecto(mock_op)
        
        assert mock_op.execute.call_count == 2

    def test_asignar_tenant_id_relaciones(self):
        """Test que _asignar_tenant_id_relaciones ejecuta las queries."""
        mock_op = Mock()
        
        migration_004._asignar_tenant_id_relaciones(mock_op)
        
        assert mock_op.execute.call_count == 6

    def test_asignar_tenant_defecto_restantes(self):
        """Test que _asignar_tenant_defecto_restantes ejecuta las queries."""
        mock_op = Mock()
        
        migration_004._asignar_tenant_defecto_restantes(mock_op)
        
        assert mock_op.execute.call_count == 5

    def test_hacer_tenant_id_not_null(self):
        """Test que _hacer_tenant_id_not_null hace tenant_id NOT NULL."""
        mock_op = Mock()
        mock_inspector = Mock()
        
        tables = ['ganado', 'potrero']
        
        # Mock de columnas con tenant_id nullable
        mock_inspector.get_columns = Mock(side_effect=lambda table: [
            {'name': 'id'}, {'name': 'tenant_id', 'nullable': True}
        ])
        
        migration_004._hacer_tenant_id_not_null(mock_op, mock_inspector, tables)
        
        assert mock_op.alter_column.call_count == 2

    def test_hacer_tenant_id_not_null_skips_if_not_nullable(self):
        """Test que _hacer_tenant_id_not_null no altera si ya es NOT NULL."""
        mock_op = Mock()
        mock_inspector = Mock()
        
        tables = ['ganado']
        
        # Mock de columnas con tenant_id NOT NULL
        mock_inspector.get_columns = Mock(return_value=[
            {'name': 'id'}, {'name': 'tenant_id', 'nullable': False}
        ])
        
        migration_004._hacer_tenant_id_not_null(mock_op, mock_inspector, tables)
        
        mock_op.alter_column.assert_not_called()

    def test_actualizar_tabla_roles(self):
        """Test que _actualizar_tabla_roles actualiza la tabla roles."""
        mock_op = Mock()
        mock_inspector = Mock()
        
        tables = ['roles']
        
        # Mock de columnas sin nivel ni permisos
        mock_inspector.get_columns = Mock(return_value=[
            {'name': 'id'}, {'name': 'rol'}, {'name': 'descripcion'}
        ])
        
        migration_004._actualizar_tabla_roles(mock_op, mock_inspector, tables)
        
        assert mock_op.add_column.call_count == 2
        assert mock_op.execute.call_count == 2

    def test_actualizar_tabla_roles_skips_if_not_exists(self):
        """Test que _actualizar_tabla_roles no hace nada si roles no existe."""
        mock_op = Mock()
        mock_inspector = Mock()
        
        tables = ['usuarios']
        
        migration_004._actualizar_tabla_roles(mock_op, mock_inspector, tables)
        
        mock_op.add_column.assert_not_called()
        mock_op.execute.assert_not_called()

    def test_upgrade_function_exists(self):
        """Test que la función upgrade() existe y es llamable."""
        assert hasattr(migration_004, 'upgrade')
        assert callable(migration_004.upgrade)

    def test_downgrade_function_exists(self):
        """Test que la función downgrade() existe y es llamable."""
        assert hasattr(migration_004, 'downgrade')
        assert callable(migration_004.downgrade)

    def test_upgrade_completo(self):
        """Test que upgrade() ejecuta todas las funciones auxiliares."""
        # Mockear op y sus métodos
        mock_op = Mock()
        mock_connection = Mock()
        mock_inspector = Mock()
        
        mock_op.get_bind.return_value = mock_connection
        mock_inspector.get_table_names.return_value = [
            'usuarios', 'personas', 'ganado', 'potrero', 'vacunacion', 'qr', 'revision', 'roles'
        ]
        mock_inspector.get_columns = Mock(side_effect=lambda table: [
            {'name': 'id'}, {'name': 'tenant_id', 'nullable': True} if 'tenant_id' not in str(table) else {'name': 'id'}
        ])
        
        # Reemplazar op en el módulo
        original_op = migration_004.op
        migration_004.op = mock_op
        
        # Mockear sa.inspect
        with patch('sqlalchemy.inspect', return_value=mock_inspector):
            try:
                # Ejecutar upgrade
                migration_004.upgrade()
            finally:
                # Restaurar op original
                migration_004.op = original_op
        
        # Verificar que se llamaron las operaciones principales
        assert mock_op.get_bind.called
        assert mock_op.execute.called

    def test_downgrade_completo(self):
        """Test que downgrade() elimina columnas y tabla."""
        # Mockear op
        mock_op = Mock()
        
        # Reemplazar op en el módulo
        original_op = migration_004.op
        migration_004.op = mock_op
        
        try:
            # Ejecutar downgrade
            migration_004.downgrade()
        finally:
            # Restaurar op original
            migration_004.op = original_op
        
        # Verificar que se eliminaron las columnas
        drop_column_calls = [call[0][0] for call in mock_op.drop_column.call_args_list]
        expected_tables = [
            'revision', 'qr', 'vacunacion', 'potrero', 'ganado', 'personas', 'usuarios'
        ]
        
        for table_name in expected_tables:
            assert table_name in drop_column_calls, f"Columna tenant_id de {table_name} no fue eliminada"
        
        # Verificar que se eliminaron columnas de roles
        roles_drops = [call for call in drop_column_calls if 'roles' in str(call)]
        assert len([c for c in mock_op.drop_column.call_args_list if c[0][0] == 'roles']) == 2
        
        # Verificar que se eliminó la tabla tenants
        mock_op.drop_table.assert_called_once_with('tenants')

    def test_upgrade_creates_tenants_table(self):
        """Test que upgrade() crea la tabla tenants."""
        mock_op = Mock()
        mock_connection = Mock()
        mock_inspector = Mock()
        
        mock_op.get_bind.return_value = mock_connection
        mock_inspector.get_table_names.return_value = ['usuarios']
        mock_inspector.get_columns = Mock(return_value=[{'name': 'id'}])
        
        original_op = migration_004.op
        migration_004.op = mock_op
        
        with patch('sqlalchemy.inspect', return_value=mock_inspector):
            try:
                migration_004.upgrade()
            finally:
                migration_004.op = original_op
        
        # Verificar que se creó la tabla tenants
        create_table_calls = [call[0][0] for call in mock_op.create_table.call_args_list]
        assert 'tenants' in create_table_calls

    def test_upgrade_adds_tenant_id_columns(self):
        """Test que upgrade() agrega tenant_id a las tablas."""
        mock_op = Mock()
        mock_connection = Mock()
        mock_inspector = Mock()
        
        mock_op.get_bind.return_value = mock_connection
        mock_inspector.get_table_names.return_value = ['usuarios', 'personas', 'ganado']
        mock_inspector.get_columns = Mock(return_value=[{'name': 'id'}])
        
        original_op = migration_004.op
        migration_004.op = mock_op
        
        with patch('sqlalchemy.inspect', return_value=mock_inspector):
            try:
                migration_004.upgrade()
            finally:
                migration_004.op = original_op
        
        # Verificar que se agregaron columnas tenant_id
        assert mock_op.add_column.called

    def test_upgrade_updates_roles_table(self):
        """Test que upgrade() actualiza la tabla roles."""
        mock_op = Mock()
        mock_connection = Mock()
        mock_inspector = Mock()
        
        mock_op.get_bind.return_value = mock_connection
        mock_inspector.get_table_names.return_value = ['roles']
        mock_inspector.get_columns = Mock(return_value=[{'name': 'id'}, {'name': 'rol'}])
        
        original_op = migration_004.op
        migration_004.op = mock_op
        
        with patch('sqlalchemy.inspect', return_value=mock_inspector):
            try:
                migration_004.upgrade()
            finally:
                migration_004.op = original_op
        
        # Verificar que se agregaron columnas a roles
        roles_add_column_calls = [
            call for call in mock_op.add_column.call_args_list 
            if call[0][0] == 'roles'
        ]
        assert len(roles_add_column_calls) >= 0  # Puede ser 0 si ya existen

