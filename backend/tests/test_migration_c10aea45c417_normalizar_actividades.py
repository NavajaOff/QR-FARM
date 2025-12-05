"""Tests para la migración c10aea45c417_normalizar_actividades_potrero.py."""
import pytest
from unittest.mock import Mock, patch, MagicMock
import importlib.util
from pathlib import Path

# Importar el módulo de migración usando importlib para que coverage lo detecte
MIGRATION_PATH = Path(__file__).parent.parent / 'src' / 'database' / 'migrations' / 'versions' / 'c10aea45c417_normalizar_actividades_potrero.py'
spec = importlib.util.spec_from_file_location("src.database.migrations.versions.c10aea45c417_normalizar_actividades_potrero", MIGRATION_PATH)
migration_c10aea = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migration_c10aea)


class TestMigrationC10aea45c417NormalizarActividades:
    """Tests para la migración c10aea45c417_normalizar_actividades_potrero."""

    def test_constants_defined(self):
        """Test que las constantes están definidas."""
        assert hasattr(migration_c10aea, 'revision')
        assert migration_c10aea.revision == 'c10aea45c417'
        assert migration_c10aea.down_revision == '005_eliminar_revision'
        assert migration_c10aea.branch_labels is None
        assert migration_c10aea.depends_on is None

    def test_upgrade_function_exists(self):
        """Test que la función upgrade existe."""
        assert hasattr(migration_c10aea, 'upgrade')
        assert callable(migration_c10aea.upgrade)

    def test_downgrade_function_exists(self):
        """Test que la función downgrade existe."""
        assert hasattr(migration_c10aea, 'downgrade')
        assert callable(migration_c10aea.downgrade)

    def test_upgrade_creates_table(self):
        """Test upgrade crea la tabla historial_potrero."""
        with patch.object(migration_c10aea, 'op') as mock_op:
            migration_c10aea.upgrade()
            
            # Verificar que se creó la tabla
            mock_op.create_table.assert_called_once()
            call_args = mock_op.create_table.call_args
            assert call_args[0][0] == 'historial_potrero'

    def test_upgrade_creates_indexes(self):
        """Test upgrade crea todos los índices."""
        with patch.object(migration_c10aea, 'op') as mock_op:
            migration_c10aea.upgrade()
            
            # Verificar que se crearon los 4 índices
            assert mock_op.create_index.call_count == 4
            index_names = [call[0][0] for call in mock_op.create_index.call_args_list]
            assert 'idx_historial_potrero_potrero' in index_names
            assert 'idx_historial_potrero_tipo' in index_names
            assert 'idx_historial_potrero_fecha' in index_names
            assert 'idx_historial_potrero_tenant' in index_names

    def test_upgrade_migrates_fecha_ultimo_uso(self):
        """Test upgrade migra fecha_ultimo_uso."""
        with patch.object(migration_c10aea, 'op') as mock_op:
            migration_c10aea.upgrade()
            
            # Verificar que se ejecutó el INSERT para fecha_ultimo_uso
            execute_calls = [call[0][0] for call in mock_op.execute.call_args_list]
            fecha_uso_migration = any('fecha_ultimo_uso' in call and 'tipo_evento' in call and "'uso'" in call for call in execute_calls)
            assert fecha_uso_migration

    def test_upgrade_migrates_ultima_limpieza(self):
        """Test upgrade migra ultima_limpieza."""
        with patch.object(migration_c10aea, 'op') as mock_op:
            migration_c10aea.upgrade()
            
            # Verificar que se ejecutó el INSERT para ultima_limpieza
            execute_calls = [call[0][0] for call in mock_op.execute.call_args_list]
            ultima_limpieza_migration = any('ultima_limpieza' in call and "'limpieza'" in call and 'observaciones' not in call for call in execute_calls)
            assert ultima_limpieza_migration

    def test_upgrade_migrates_proxima_limpieza(self):
        """Test upgrade migra proxima_limpieza."""
        with patch.object(migration_c10aea, 'op') as mock_op:
            migration_c10aea.upgrade()
            
            # Verificar que se ejecutó el INSERT para proxima_limpieza
            execute_calls = [call[0][0] for call in mock_op.execute.call_args_list]
            proxima_limpieza_migration = any('proxima_limpieza' in call and "'Programada'" in call for call in execute_calls)
            assert proxima_limpieza_migration

    def test_upgrade_drops_columns(self):
        """Test upgrade elimina las columnas de potrero."""
        with patch.object(migration_c10aea, 'op') as mock_op:
            migration_c10aea.upgrade()
            
            # Verificar que se intentaron eliminar las 3 columnas
            drop_column_calls = [call[0] for call in mock_op.drop_column.call_args_list]
            column_names = [call[1] for call in drop_column_calls]
            assert 'fecha_ultimo_uso' in column_names
            assert 'ultima_limpieza' in column_names
            assert 'proxima_limpieza' in column_names

    def test_upgrade_drops_column_with_exception(self):
        """Test upgrade maneja excepción al eliminar columnas."""
        with patch.object(migration_c10aea, 'op') as mock_op:
            mock_op.drop_column.side_effect = Exception("Columna no existe")
            
            # No debe lanzar excepción
            migration_c10aea.upgrade()
            
            # Verificar que se intentaron eliminar las columnas
            assert mock_op.drop_column.call_count == 3

    def test_upgrade_complete_flow(self):
        """Test upgrade ejecuta todas las operaciones en orden."""
        with patch.object(migration_c10aea, 'op') as mock_op:
            migration_c10aea.upgrade()
            
            # Verificar que todas las operaciones se ejecutaron
            assert mock_op.create_table.called
            assert mock_op.create_index.called
            assert mock_op.execute.called
            assert mock_op.drop_column.called

    def test_downgrade_adds_columns(self):
        """Test downgrade agrega las columnas a potrero."""
        with patch.object(migration_c10aea, 'op') as mock_op:
            migration_c10aea.downgrade()
            
            # Verificar que se agregaron las 3 columnas
            assert mock_op.add_column.call_count == 3
            add_column_calls = [call[0] for call in mock_op.add_column.call_args_list]
            table_names = [call[0] for call in add_column_calls]
            assert all(name == 'potrero' for name in table_names)

    def test_downgrade_migrates_data_back(self):
        """Test downgrade migra datos de vuelta desde historial_potrero."""
        with patch.object(migration_c10aea, 'op') as mock_op:
            migration_c10aea.downgrade()
            
            # Verificar que se ejecutaron los 3 UPDATE statements
            execute_calls = [call[0][0] for call in mock_op.execute.call_args_list]
            update_calls = [call for call in execute_calls if 'UPDATE potrero' in call]
            assert len(update_calls) == 3

    def test_downgrade_migrates_fecha_ultimo_uso_back(self):
        """Test downgrade migra fecha_ultimo_uso de vuelta."""
        with patch.object(migration_c10aea, 'op') as mock_op:
            migration_c10aea.downgrade()
            
            # Verificar que se ejecutó el UPDATE para fecha_ultimo_uso
            execute_calls = [call[0][0] for call in mock_op.execute.call_args_list]
            fecha_uso_update = any('fecha_ultimo_uso' in call and "tipo_evento = 'uso'" in call for call in execute_calls)
            assert fecha_uso_update

    def test_downgrade_migrates_ultima_limpieza_back(self):
        """Test downgrade migra ultima_limpieza de vuelta."""
        with patch.object(migration_c10aea, 'op') as mock_op:
            migration_c10aea.downgrade()
            
            # Verificar que se ejecutó el UPDATE para ultima_limpieza
            execute_calls = [call[0][0] for call in mock_op.execute.call_args_list]
            ultima_limpieza_update = any('ultima_limpieza' in call and "tipo_evento = 'limpieza'" in call and "observaciones != 'Programada'" in call for call in execute_calls)
            assert ultima_limpieza_update

    def test_downgrade_migrates_proxima_limpieza_back(self):
        """Test downgrade migra proxima_limpieza de vuelta."""
        with patch.object(migration_c10aea, 'op') as mock_op:
            migration_c10aea.downgrade()
            
            # Verificar que se ejecutó el UPDATE para proxima_limpieza
            execute_calls = [call[0][0] for call in mock_op.execute.call_args_list]
            proxima_limpieza_update = any('proxima_limpieza' in call and "observaciones = 'Programada'" in call and 'fecha_evento > NOW()' in call for call in execute_calls)
            assert proxima_limpieza_update

    def test_downgrade_drops_indexes(self):
        """Test downgrade elimina los índices."""
        with patch.object(migration_c10aea, 'op') as mock_op:
            migration_c10aea.downgrade()
            
            # Verificar que se intentaron eliminar los 4 índices
            assert mock_op.drop_index.call_count == 4
            drop_index_calls = [call[0][0] for call in mock_op.drop_index.call_args_list]
            assert 'idx_historial_potrero_tenant' in drop_index_calls
            assert 'idx_historial_potrero_fecha' in drop_index_calls
            assert 'idx_historial_potrero_tipo' in drop_index_calls
            assert 'idx_historial_potrero_potrero' in drop_index_calls

    def test_downgrade_drops_index_with_exception(self):
        """Test downgrade maneja excepción al eliminar índices."""
        with patch.object(migration_c10aea, 'op') as mock_op:
            mock_op.drop_index.side_effect = Exception("Índice no existe")
            
            # No debe lanzar excepción
            migration_c10aea.downgrade()
            
            # Verificar que se intentaron eliminar los índices
            assert mock_op.drop_index.call_count == 4

    def test_downgrade_drops_table(self):
        """Test downgrade elimina la tabla historial_potrero."""
        with patch.object(migration_c10aea, 'op') as mock_op:
            migration_c10aea.downgrade()
            
            # Verificar que se eliminó la tabla
            mock_op.drop_table.assert_called_once_with('historial_potrero')

    def test_downgrade_drops_enum(self):
        """Test downgrade elimina el enum tipo_evento_potrero."""
        with patch.object(migration_c10aea, 'op') as mock_op:
            migration_c10aea.downgrade()
            
            # Verificar que se ejecutó el DROP TYPE
            execute_calls = [call[0][0] for call in mock_op.execute.call_args_list]
            drop_enum_call = any('DROP TYPE' in call and 'tipo_evento_potrero' in call for call in execute_calls)
            assert drop_enum_call

    def test_downgrade_drops_enum_with_exception(self):
        """Test downgrade maneja excepción al eliminar enum."""
        with patch.object(migration_c10aea, 'op') as mock_op:
            # Hacer que el último execute (DROP TYPE) falle
            def side_effect(*args):
                if 'DROP TYPE' in str(args[0]):
                    raise Exception("Enum no existe")
                return None
            
            mock_op.execute.side_effect = side_effect
            
            # No debe lanzar excepción
            migration_c10aea.downgrade()
            
            # Verificar que se intentó eliminar el enum
            execute_calls = [call[0][0] for call in mock_op.execute.call_args_list]
            drop_enum_call = any('DROP TYPE' in call for call in execute_calls)
            assert drop_enum_call

    def test_downgrade_complete_flow(self):
        """Test downgrade ejecuta todas las operaciones."""
        with patch.object(migration_c10aea, 'op') as mock_op:
            migration_c10aea.downgrade()
            
            # Verificar que todas las operaciones se ejecutaron
            assert mock_op.add_column.called
            assert mock_op.execute.called
            assert mock_op.drop_index.called
            assert mock_op.drop_table.called

    def test_upgrade_executes_all_migrations(self):
        """Test upgrade ejecuta las 3 migraciones de datos."""
        with patch.object(migration_c10aea, 'op') as mock_op:
            migration_c10aea.upgrade()
            
            # Verificar que se ejecutaron 3 INSERT statements
            execute_calls = [call[0][0] for call in mock_op.execute.call_args_list]
            insert_calls = [call for call in execute_calls if 'INSERT INTO historial_potrero' in call]
            assert len(insert_calls) == 3

    def test_downgrade_executes_all_updates(self):
        """Test downgrade ejecuta los 3 UPDATE statements."""
        with patch.object(migration_c10aea, 'op') as mock_op:
            migration_c10aea.downgrade()
            
            # Verificar que se ejecutaron 3 UPDATE statements + 1 DROP TYPE
            execute_calls = [call[0][0] for call in mock_op.execute.call_args_list]
            assert len(execute_calls) == 4  # 3 UPDATEs + 1 DROP TYPE

