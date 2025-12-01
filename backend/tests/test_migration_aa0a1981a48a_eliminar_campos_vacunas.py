"""Tests para la migración aa0a1981a48a_eliminar_campos_vacunas.py."""
import pytest
from unittest.mock import Mock, patch
import importlib.util
from pathlib import Path

# Importar el módulo de migración usando importlib para que coverage lo detecte
MIGRATION_PATH = Path(__file__).parent.parent / 'src' / 'database' / 'migrations' / 'versions' / 'aa0a1981a48a_eliminar_campos_vacunas.py'
spec = importlib.util.spec_from_file_location("src.database.migrations.versions.aa0a1981a48a_eliminar_campos_vacunas", MIGRATION_PATH)
migration_aa0a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migration_aa0a)


class TestMigrationAa0a1981a48aEliminarCamposVacunas:
    """Tests para la migración de eliminar campos de vacunación."""

    def test_constants_defined(self):
        """Test que las constantes están definidas."""
        assert hasattr(migration_aa0a, 'revision')
        assert migration_aa0a.revision == 'aa0a1981a48a'
        assert migration_aa0a.down_revision == '001'
        assert migration_aa0a.branch_labels is None
        assert migration_aa0a.depends_on is None

    def test_upgrade_drops_columns(self):
        """Test que upgrade() elimina las columnas de vacunacion."""
        # Mockear op.drop_column directamente en el módulo
        mock_op = Mock()
        mock_op.drop_column = Mock()

        # Reemplazar op en el módulo
        original_op = migration_aa0a.op
        migration_aa0a.op = mock_op

        try:
            # Ejecutar upgrade
            migration_aa0a.upgrade()
        finally:
            # Restaurar op original
            migration_aa0a.op = original_op

        # Verificar que se llamó drop_column para cada columna
        drop_column_calls = mock_op.drop_column.call_args_list
        assert len(drop_column_calls) == 3, f"Se esperaban 3 llamadas a drop_column, se obtuvieron {len(drop_column_calls)}"

        # Verificar columnas eliminadas
        dropped_columns = [call[0][1] for call in drop_column_calls]
        expected_drops = ['nombre_animal', 'fecha_inicio', 'fecha_fin']
        assert dropped_columns == expected_drops

    def test_downgrade_adds_columns(self):
        """Test que downgrade() agrega las columnas de vacunacion."""
        # Mockear op.add_column directamente en el módulo
        mock_op = Mock()
        mock_op.add_column = Mock()

        # Reemplazar op en el módulo
        original_op = migration_aa0a.op
        migration_aa0a.op = mock_op

        try:
            # Ejecutar downgrade
            migration_aa0a.downgrade()
        finally:
            # Restaurar op original
            migration_aa0a.op = original_op

        # Verificar que se llamó add_column para cada columna
        add_column_calls = mock_op.add_column.call_args_list
        assert len(add_column_calls) == 3, f"Se esperaban 3 llamadas a add_column, se obtuvieron {len(add_column_calls)}"

        # Verificar columnas agregadas
        column_names = [call[0][1].name for call in add_column_calls]
        expected_columns = ['nombre_animal', 'fecha_inicio', 'fecha_fin']
        for col in expected_columns:
            assert col in column_names

    def test_upgrade_function_exists(self):
        """Test que la función upgrade() existe y es llamable."""
        assert hasattr(migration_aa0a, 'upgrade')
        assert callable(migration_aa0a.upgrade)

    def test_downgrade_function_exists(self):
        """Test que la función downgrade() existe y es llamable."""
        assert hasattr(migration_aa0a, 'downgrade')
        assert callable(migration_aa0a.downgrade)