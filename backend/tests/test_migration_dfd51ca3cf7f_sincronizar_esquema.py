"""Tests para la migración dfd51ca3cf7f_sincronizar_esquema_con_dump.py."""
import pytest
from unittest.mock import Mock, patch, MagicMock
import importlib.util
from pathlib import Path
import sqlalchemy as sa

# Importar el módulo de migración usando importlib para que coverage lo detecte
MIGRATION_PATH = Path(__file__).parent.parent / 'src' / 'database' / 'migrations' / 'versions' / 'dfd51ca3cf7f_sincronizar_esquema_con_dump.py'
spec = importlib.util.spec_from_file_location("src.database.migrations.versions.dfd51ca3cf7f_sincronizar_esquema_con_dump", MIGRATION_PATH)
migration_dfd51ca = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migration_dfd51ca)


class TestMigrationDfd51ca3cf7fSincronizarEsquema:
    """Tests para la migración dfd51ca3cf7f_sincronizar_esquema_con_dump."""

    def test_constants_defined(self):
        """Test que las constantes están definidas."""
        assert hasattr(migration_dfd51ca, 'revision')
        assert migration_dfd51ca.revision == 'dfd51ca3cf7f'
        assert hasattr(migration_dfd51ca, 'down_revision')
        assert migration_dfd51ca.down_revision == 'c10aea45c417'
        assert hasattr(migration_dfd51ca, 'branch_labels')
        assert migration_dfd51ca.branch_labels is None
        assert hasattr(migration_dfd51ca, 'depends_on')
        assert migration_dfd51ca.depends_on is None

    def test_upgrade_function_exists(self):
        """Test que la función upgrade existe."""
        assert hasattr(migration_dfd51ca, 'upgrade')
        assert callable(migration_dfd51ca.upgrade)

    def test_downgrade_function_exists(self):
        """Test que la función downgrade existe."""
        assert hasattr(migration_dfd51ca, 'downgrade')
        assert callable(migration_dfd51ca.downgrade)

    def test_agregar_constraint_unique_personas_constraint_not_exists(self):
        """Test _agregar_constraint_unique_personas cuando el constraint no existe."""
        mock_inspector = MagicMock()
        mock_inspector.get_unique_constraints.return_value = []
        
        with patch.object(migration_dfd51ca, 'op') as mock_op:
            migration_dfd51ca._agregar_constraint_unique_personas(mock_inspector)
            
            mock_inspector.get_unique_constraints.assert_called_once_with('personas')
            mock_op.create_unique_constraint.assert_called_once_with(
                'email',
                'personas',
                ['email', 'telefono']
            )

    def test_agregar_constraint_unique_personas_constraint_exists(self):
        """Test _agregar_constraint_unique_personas cuando el constraint ya existe."""
        mock_inspector = MagicMock()
        mock_inspector.get_unique_constraints.return_value = [
            {'name': 'email', 'column_names': ['email', 'telefono']}
        ]
        
        with patch.object(migration_dfd51ca, 'op') as mock_op:
            migration_dfd51ca._agregar_constraint_unique_personas(mock_inspector)
            
            mock_inspector.get_unique_constraints.assert_called_once_with('personas')
            mock_op.create_unique_constraint.assert_not_called()

    def test_agregar_constraint_unique_personas_with_exception(self):
        """Test _agregar_constraint_unique_personas maneja excepciones."""
        mock_inspector = MagicMock()
        mock_inspector.get_unique_constraints.side_effect = Exception("Error")
        
        with patch.object(migration_dfd51ca, 'op') as mock_op:
            with patch('builtins.print') as mock_print:
                migration_dfd51ca._agregar_constraint_unique_personas(mock_inspector)
                
                mock_print.assert_called_once()
                mock_op.create_unique_constraint.assert_not_called()

    def test_eliminar_columna_area_potrero_column_exists(self):
        """Test _eliminar_columna_area_potrero cuando la columna existe."""
        mock_inspector = MagicMock()
        mock_inspector.get_columns.return_value = [
            {'name': 'id'},
            {'name': 'nombre'},
            {'name': 'area'},
            {'name': 'hectareas'}
        ]
        
        with patch.object(migration_dfd51ca, 'op') as mock_op:
            migration_dfd51ca._eliminar_columna_area_potrero(mock_inspector)
            
            mock_inspector.get_columns.assert_called_once_with('potrero')
            mock_op.drop_column.assert_called_once_with('potrero', 'area')

    def test_eliminar_columna_area_potrero_column_not_exists(self):
        """Test _eliminar_columna_area_potrero cuando la columna no existe."""
        mock_inspector = MagicMock()
        mock_inspector.get_columns.return_value = [
            {'name': 'id'},
            {'name': 'nombre'},
            {'name': 'hectareas'}
        ]
        
        with patch.object(migration_dfd51ca, 'op') as mock_op:
            migration_dfd51ca._eliminar_columna_area_potrero(mock_inspector)
            
            mock_inspector.get_columns.assert_called_once_with('potrero')
            mock_op.drop_column.assert_not_called()

    def test_eliminar_columna_area_potrero_with_exception(self):
        """Test _eliminar_columna_area_potrero maneja excepciones."""
        mock_inspector = MagicMock()
        mock_inspector.get_columns.side_effect = Exception("Error")
        
        with patch.object(migration_dfd51ca, 'op') as mock_op:
            migration_dfd51ca._eliminar_columna_area_potrero(mock_inspector)
            
            mock_op.drop_column.assert_not_called()

    def test_asegurar_columna_not_null_column_nullable(self):
        """Test _asegurar_columna_not_null cuando la columna es nullable."""
        mock_inspector = MagicMock()
        mock_inspector.get_columns.return_value = [
            {'name': 'id', 'nullable': False},
            {'name': 'sexo', 'nullable': True}
        ]
        tipo = sa.Enum('macho', 'hembra')
        
        with patch.object(migration_dfd51ca, 'op') as mock_op:
            migration_dfd51ca._asegurar_columna_not_null(
                mock_inspector, 'ganado', 'sexo', tipo
            )
            
            mock_inspector.get_columns.assert_called_once_with('ganado')
            mock_op.alter_column.assert_called_once_with(
                'ganado', 'sexo', existing_type=tipo, nullable=False
            )

    def test_asegurar_columna_not_null_column_not_nullable(self):
        """Test _asegurar_columna_not_null cuando la columna ya es NOT NULL."""
        mock_inspector = MagicMock()
        mock_inspector.get_columns.return_value = [
            {'name': 'id', 'nullable': False},
            {'name': 'sexo', 'nullable': False}
        ]
        tipo = sa.Enum('macho', 'hembra')
        
        with patch.object(migration_dfd51ca, 'op') as mock_op:
            migration_dfd51ca._asegurar_columna_not_null(
                mock_inspector, 'ganado', 'sexo', tipo
            )
            
            mock_inspector.get_columns.assert_called_once_with('ganado')
            mock_op.alter_column.assert_not_called()

    def test_asegurar_columna_not_null_column_not_found(self):
        """Test _asegurar_columna_not_null cuando la columna no existe."""
        mock_inspector = MagicMock()
        mock_inspector.get_columns.return_value = [
            {'name': 'id', 'nullable': False}
        ]
        tipo = sa.Enum('macho', 'hembra')
        
        with patch.object(migration_dfd51ca, 'op') as mock_op:
            migration_dfd51ca._asegurar_columna_not_null(
                mock_inspector, 'ganado', 'sexo', tipo
            )
            
            mock_inspector.get_columns.assert_called_once_with('ganado')
            mock_op.alter_column.assert_not_called()

    def test_asegurar_columna_not_null_with_exception(self):
        """Test _asegurar_columna_not_null maneja excepciones."""
        mock_inspector = MagicMock()
        mock_inspector.get_columns.side_effect = Exception("Error")
        tipo = sa.Enum('macho', 'hembra')
        
        with patch.object(migration_dfd51ca, 'op') as mock_op:
            migration_dfd51ca._asegurar_columna_not_null(
                mock_inspector, 'ganado', 'sexo', tipo
            )
            
            mock_op.alter_column.assert_not_called()

    def test_asegurar_tenant_id_not_null(self):
        """Test _asegurar_tenant_id_not_null."""
        mock_inspector = MagicMock()
        mock_inspector.get_columns.return_value = [
            {'name': 'id', 'nullable': False},
            {'name': 'tenant_id', 'nullable': True}
        ]
        
        with patch.object(migration_dfd51ca, '_asegurar_columna_not_null') as mock_helper:
            migration_dfd51ca._asegurar_tenant_id_not_null(mock_inspector, 'ganado')
            
            assert mock_helper.call_count == 1
            call_args = mock_helper.call_args
            assert call_args[0][0] == mock_inspector
            assert call_args[0][1] == 'ganado'
            assert call_args[0][2] == 'tenant_id'
            assert isinstance(call_args[0][3], sa.Integer)

    def test_upgrade_complete_flow(self):
        """Test upgrade ejecuta todas las operaciones."""
        mock_connection = MagicMock()
        mock_inspector = MagicMock()
        mock_inspector.get_unique_constraints.return_value = []
        
        # Configurar get_columns para retornar columnas nullable según la tabla
        def get_columns_side_effect(table_name):
            if table_name == 'potrero':
                return [
                    {'name': 'id'},
                    {'name': 'area'},
                    {'name': 'nombre'},
                    {'name': 'tenant_id', 'nullable': True}
                ]
            elif table_name == 'ganado':
                return [
                    {'name': 'id'},
                    {'name': 'sexo', 'nullable': True},
                    {'name': 'tenant_id', 'nullable': True}
                ]
            else:
                return [
                    {'name': 'id'},
                    {'name': 'tenant_id', 'nullable': True}
                ]
        
        mock_inspector.get_columns.side_effect = get_columns_side_effect
        
        with patch.object(migration_dfd51ca, 'op') as mock_op:
            mock_op.get_bind.return_value = mock_connection
            with patch('sqlalchemy.inspect', return_value=mock_inspector):
                migration_dfd51ca.upgrade()
                
                mock_op.get_bind.assert_called_once()
                mock_op.create_unique_constraint.assert_called_once()
                mock_op.drop_column.assert_called_once()
                # Verificar que alter_column se llamó para sexo y para cada tenant_id
                assert mock_op.alter_column.call_count >= 4
                # Verificar que se llamó para sexo
                sexo_calls = [call for call in mock_op.alter_column.call_args_list
                             if call[0][0] == 'ganado' and call[0][1] == 'sexo']
                assert len(sexo_calls) == 1
                # Verificar que se llamó para tenant_id en todas las tablas
                tenant_tables = ['ganado', 'potrero', 'vacunacion', 'qr']
                for tabla in tenant_tables:
                    tenant_calls = [call for call in mock_op.alter_column.call_args_list
                                  if call[0][0] == tabla and call[0][1] == 'tenant_id']
                    assert len(tenant_calls) == 1

    def test_downgrade_drops_constraint_success(self):
        """Test downgrade elimina constraint exitosamente."""
        with patch.object(migration_dfd51ca, 'op') as mock_op:
            migration_dfd51ca.downgrade()
            
            mock_op.drop_constraint.assert_called_once_with(
                'email', 'personas', type_='unique'
            )

    def test_downgrade_drops_constraint_with_exception(self):
        """Test downgrade maneja excepción al eliminar constraint."""
        with patch.object(migration_dfd51ca, 'op') as mock_op:
            mock_op.drop_constraint.side_effect = Exception("Constraint no existe")
            
            migration_dfd51ca.downgrade()
            
            mock_op.drop_constraint.assert_called_once()

    def test_downgrade_adds_area_column_not_exists(self):
        """Test downgrade agrega columna area cuando no existe."""
        mock_connection = MagicMock()
        mock_inspector = MagicMock()
        mock_inspector.get_columns.return_value = [
            {'name': 'id'},
            {'name': 'nombre'},
            {'name': 'hectareas'}
        ]
        
        with patch.object(migration_dfd51ca, 'op') as mock_op:
            mock_op.get_bind.return_value = mock_connection
            with patch('sqlalchemy.inspect', return_value=mock_inspector):
                migration_dfd51ca.downgrade()
                
                mock_op.add_column.assert_called_once()
                call_args = mock_op.add_column.call_args
                assert call_args[0][0] == 'potrero'
                assert isinstance(call_args[0][1], sa.Column)
                assert call_args[0][1].name == 'area'

    def test_downgrade_adds_area_column_already_exists(self):
        """Test downgrade no agrega columna area cuando ya existe."""
        mock_connection = MagicMock()
        mock_inspector = MagicMock()
        mock_inspector.get_columns.return_value = [
            {'name': 'id'},
            {'name': 'nombre'},
            {'name': 'area'},
            {'name': 'hectareas'}
        ]
        
        with patch.object(migration_dfd51ca, 'op') as mock_op:
            mock_op.get_bind.return_value = mock_connection
            with patch('sqlalchemy.inspect', return_value=mock_inspector):
                migration_dfd51ca.downgrade()
                
                mock_op.add_column.assert_not_called()

    def test_downgrade_adds_area_column_with_exception(self):
        """Test downgrade maneja excepción al agregar columna."""
        mock_connection = MagicMock()
        mock_inspector = MagicMock()
        mock_inspector.get_columns.side_effect = Exception("Error")
        
        with patch.object(migration_dfd51ca, 'op') as mock_op:
            mock_op.get_bind.return_value = mock_connection
            with patch('sqlalchemy.inspect', return_value=mock_inspector):
                migration_dfd51ca.downgrade()
                
                mock_op.add_column.assert_not_called()

    def test_downgrade_makes_tenant_id_nullable(self):
        """Test downgrade hace tenant_id nullable en todas las tablas."""
        mock_connection = MagicMock()
        mock_inspector = MagicMock()
        
        with patch.object(migration_dfd51ca, 'op') as mock_op:
            mock_op.get_bind.return_value = mock_connection
            with patch('sqlalchemy.inspect', return_value=mock_inspector):
                migration_dfd51ca.downgrade()
                
                expected_tables = ['ganado', 'potrero', 'vacunacion', 'qr']
                assert mock_op.alter_column.call_count == len(expected_tables)
                
                for tabla in expected_tables:
                    calls = [call for call in mock_op.alter_column.call_args_list
                            if call[0][0] == tabla and call[0][1] == 'tenant_id']
                    assert len(calls) == 1
                    call_kwargs = calls[0][1]
                    assert call_kwargs['nullable'] is True
                    assert isinstance(call_kwargs['existing_type'], sa.Integer)

    def test_downgrade_makes_tenant_id_nullable_with_exception(self):
        """Test downgrade maneja excepciones al hacer tenant_id nullable."""
        mock_connection = MagicMock()
        mock_inspector = MagicMock()
        
        with patch.object(migration_dfd51ca, 'op') as mock_op:
            mock_op.get_bind.return_value = mock_connection
            mock_op.alter_column.side_effect = Exception("Error")
            with patch('sqlalchemy.inspect', return_value=mock_inspector):
                migration_dfd51ca.downgrade()
                
                expected_tables = ['ganado', 'potrero', 'vacunacion', 'qr']
                assert mock_op.alter_column.call_count == len(expected_tables)

    def test_downgrade_complete_flow(self):
        """Test downgrade ejecuta todas las operaciones."""
        mock_connection = MagicMock()
        mock_inspector = MagicMock()
        mock_inspector.get_columns.return_value = [
            {'name': 'id'},
            {'name': 'nombre'}
        ]
        
        with patch.object(migration_dfd51ca, 'op') as mock_op:
            mock_op.get_bind.return_value = mock_connection
            with patch('sqlalchemy.inspect', return_value=mock_inspector):
                migration_dfd51ca.downgrade()
                
                mock_op.drop_constraint.assert_called_once()
                mock_op.add_column.assert_called_once()
                assert mock_op.alter_column.call_count == 4  # 4 tablas con tenant_id

