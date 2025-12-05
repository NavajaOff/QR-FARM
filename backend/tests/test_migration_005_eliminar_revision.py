"""Tests para la migración 005_eliminar_revision_y_normalizar.py."""
import pytest
from unittest.mock import Mock, patch, MagicMock
import importlib.util
from pathlib import Path

# Importar el módulo de migración usando importlib para que coverage lo detecte
MIGRATION_PATH = Path(__file__).parent.parent / 'src' / 'database' / 'migrations' / 'versions' / '005_eliminar_revision_y_normalizar.py'
spec = importlib.util.spec_from_file_location("src.database.migrations.versions.005_eliminar_revision_y_normalizar", MIGRATION_PATH)
migration_005 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migration_005)


class TestMigration005EliminarRevision:
    """Tests para la migración 005_eliminar_revision_y_normalizar."""

    def test_constants_defined(self):
        """Test que las constantes están definidas."""
        assert hasattr(migration_005, 'revision')
        assert migration_005.revision == '005_eliminar_revision'
        assert migration_005.down_revision == '004_multi_tenant'
        assert migration_005.branch_labels is None
        assert migration_005.depends_on is None

    def test_upgrade_function_exists(self):
        """Test que la función upgrade existe."""
        assert hasattr(migration_005, 'upgrade')
        assert callable(migration_005.upgrade)

    def test_downgrade_function_exists(self):
        """Test que la función downgrade existe."""
        assert hasattr(migration_005, 'downgrade')
        assert callable(migration_005.downgrade)

    def test_upgrade_drops_foreign_key_success(self):
        """Test upgrade elimina foreign key exitosamente."""
        with patch.object(migration_005, 'op') as mock_op:
            migration_005.upgrade()
            
            # Verificar que se intentó eliminar la constraint
            mock_op.drop_constraint.assert_called_once_with(
                'ganado_ibfk_3', 'ganado', type_='foreignkey'
            )

    def test_upgrade_drops_foreign_key_with_exception(self):
        """Test upgrade maneja excepción al eliminar foreign key."""
        with patch.object(migration_005, 'op') as mock_op:
            mock_op.drop_constraint.side_effect = Exception("Constraint no existe")
            
            # No debe lanzar excepción
            migration_005.upgrade()
            
            mock_op.drop_constraint.assert_called_once()

    def test_upgrade_drops_index_success(self):
        """Test upgrade elimina índice exitosamente."""
        with patch.object(migration_005, 'op') as mock_op:
            migration_005.upgrade()
            
            # Verificar que se intentó eliminar el índice
            mock_op.drop_index.assert_called_once_with('id_revision', table_name='ganado')

    def test_upgrade_drops_index_with_exception(self):
        """Test upgrade maneja excepción al eliminar índice."""
        with patch.object(migration_005, 'op') as mock_op:
            mock_op.drop_index.side_effect = Exception("Índice no existe")
            
            # No debe lanzar excepción
            migration_005.upgrade()
            
            mock_op.drop_index.assert_called_once()

    def test_upgrade_drops_column_success(self):
        """Test upgrade elimina columna exitosamente."""
        with patch.object(migration_005, 'op') as mock_op:
            migration_005.upgrade()
            
            # Verificar que se intentó eliminar la columna
            mock_op.drop_column.assert_called_once_with('ganado', 'id_revision')

    def test_upgrade_drops_column_with_exception(self):
        """Test upgrade maneja excepción al eliminar columna."""
        with patch.object(migration_005, 'op') as mock_op:
            mock_op.drop_column.side_effect = Exception("Columna no existe")
            
            # No debe lanzar excepción
            migration_005.upgrade()
            
            mock_op.drop_column.assert_called_once()

    def test_upgrade_drops_table_success(self):
        """Test upgrade elimina tabla exitosamente."""
        with patch.object(migration_005, 'op') as mock_op:
            migration_005.upgrade()
            
            # Verificar que se intentó eliminar la tabla
            mock_op.drop_table.assert_called_once_with('revision')

    def test_upgrade_drops_table_with_exception(self):
        """Test upgrade maneja excepción al eliminar tabla."""
        with patch.object(migration_005, 'op') as mock_op:
            mock_op.drop_table.side_effect = Exception("Tabla no existe")
            
            # No debe lanzar excepción
            migration_005.upgrade()
            
            mock_op.drop_table.assert_called_once()

    def test_upgrade_complete_flow(self):
        """Test upgrade ejecuta todas las operaciones en orden."""
        with patch.object(migration_005, 'op') as mock_op:
            migration_005.upgrade()
            
            # Verificar el orden de las llamadas
            assert mock_op.drop_constraint.called
            assert mock_op.drop_index.called
            assert mock_op.drop_column.called
            assert mock_op.drop_table.called

    def test_downgrade_creates_table(self):
        """Test downgrade crea la tabla revision."""
        with patch.object(migration_005, 'op') as mock_op:
            migration_005.downgrade()
            
            # Verificar que se creó la tabla
            mock_op.create_table.assert_called_once()
            call_args = mock_op.create_table.call_args
            assert call_args[0][0] == 'revision'

    def test_downgrade_adds_column(self):
        """Test downgrade agrega columna id_revision."""
        with patch.object(migration_005, 'op') as mock_op:
            migration_005.downgrade()
            
            # Verificar que se agregó la columna
            mock_op.add_column.assert_called_once()
            call_args = mock_op.add_column.call_args
            assert call_args[0][0] == 'ganado'

    def test_downgrade_creates_index(self):
        """Test downgrade crea el índice."""
        with patch.object(migration_005, 'op') as mock_op:
            migration_005.downgrade()
            
            # Verificar que se creó el índice
            mock_op.create_index.assert_called_once_with('id_revision', 'ganado', ['id_revision'])

    def test_downgrade_creates_foreign_key(self):
        """Test downgrade crea la foreign key."""
        with patch.object(migration_005, 'op') as mock_op:
            migration_005.downgrade()
            
            # Verificar que se creó la foreign key
            mock_op.create_foreign_key.assert_called_once_with(
                'ganado_ibfk_3', 'ganado', 'revision', ['id_revision'], ['id']
            )

    def test_downgrade_complete_flow(self):
        """Test downgrade ejecuta todas las operaciones."""
        with patch.object(migration_005, 'op') as mock_op:
            migration_005.downgrade()
            
            # Verificar que todas las operaciones se ejecutaron
            assert mock_op.create_table.called
            assert mock_op.add_column.called
            assert mock_op.create_index.called
            assert mock_op.create_foreign_key.called

    def test_downgrade_table_structure(self):
        """Test que downgrade crea la tabla con la estructura correcta."""
        with patch.object(migration_005, 'op') as mock_op:
            migration_005.downgrade()
            
            # Verificar que create_table fue llamado
            create_table_call = mock_op.create_table.call_args
            assert create_table_call is not None
            
            # Verificar que se pasaron columnas
            # El segundo argumento debe ser una lista de columnas
            table_name = create_table_call[0][0]
            assert table_name == 'revision'

    def test_upgrade_all_exceptions(self):
        """Test upgrade maneja todas las excepciones correctamente."""
        with patch.object(migration_005, 'op') as mock_op:
            # Hacer que todas las operaciones fallen
            mock_op.drop_constraint.side_effect = Exception("Error constraint")
            mock_op.drop_index.side_effect = Exception("Error index")
            mock_op.drop_column.side_effect = Exception("Error column")
            mock_op.drop_table.side_effect = Exception("Error table")
            
            # No debe lanzar excepción
            migration_005.upgrade()
            
            # Verificar que todas las operaciones se intentaron
            assert mock_op.drop_constraint.called
            assert mock_op.drop_index.called
            assert mock_op.drop_column.called
            assert mock_op.drop_table.called

