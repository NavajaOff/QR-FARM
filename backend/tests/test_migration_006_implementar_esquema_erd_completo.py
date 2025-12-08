"""Tests para la migración 006_implementar_esquema_erd_completo.py."""
import pytest
from unittest.mock import Mock, patch, MagicMock
import importlib.util
from pathlib import Path

# Importar el módulo de migración usando importlib para que coverage lo detecte
MIGRATION_PATH = Path(__file__).parent.parent / 'src' / 'database' / 'migrations' / 'versions' / '006_implementar_esquema_erd_completo.py'
spec = importlib.util.spec_from_file_location("src.database.migrations.versions.006_implementar_esquema_erd_completo", MIGRATION_PATH)
migration_006 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(migration_006)


class TestMigration006ImplementarEsquemaERDCompleto:
    """Tests para la migración que implementa el esquema completo según ERD."""

    def test_constants_defined(self):
        """Test que las constantes están definidas."""
        assert hasattr(migration_006, 'TENANT_ID_FK')
        assert migration_006.TENANT_ID_FK == 'tenants.id'
        assert hasattr(migration_006, 'revision')
        assert migration_006.revision == '006_esquema_erd'
        assert migration_006.down_revision == 'dfd51ca3cf7f'
        assert migration_006.branch_labels is None
        assert migration_006.depends_on is None

    def test_upgrade_function_exists(self):
        """Test que la función upgrade() existe y es llamable."""
        assert hasattr(migration_006, 'upgrade')
        assert callable(migration_006.upgrade)

    def test_downgrade_function_exists(self):
        """Test que la función downgrade() existe y es llamable."""
        assert hasattr(migration_006, 'downgrade')
        assert callable(migration_006.downgrade)

    @patch('sqlalchemy.inspect')
    def test_upgrade_calls_all_functions(self, mock_inspect):
        """Test que upgrade() llama a todas las funciones de actualización."""
        # Mock del inspector
        mock_inspector = MagicMock()
        mock_inspector.get_table_names.return_value = []
        mock_inspector.get_columns.return_value = []
        mock_inspector.get_indexes.return_value = []
        mock_inspector.get_unique_constraints.return_value = []
        mock_inspector.get_foreign_keys.return_value = []
        mock_inspect.return_value = mock_inspector

        # Mock de op
        mock_op = MagicMock()
        original_op = migration_006.op
        migration_006.op = mock_op

        try:
            migration_006.upgrade()
        finally:
            migration_006.op = original_op

        # Verificar que se llamaron las funciones principales
        # Nota: Las funciones privadas no se pueden mockear fácilmente,
        # pero podemos verificar que op fue usado
        assert mock_op.create_table.called or mock_op.add_column.called or mock_op.execute.called

    @patch('sqlalchemy.inspect')
    def test_crear_tabla_estado_potrero(self, mock_inspect):
        """Test que _crear_tabla_estado_potrero funciona correctamente."""
        mock_inspector = MagicMock()
        mock_inspector.get_table_names.return_value = []  # Tabla no existe
        mock_inspect.return_value = mock_inspector

        mock_op = MagicMock()
        original_op = migration_006.op
        migration_006.op = mock_op

        try:
            migration_006._crear_tabla_estado_potrero(mock_inspector)
        finally:
            migration_006.op = original_op

        # Verificar que se creó la tabla
        mock_op.create_table.assert_called_once()
        args, kwargs = mock_op.create_table.call_args
        assert args[0] == 'estado_potrero'

        # Verificar que se insertaron datos por defecto
        mock_op.execute.assert_called_once()

    @patch('sqlalchemy.inspect')
    def test_crear_tabla_historial_potreros_case_1(self, mock_inspect):
        """Test caso 1: Solo existe historial_potrero."""
        mock_inspector = MagicMock()
        mock_inspector.get_table_names.return_value = ['historial_potrero']  # Solo la tabla antigua
        mock_inspector.get_indexes.return_value = [{'name': 'idx_test'}]
        mock_inspect.return_value = mock_inspector

        mock_op = MagicMock()
        original_op = migration_006.op
        migration_006.op = mock_op

        try:
            migration_006._crear_tabla_historial_potreros(mock_inspector)
        finally:
            migration_006.op = original_op

        # Verificar que se creó la nueva tabla
        assert mock_op.create_table.called
        # Verificar que se migraron datos
        assert mock_op.execute.called
        # Verificar que se eliminó la tabla antigua
        mock_op.drop_table.assert_called_once_with('historial_potrero')

    @patch('sqlalchemy.inspect')
    def test_crear_tabla_historial_potreros_case_3(self, mock_inspect):
        """Test caso 3: No existe historial_potreros."""
        mock_inspector = MagicMock()
        mock_inspector.get_table_names.return_value = []  # Ninguna tabla existe
        mock_inspect.return_value = mock_inspector

        mock_op = MagicMock()
        original_op = migration_006.op
        migration_006.op = mock_op

        try:
            migration_006._crear_tabla_historial_potreros(mock_inspector)
        finally:
            migration_006.op = original_op

        # Verificar que se creó la nueva tabla
        mock_op.create_table.assert_called_once()
        args, kwargs = mock_op.create_table.call_args
        assert args[0] == 'historial_potreros'

    @patch('sqlalchemy.inspect')
    def test_actualizar_tabla_personas(self, mock_inspect):
        """Test que _actualizar_tabla_personas funciona correctamente."""
        mock_inspector = MagicMock()
        mock_inspector.get_table_names.return_value = ['personas']
        mock_inspector.get_columns.return_value = [{'name': 'id'}, {'name': 'nombre'}]  # tenant_id no existe
        mock_inspector.get_unique_constraints.return_value = []
        mock_inspect.return_value = mock_inspector

        mock_op = MagicMock()
        original_op = migration_006.op
        migration_006.op = mock_op

        try:
            migration_006._actualizar_tabla_personas(mock_inspector)
        finally:
            migration_006.op = original_op

        # Verificar que se agregó tenant_id
        mock_op.add_column.assert_called_once()
        args, kwargs = mock_op.add_column.call_args
        assert args[0] == 'personas'
        assert args[1].name == 'tenant_id'
        # Verificar que usa la constante
        assert migration_006.TENANT_ID_FK in str(args[1].foreign_keys)

    @patch('sqlalchemy.inspect')
    def test_actualizar_tabla_potrero(self, mock_inspect):
        """Test que _actualizar_tabla_potrero funciona correctamente."""
        mock_inspector = MagicMock()
        mock_inspector.get_table_names.return_value = ['potrero']
        mock_inspector.get_columns.return_value = [{'name': 'id'}, {'name': 'nombre'}]  # Campos faltan
        mock_inspect.return_value = mock_inspector

        mock_op = MagicMock()
        original_op = migration_006.op
        migration_006.op = mock_op

        try:
            migration_006._actualizar_tabla_potrero(mock_inspector)
        finally:
            migration_006.op = original_op

        # Verificar que se agregaron múltiples columnas
        assert mock_op.add_column.call_count >= 4  # id_estado_potrero, area, fecha_creacion, fecha_actualizacion, tenant_id

    @patch('sqlalchemy.inspect')
    def test_actualizar_tabla_ganado(self, mock_inspect):
        """Test que _actualizar_tabla_ganado funciona correctamente."""
        mock_inspector = MagicMock()
        mock_inspector.get_table_names.return_value = ['ganado']
        mock_inspector.get_columns.return_value = [{'name': 'id'}, {'name': 'nombre'}]  # tenant_id no existe
        mock_inspect.return_value = mock_inspector

        mock_op = MagicMock()
        original_op = migration_006.op
        migration_006.op = mock_op

        try:
            migration_006._actualizar_tabla_ganado(mock_inspector)
        finally:
            migration_006.op = original_op

        # Verificar que se agregó tenant_id
        mock_op.add_column.assert_called_once()
        args, kwargs = mock_op.add_column.call_args
        assert args[0] == 'ganado'
        assert args[1].name == 'tenant_id'
        assert migration_006.TENANT_ID_FK in str(args[1].foreign_keys)

    @patch('sqlalchemy.inspect')
    def test_actualizar_tabla_vacunacion(self, mock_inspect):
        """Test que _actualizar_tabla_vacunacion funciona correctamente."""
        mock_inspector = MagicMock()
        mock_inspector.get_table_names.return_value = ['vacunacion']
        mock_inspector.get_columns.return_value = [
            {'name': 'id'}, {'name': 'nombre_animal'}, {'name': 'fecha_inicio'}, {'name': 'fecha_fin'}
        ]  # Campos a eliminar existen, tenant_id no
        mock_inspector.get_foreign_keys.return_value = []
        mock_inspect.return_value = mock_inspector

        mock_op = MagicMock()
        original_op = migration_006.op
        migration_006.op = mock_op

        try:
            migration_006._actualizar_tabla_vacunacion(mock_inspector)
        finally:
            migration_006.op = original_op

        # Verificar que se eliminaron campos obsoletos
        drop_calls = [call for call in mock_op.drop_column.call_args_list]
        assert len(drop_calls) >= 3  # nombre_animal, fecha_inicio, fecha_fin

        # Verificar que se agregó tenant_id
        add_calls = [call for call in mock_op.add_column.call_args_list]
        tenant_calls = [call for call in add_calls if call[0][1].name == 'tenant_id']
        assert len(tenant_calls) == 1
        assert migration_006.TENANT_ID_FK in str(tenant_calls[0][0][1].foreign_keys)

    @patch('sqlalchemy.inspect')
    def test_actualizar_tabla_qr(self, mock_inspect):
        """Test que _actualizar_tabla_qr funciona correctamente."""
        mock_inspector = MagicMock()
        mock_inspector.get_table_names.return_value = ['qr']
        mock_inspector.get_columns.return_value = [{'name': 'id'}, {'name': 'codigo_qr'}]  # tenant_id no existe
        mock_inspect.return_value = mock_inspector

        mock_op = MagicMock()
        original_op = migration_006.op
        migration_006.op = mock_op

        try:
            migration_006._actualizar_tabla_qr(mock_inspector)
        finally:
            migration_006.op = original_op

        # Verificar que se agregó tenant_id
        mock_op.add_column.assert_called_once()
        args, kwargs = mock_op.add_column.call_args
        assert args[0] == 'qr'
        assert args[1].name == 'tenant_id'
        assert migration_006.TENANT_ID_FK in str(args[1].foreign_keys)

    @patch('sqlalchemy.inspect')
    def test_actualizar_tabla_usuarios(self, mock_inspect):
        """Test que _actualizar_tabla_usuarios funciona correctamente."""
        mock_inspector = MagicMock()
        mock_inspector.get_table_names.return_value = ['usuarios']
        mock_inspector.get_columns.return_value = [{'name': 'id'}, {'name': 'username'}]  # tenant_id no existe
        mock_inspect.return_value = mock_inspector

        mock_op = MagicMock()
        original_op = migration_006.op
        migration_006.op = mock_op

        try:
            migration_006._actualizar_tabla_usuarios(mock_inspector)
        finally:
            migration_006.op = original_op

        # Verificar que se agregó tenant_id
        mock_op.add_column.assert_called_once()
        args, kwargs = mock_op.add_column.call_args
        assert args[0] == 'usuarios'
        assert args[1].name == 'tenant_id'
        assert migration_006.TENANT_ID_FK in str(args[1].foreign_keys)

    @patch('sqlalchemy.inspect')
    def test_crear_indices(self, mock_inspect):
        """Test que _crear_indices funciona correctamente."""
        mock_inspector = MagicMock()
        mock_inspector.get_table_names.return_value = ['historial_potreros']
        mock_inspector.get_indexes.return_value = []  # Índice no existe
        mock_inspect.return_value = mock_inspector

        mock_op = MagicMock()
        original_op = migration_006.op
        migration_006.op = mock_op

        try:
            migration_006._crear_indices(mock_inspector)
        finally:
            migration_006.op = original_op

        # Verificar que se creó el índice
        mock_op.create_index.assert_called_once()
        args, kwargs = mock_op.create_index.call_args
        assert args[0] == 'idx_historial_potreros_potrero'
        assert args[1] == 'historial_potreros'
        assert args[2] == ['id_potrero']

    def test_upgrade_uses_tenant_constant(self):
        """Test que upgrade() usa la constante TENANT_ID_FK."""
        # Mock del inspector y op
        with patch('sqlalchemy.inspect') as mock_inspect, \
             patch.object(migration_006, 'op') as mock_op:

            mock_inspector = MagicMock()
            # Hacer que las tablas existan pero les falten las columnas tenant_id
            mock_inspector.get_table_names.return_value = [
                'personas', 'potrero', 'ganado', 'vacunacion', 'qr', 'usuarios', 'roles'
            ]
            mock_inspector.get_columns.return_value = [{'name': 'id'}, {'name': 'nombre'}]  # tenant_id no existe
            mock_inspector.get_indexes.return_value = []
            mock_inspector.get_unique_constraints.return_value = []
            mock_inspector.get_foreign_keys.return_value = []
            mock_inspect.return_value = mock_inspector

            mock_op.create_table = MagicMock()
            mock_op.add_column = MagicMock()
            mock_op.execute = MagicMock()
            mock_op.create_index = MagicMock()
            mock_op.create_unique_constraint = MagicMock()
            mock_op.create_foreign_key = MagicMock()
            mock_op.drop_column = MagicMock()

            migration_006.upgrade()

            # Verificar que se usó la constante TENANT_ID_FK en las llamadas
            all_add_column_calls = str(mock_op.add_column.call_args_list)
            assert migration_006.TENANT_ID_FK in all_add_column_calls

    @patch('sqlalchemy.inspect')
    def test_downgrade_removes_indices_and_constraints(self, mock_inspect):
        """Test que downgrade() elimina índices y constraints."""
        mock_inspector = MagicMock()
        mock_inspector.get_table_names.return_value = ['historial_potreros']
        mock_inspect.return_value = mock_inspector

        mock_op = MagicMock()
        original_op = migration_006.op
        migration_006.op = mock_op

        try:
            migration_006.downgrade()
        finally:
            migration_006.op = original_op

        # Verificar que se intentó eliminar el índice
        mock_op.drop_index.assert_called_once_with('idx_historial_potreros_potrero', 'historial_potreros')

        # Verificar que se intentó eliminar constraints únicos
        drop_constraint_calls = mock_op.drop_constraint.call_args_list
        constraint_names = [call[0][0] for call in drop_constraint_calls]
        assert 'uq_personas_email' in constraint_names
        assert 'uq_personas_telefono' in constraint_names