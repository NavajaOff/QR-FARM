"""Tests para la migración 002_agregar_campos_baja_ganado.py."""
import pytest
from unittest.mock import Mock, patch
import importlib.util
from pathlib import Path

# Importar el módulo de migración usando importlib para que coverage lo detecte
MIGRATION_PATH = Path(__file__).parent.parent / 'src' / 'database' / 'migrations' / 'versions' / '002_agregar_campos_baja_ganado.py'
spec = importlib.util.spec_from_file_location("src.database.migrations.versions.002_agregar_campos_baja_ganado", MIGRATION_PATH)
migration_002 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migration_002)


class TestMigration002AgregarCamposBajaGanado:
    """Tests para la migración de agregar campos de baja para ganado."""

    def test_constants_defined(self):
        """Test que las constantes están definidas."""
        assert hasattr(migration_002, 'revision')
        assert migration_002.revision == '002_baja_ganado'
        assert migration_002.down_revision == 'aa0a1981a48a'
        assert migration_002.branch_labels is None
        assert migration_002.depends_on is None

    def test_upgrade_adds_columns_and_updates(self):
        """Test que upgrade() agrega las columnas y actualiza registros."""
        # Mockear op.add_column y op.execute directamente en el módulo
        mock_op = Mock()
        mock_op.add_column = Mock()
        mock_op.execute = Mock()

        # Reemplazar op en el módulo
        original_op = migration_002.op
        migration_002.op = mock_op

        try:
            # Ejecutar upgrade
            migration_002.upgrade()
        finally:
            # Restaurar op original
            migration_002.op = original_op

        # Verificar que se llamó add_column para cada columna nueva
        add_column_calls = mock_op.add_column.call_args_list
        assert len(add_column_calls) == 4, f"Se esperaban 4 llamadas a add_column, se obtuvieron {len(add_column_calls)}"

        # Verificar columnas específicas
        column_names = [call[0][1].name for call in add_column_calls]
        expected_columns = ['estado_baja', 'causa_baja', 'fecha_baja', 'observaciones_baja']
        for col in expected_columns:
            assert col in column_names, f"Columna {col} no fue agregada"

        # Verificar que se llamó execute para actualizar registros existentes
        assert mock_op.execute.call_count == 1
        execute_call = mock_op.execute.call_args[0][0]
        assert "UPDATE ganado SET estado_baja = 'activo' WHERE estado_baja IS NULL" in execute_call

    def test_downgrade_drops_columns(self):
        """Test que downgrade() elimina las columnas."""
        # Mockear op.drop_column directamente en el módulo
        mock_op = Mock()
        mock_op.drop_column = Mock()

        # Reemplazar op en el módulo
        original_op = migration_002.op
        migration_002.op = mock_op

        try:
            # Ejecutar downgrade
            migration_002.downgrade()
        finally:
            # Restaurar op original
            migration_002.op = original_op

        # Verificar que se llamó drop_column para cada columna
        drop_column_calls = mock_op.drop_column.call_args_list
        assert len(drop_column_calls) == 4, f"Se esperaban 4 llamadas a drop_column, se obtuvieron {len(drop_column_calls)}"

        # Verificar columnas eliminadas en orden correcto
        dropped_columns = [call[0][1] for call in drop_column_calls]
        expected_drops = ['observaciones_baja', 'fecha_baja', 'causa_baja', 'estado_baja']
        assert dropped_columns == expected_drops

    def test_upgrade_function_exists(self):
        """Test que la función upgrade() existe y es llamable."""
        assert hasattr(migration_002, 'upgrade')
        assert callable(migration_002.upgrade)

    def test_downgrade_function_exists(self):
        """Test que la función downgrade() existe y es llamable."""
        assert hasattr(migration_002, 'downgrade')
        assert callable(migration_002.downgrade)