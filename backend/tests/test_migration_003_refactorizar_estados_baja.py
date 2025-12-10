"""Tests para la migración 003_refactorizar_estados_baja.py."""
import pytest
from unittest.mock import Mock, patch
import importlib.util
from pathlib import Path

# Importar el módulo de migración usando importlib para que coverage lo detecte
MIGRATION_PATH = Path(__file__).parent.parent / 'src' / 'database' / 'migrations' / 'versions' / '003_refactorizar_estados_baja.py'
spec = importlib.util.spec_from_file_location("src.database.migrations.versions.003_refactorizar_estados_baja", MIGRATION_PATH)
migration_003 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migration_003)


class TestMigration003RefactorizarEstadosBaja:
    """Tests para la migración de refactorizar estados de baja."""

    def test_constants_defined(self):
        """Test que las constantes están definidas."""
        assert hasattr(migration_003, 'revision')
        assert migration_003.revision == '003_refactorizar_estados_baja'
        assert migration_003.down_revision == '002_baja_ganado'
        assert migration_003.branch_labels is None
        assert migration_003.depends_on is None

    def test_upgrade_inserts_states_and_updates_and_drops_columns(self):
        """Test que upgrade() inserta estados, actualiza ganado y elimina columnas."""
        # Mockear op.bulk_insert, op.execute y op.drop_column
        mock_op = Mock()
        mock_op.bulk_insert = Mock()
        mock_op.execute = Mock()
        mock_op.drop_column = Mock()

        # Reemplazar op en el módulo
        original_op = migration_003.op
        migration_003.op = mock_op

        try:
            # Ejecutar upgrade
            migration_003.upgrade()
        finally:
            # Restaurar op original
            migration_003.op = original_op

        # Verificar que se llamó bulk_insert para estado_ganado
        assert mock_op.bulk_insert.call_count == 1
        bulk_insert_call = mock_op.bulk_insert.call_args
        table_name = bulk_insert_call[0][0].name  # sa.table name
        assert table_name == 'estado_ganado'

        # Verificar los datos insertados
        inserted_data = bulk_insert_call[0][1]
        expected_data = [
            {'id': 5, 'tipo_estado': 'muerte'},
            {'id': 6, 'tipo_estado': 'venta'},
            {'id': 7, 'tipo_estado': 'robo'},
            {'id': 8, 'tipo_estado': 'otra'}
        ]
        assert inserted_data == expected_data

        # Verificar que se llamó execute para actualizar ganado
        execute_calls = mock_op.execute.call_args_list
        assert len(execute_calls) == 1
        update_sql = execute_calls[0][0][0]
        assert "UPDATE ganado" in update_sql
        assert "SET id_estado = CASE" in update_sql.replace('\n', ' ')
        assert "WHERE estado_baja = 'dado_de_baja'" in update_sql

        # Verificar que se llamó drop_column para las columnas de baja
        drop_column_calls = mock_op.drop_column.call_args_list
        assert len(drop_column_calls) == 4
        dropped_columns = [call[0][1] for call in drop_column_calls]
        expected_drops = ['observaciones_baja', 'fecha_baja', 'causa_baja', 'estado_baja']
        assert dropped_columns == expected_drops

    def test_downgrade_adds_columns_and_updates_and_deletes_states(self):
        """Test que downgrade() agrega columnas, actualiza ganado y elimina estados."""
        # Mockear op.add_column, op.execute
        mock_op = Mock()
        mock_op.add_column = Mock()
        mock_op.execute = Mock()

        # Reemplazar op en el módulo
        original_op = migration_003.op
        migration_003.op = mock_op

        try:
            # Ejecutar downgrade
            migration_003.downgrade()
        finally:
            # Restaurar op original
            migration_003.op = original_op

        # Verificar que se llamó add_column para las columnas de baja
        add_column_calls = mock_op.add_column.call_args_list
        assert len(add_column_calls) == 4
        column_names = [call[0][1].name for call in add_column_calls]
        expected_columns = ['estado_baja', 'causa_baja', 'fecha_baja', 'observaciones_baja']
        for col in expected_columns:
            assert col in column_names

        # Verificar que se llamó execute dos veces: uno para UPDATE, otro para DELETE
        execute_calls = mock_op.execute.call_args_list
        assert len(execute_calls) == 2

        # Primer execute: UPDATE ganado
        update_sql = execute_calls[0][0][0]
        assert "UPDATE ganado" in update_sql
        assert "SET estado_baja = 'dado_de_baja'" in update_sql.replace('\n', ' ')
        assert "WHERE id_estado IN (5, 6, 7, 8)" in update_sql

        # Segundo execute: DELETE from estado_ganado
        delete_sql = execute_calls[1][0][0]
        assert "DELETE FROM estado_ganado WHERE id IN (5, 6, 7, 8)" in delete_sql

    def test_upgrade_function_exists(self):
        """Test que la función upgrade() existe y es llamable."""
        assert hasattr(migration_003, 'upgrade')
        assert callable(migration_003.upgrade)

    def test_downgrade_function_exists(self):
        """Test que la función downgrade() existe y es llamable."""
        assert hasattr(migration_003, 'downgrade')
        assert callable(migration_003.downgrade)