"""Tests para la migración inicial 001_inicial.py."""
import pytest
from unittest.mock import Mock, patch
import importlib.util
from pathlib import Path

# Importar el módulo de migración usando importlib para que coverage lo detecte
MIGRATION_PATH = Path(__file__).parent.parent / 'src' / 'database' / 'migrations' / 'versions' / '001_inicial.py'
spec = importlib.util.spec_from_file_location("src.database.migrations.versions.001_inicial", MIGRATION_PATH)
migration_001 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migration_001)


class TestMigration001Inicial:
    """Tests para la migración inicial."""

    def test_constants_defined(self):
        """Test que las constantes están definidas."""
        assert hasattr(migration_001, 'FK_PERSONAS_ID')
        assert migration_001.FK_PERSONAS_ID == 'personas.id'
        assert hasattr(migration_001, 'revision')
        assert migration_001.revision == '001'
        assert migration_001.down_revision is None
        assert migration_001.branch_labels is None
        assert migration_001.depends_on is None

    def test_upgrade_creates_tables(self):
        """Test que upgrade() crea todas las tablas."""
        # Mockear op.create_table y op.bulk_insert directamente en el módulo
        mock_op = Mock()
        mock_op.create_table = Mock()
        mock_op.bulk_insert = Mock()
        
        # Reemplazar op en el módulo
        original_op = migration_001.op
        migration_001.op = mock_op
        
        try:
            # Ejecutar upgrade
            migration_001.upgrade()
        finally:
            # Restaurar op original
            migration_001.op = original_op
        
        # Verificar que se llamó create_table para todas las tablas esperadas
        create_table_calls = [call[0][0] for call in mock_op.create_table.call_args_list]
        expected_tables = [
            'roles', 'tipo_pasto', 'tipo_vacuna', 'personas',
            'estado_ganado', 'potrero', 'ganado',
            'qr', 'usuarios', 'vacunacion'
        ]
        
        for table_name in expected_tables:
            assert table_name in create_table_calls, f"Tabla {table_name} no fue creada"
        
        # Verificar que se llamó bulk_insert para los datos iniciales
        assert mock_op.bulk_insert.call_count >= 4  # roles, tipo_pasto, tipo_vacuna, estado_ganado

    def test_downgrade_drops_tables(self):
        """Test que downgrade() elimina todas las tablas."""
        # Mockear op.drop_table directamente en el módulo
        mock_op = Mock()
        mock_op.drop_table = Mock()
        
        # Reemplazar op en el módulo
        original_op = migration_001.op
        migration_001.op = mock_op
        
        try:
            # Ejecutar downgrade
            migration_001.downgrade()
        finally:
            # Restaurar op original
            migration_001.op = original_op
        
        # Verificar que se llamó drop_table para todas las tablas
        drop_table_calls = [call[0][0] for call in mock_op.drop_table.call_args_list]
        # Nota: revision está incluida porque la migración 001_inicial la crea originalmente
        # La migración 005_eliminar_revision_y_normalizar la eliminará en una migración posterior
        expected_tables = [
            'vacunacion', 'usuarios', 'qr', 'ganado',
            'potrero', 'revision', 'estado_ganado', 'personas',
            'tipo_vacuna', 'tipo_pasto', 'roles'
        ]
        
        assert len(drop_table_calls) == len(expected_tables)
        for table_name in expected_tables:
            assert table_name in drop_table_calls, f"Tabla {table_name} no fue eliminada"

    def test_upgrade_bulk_inserts_data(self):
        """Test que upgrade() inserta datos iniciales."""
        # Mockear op.create_table y op.bulk_insert directamente en el módulo
        mock_op = Mock()
        mock_op.create_table = Mock()
        mock_op.bulk_insert = Mock()
        
        # Reemplazar op en el módulo
        original_op = migration_001.op
        migration_001.op = mock_op
        
        try:
            # Ejecutar upgrade
            migration_001.upgrade()
        finally:
            # Restaurar op original
            migration_001.op = original_op
        
        # Verificar que bulk_insert fue llamado con los datos correctos
        bulk_insert_calls = mock_op.bulk_insert.call_args_list
        
        # Verificar que se insertaron roles
        roles_call = next((call for call in bulk_insert_calls if 'roles' in str(call)), None)
        assert roles_call is not None, "No se insertaron roles"
        
        # Verificar que se insertaron tipos de pasto
        pasto_call = next((call for call in bulk_insert_calls if 'tipo_pasto' in str(call)), None)
        assert pasto_call is not None, "No se insertaron tipos de pasto"
        
        # Verificar que se insertaron tipos de vacuna
        vacuna_call = next((call for call in bulk_insert_calls if 'tipo_vacuna' in str(call)), None)
        assert vacuna_call is not None, "No se insertaron tipos de vacuna"
        
        # Verificar que se insertaron estados de ganado
        estado_call = next((call for call in bulk_insert_calls if 'estado_ganado' in str(call)), None)
        assert estado_call is not None, "No se insertaron estados de ganado"

    def test_upgrade_function_exists(self):
        """Test que la función upgrade() existe y es llamable."""
        assert hasattr(migration_001, 'upgrade')
        assert callable(migration_001.upgrade)

    def test_downgrade_function_exists(self):
        """Test que la función downgrade() existe y es llamable."""
        assert hasattr(migration_001, 'downgrade')
        assert callable(migration_001.downgrade)

    def test_upgrade_uses_fk_constant(self):
        """Test que upgrade() usa la constante FK_PERSONAS_ID."""
        # Mockear op.create_table directamente en el módulo
        mock_op = Mock()
        mock_op.create_table = Mock()
        mock_op.bulk_insert = Mock()
        
        # Reemplazar op en el módulo
        original_op = migration_001.op
        migration_001.op = mock_op
        
        try:
            # Ejecutar upgrade
            migration_001.upgrade()
        finally:
            # Restaurar op original
            migration_001.op = original_op
        
        # Verificar que se usó FK_PERSONAS_ID en las foreign keys
        # Buscar en los argumentos de create_table si se usa la constante
        all_calls = str(mock_op.create_table.call_args_list)
        # La constante debería estar presente en las llamadas a create_table
        # para tablas que tienen foreign keys a personas
        assert 'personas.id' in all_calls or migration_001.FK_PERSONAS_ID in all_calls

