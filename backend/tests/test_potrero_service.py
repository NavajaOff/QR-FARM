import pytest
from unittest.mock import Mock, patch
from src.services.potrero_service import PotreroService


class TestPotreroService:
    @patch('src.services.potrero_service.db')
    def test_get_tipos_pasto_success(self, mock_db):
        """Test get_tipos_pasto with successful database call"""
        mock_cursor = Mock()
        mock_db.get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            {'id': 1, 'tipo_pasto': 'Césped'},
            {'id': 2, 'tipo_pasto': 'Pasto alto'}
        ]

        result = PotreroService.get_tipos_pasto()

        assert len(result) == 2
        assert result[0]['tipo_pasto'] == 'Césped'

    @patch('src.services.potrero_service.db')
    def test_get_tipos_pasto_exception(self, mock_db):
        """Test get_tipos_pasto with database exception"""
        mock_cursor = Mock()
        mock_db.get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.side_effect = Exception("DB Error")

        result = PotreroService.get_tipos_pasto()

        assert result == []

    @patch('src.services.potrero_service.db')
    def test_get_estados_potrero_success(self, mock_db):
        """Test get_estados_potrero with successful database call"""
        mock_cursor = Mock()
        mock_db.get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {'COLUMN_TYPE': "enum('disponible','ocupado','limpieza')"}

        result = PotreroService.get_estados_potrero()

        assert len(result) == 3
        assert result[0]['estado'] == 'disponible'
        assert result[0]['id'] == 1

    @patch('src.services.potrero_service.db')
    def test_get_estados_potrero_no_result(self, mock_db):
        """Test get_estados_potrero when no result"""
        mock_cursor = Mock()
        mock_db.get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        result = PotreroService.get_estados_potrero()

        assert result == []

    @patch('src.services.potrero_service.db')
    def test_get_estados_potrero_exception(self, mock_db):
        """Test get_estados_potrero with database exception"""
        mock_cursor = Mock()
        mock_db.get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.side_effect = Exception("DB Error")

        result = PotreroService.get_estados_potrero()

        assert result == []

    @patch('src.services.potrero_service.get_current_tenant_id')
    def test_obtener_tenant_id(self, mock_get_tenant):
        """Test _obtener_tenant_id"""
        mock_get_tenant.return_value = 1
        result = PotreroService._obtener_tenant_id()
        assert result == 1

    @patch('src.services.potrero_service.get_current_tenant_id')
    def test_obtener_tenant_id_exception(self, mock_get_tenant):
        """Test _obtener_tenant_id with exception"""
        mock_get_tenant.side_effect = Exception
        result = PotreroService._obtener_tenant_id()
        assert result is None

    @patch('src.services.potrero_service.db')
    def test_obtener_ocupacion_real(self, mock_db):
        """Test _obtener_ocupacion_real"""
        mock_cursor = Mock()
        mock_db.get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {'total': 5}

        result = PotreroService._obtener_ocupacion_real(1)

        assert result == 5

    @patch('src.services.potrero_service.db')
    def test_obtener_ocupacion_real_exception(self, mock_db):
        """Test _obtener_ocupacion_real with exception"""
        mock_cursor = Mock()
        mock_db.get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.side_effect = Exception

        result = PotreroService._obtener_ocupacion_real(1)

        assert result == 0

    @patch('src.services.potrero_service.get_connection')
    def test_get_all_success(self, mock_get_connection):
        """Test get_all exitoso."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True

        mock_cursor.fetchall.return_value = [
            {'id': 1, 'nombre': 'Potrero 1', 'id_tipo_pasto': 1}
        ]

        with patch('src.services.potrero_service.get_current_tenant_id', return_value=1), \
             patch('src.services.potrero_service.PotreroService._obtener_ocupacion_real', return_value=0), \
             patch('src.services.potrero_service.PotreroService._actualizar_ocupacion_en_db'), \
             patch('src.services.potrero_service.PotreroService.get_tipos_pasto', return_value=[{'id': 1, 'tipo_pasto': 'Césped'}]):
            result = PotreroService.get_all()

            assert isinstance(result, list)

    @patch('src.services.potrero_service.db')
    def test_get_by_id_success(self, mock_db):
        """Test get_by_id exitoso."""
        mock_cursor = Mock()
        mock_db.get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {
            'id': 1,
            'nombre': 'Potrero 1',
            'id_tipo_pasto': 1,
            'ocupacion': 0
        }

        with patch('src.services.potrero_service.get_current_tenant_id', return_value=1), \
             patch('src.services.potrero_service.PotreroService._obtener_ocupacion_real', return_value=0), \
             patch('src.services.potrero_service.PotreroService.get_tipos_pasto', return_value=[{'id': 1, 'tipo_pasto': 'Césped'}]):
            result = PotreroService.get_by_id(1)

            assert result is not None
            assert result['id'] == 1

    @patch('src.services.potrero_service.db')
    def test_get_by_id_not_found(self, mock_db):
        """Test get_by_id cuando no existe."""
        mock_cursor = Mock()
        mock_db.get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        with patch('src.services.potrero_service.get_current_tenant_id', return_value=1):
            with pytest.raises(ValueError):
                PotreroService.get_by_id(999)

    @patch('src.services.potrero_service.get_connection')
    def test_create_success(self, mock_get_connection):
        """Test create exitoso."""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True
        mock_cursor.lastrowid = 1

        with patch('src.services.potrero_service.get_current_tenant_id', return_value=1), \
             patch('src.services.potrero_service.db') as mock_db:
            mock_select_cursor = Mock()
            mock_db.get_cursor.return_value.__enter__.return_value = mock_select_cursor
            mock_select_cursor.fetchone.return_value = {
                'id': 1,
                'nombre': 'Potrero 1',
                'id_tipo_pasto': 1
            }

            data = {
                'nombre': 'Potrero Test',
                'capacidad': 10,
                'id_tipo_pasto': 1
            }

            with patch('src.services.potrero_service.PotreroService._agregar_tipo_pasto'), \
                 patch('src.services.potrero_service.PotreroService._agregar_responsable'):
                result = PotreroService.create(data)

                assert result is not None

    @patch('src.services.potrero_service.db')
    def test_update_success(self, mock_db):
        """Test update exitoso."""
        mock_cursor = Mock()
        mock_db.get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {
            'id': 1,
            'nombre': 'Potrero 1',
            'id_tipo_pasto': 1,
            'ocupacion': 0
        }

        with patch('src.services.potrero_service.get_current_tenant_id', return_value=1), \
             patch('src.services.potrero_service.PotreroService._obtener_ocupacion_real', return_value=0), \
             patch('src.services.potrero_service.PotreroService.get_tipos_pasto', return_value=[{'id': 1, 'tipo_pasto': 'Césped'}]):
            data = {'nombre': 'Potrero Actualizado'}

            with patch('src.services.potrero_service.PotreroService._agregar_tipo_pasto_actualizado'):
                result = PotreroService.update(1, data)

                assert result is not None

    @patch('src.services.potrero_service.db')
    def test_delete_success(self, mock_db):
        """Test delete exitoso."""
        mock_cursor = Mock()
        mock_db.get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {
            'id': 1,
            'nombre': 'Potrero 1',
            'id_tipo_pasto': 1
        }

        with patch('src.services.potrero_service.get_current_tenant_id', return_value=1), \
             patch('src.services.potrero_service.PotreroService._obtener_ocupacion_real', return_value=0), \
             patch('src.services.potrero_service.PotreroService.get_tipos_pasto', return_value=[{'id': 1, 'tipo_pasto': 'Césped'}]):
            result = PotreroService.delete(1)

            assert result is True

    @patch('src.services.potrero_service.db')
    def test_sincronizar_ocupacion(self, mock_db):
        """Test sincronizar_ocupacion."""
        mock_cursor = Mock()
        mock_db.get_cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {'total': 5}

        with patch('src.services.potrero_service.PotreroService._actualizar_ocupacion_en_db') as mock_actualizar, \
             patch('src.services.potrero_service.PotreroService.get_by_id') as mock_get:
            mock_get.return_value = {'id': 1, 'nombre': 'Potrero 1'}
            mock_actualizar.return_value = {'id': 1, 'ocupacion': 5}

            result = PotreroService.sincronizar_ocupacion(1)

            assert result is not None

    @patch('src.services.potrero_service.db')
    def test_verificar_capacidad_disponible(self, mock_db):
        """Test verificar_capacidad_disponible."""
        with patch('src.services.potrero_service.PotreroService.get_by_id') as mock_get, \
             patch('src.services.potrero_service.PotreroService._obtener_ocupacion_real', return_value=5), \
             patch('src.services.potrero_service.PotreroService._actualizar_ocupacion_en_db'):
            mock_get.return_value = {'id': 1, 'nombre': 'Potrero 1', 'capacidad': 10, 'ocupacion': 5}

            result = PotreroService.verificar_capacidad_disponible(1, 3)

            assert result is not None

    @patch('src.services.potrero_service.db')
    def test_verificar_capacidad_disponible_exceeded(self, mock_db):
        """Test verificar_capacidad_disponible cuando se excede capacidad."""
        with patch('src.services.potrero_service.PotreroService.get_by_id') as mock_get, \
             patch('src.services.potrero_service.PotreroService._obtener_ocupacion_real', return_value=8), \
             patch('src.services.potrero_service.PotreroService._actualizar_ocupacion_en_db'):
            mock_get.return_value = {'id': 1, 'nombre': 'Potrero 1', 'capacidad': 10, 'ocupacion': 8}

            with pytest.raises(ValueError):
                PotreroService.verificar_capacidad_disponible(1, 5)

    @patch('src.services.potrero_service.db')
    @patch('src.services.potrero_service.PotreroService._obtener_tenant_id')
    def test_registrar_actividad_potrero_success(self, mock_tenant, mock_db):
        """Test _registrar_actividad_potrero exitoso."""
        from datetime import datetime
        mock_tenant.return_value = 1
        mock_cursor = Mock()
        mock_db.get_cursor.return_value.__enter__.return_value = mock_cursor
        
        PotreroService._registrar_actividad_potrero(
            1, 'uso', datetime(2024, 1, 1), 'Test', 1
        )
        
        assert mock_cursor.execute.called

    @patch('src.services.potrero_service.PotreroService._obtener_tenant_id')
    def test_registrar_actividad_potrero_no_tenant(self, mock_tenant):
        """Test _registrar_actividad_potrero sin tenant."""
        from datetime import datetime
        mock_tenant.return_value = None
        
        with pytest.raises(ValueError, match="Tenant requerido"):
            PotreroService._registrar_actividad_potrero(
                1, 'uso', datetime(2024, 1, 1), 'Test', None
            )

    @patch('src.services.potrero_service.PotreroService._registrar_actividad_potrero')
    @patch('src.services.potrero_service.PotreroService._obtener_tenant_id')
    def test_registrar_actividad_si_existe_with_data(self, mock_tenant, mock_registrar):
        """Test _registrar_actividad_si_existe con datos."""
        from datetime import datetime
        mock_tenant.return_value = 1
        
        data = {'fecha_ultimo_uso': '2024-01-01T10:00:00Z'}
        PotreroService._registrar_actividad_si_existe(
            1, data, 'fecha_ultimo_uso', 'uso', None, 1
        )
        
        assert mock_registrar.called

    @patch('src.services.potrero_service.PotreroService._registrar_actividad_potrero')
    def test_registrar_actividad_si_existe_no_data(self, mock_registrar):
        """Test _registrar_actividad_si_existe sin datos."""
        data = {}
        PotreroService._registrar_actividad_si_existe(
            1, data, 'fecha_ultimo_uso', 'uso', None, 1
        )
        
        assert not mock_registrar.called

    @patch('src.services.potrero_service.PotreroService._registrar_actividad_potrero')
    @patch('src.services.potrero_service.PotreroService._obtener_tenant_id')
    def test_registrar_actividades_potrero_create(self, mock_tenant, mock_registrar):
        """Test _registrar_actividades_potrero_create."""
        from datetime import datetime
        mock_tenant.return_value = 1
        
        data = {
            'fecha_ultimo_uso': '2024-01-01T10:00:00Z',
            'ultima_limpieza': '2024-01-02T10:00:00Z',
            'proxima_limpieza': '2024-01-03T10:00:00Z'
        }
        PotreroService._registrar_actividades_potrero_create(1, data, 1)
        
        assert mock_registrar.call_count == 3

    @patch('src.services.potrero_service.PotreroService._registrar_actividad_potrero')
    @patch('src.services.potrero_service.PotreroService._obtener_tenant_id')
    def test_registrar_actividades_potrero_create_auto_fecha(self, mock_tenant, mock_registrar):
        """Test _registrar_actividades_potrero_create con fecha automática."""
        from datetime import datetime
        mock_tenant.return_value = 1
        
        data = {}  # Sin fecha_ultimo_uso
        PotreroService._registrar_actividades_potrero_create(1, data, 1)
        
        # Debe registrar fecha_ultimo_uso automáticamente
        assert mock_registrar.called

    @patch('src.services.potrero_service.PotreroService._registrar_actividad_potrero')
    @patch('src.services.potrero_service.PotreroService._obtener_tenant_id')
    def test_procesar_actividad_actualizacion(self, mock_tenant, mock_registrar):
        """Test _procesar_actividad_actualizacion."""
        from datetime import datetime
        mock_tenant.return_value = 1
        
        actividades_data = {'fecha_ultimo_uso': '2024-01-01T10:00:00Z'}
        PotreroService._procesar_actividad_actualizacion(
            1, actividades_data, 'fecha_ultimo_uso', 'uso', None, 1
        )
        
        assert mock_registrar.called

    @patch('src.services.potrero_service.PotreroService._registrar_actividad_potrero')
    def test_procesar_actividad_actualizacion_no_data(self, mock_registrar):
        """Test _procesar_actividad_actualizacion sin datos."""
        actividades_data = {}
        PotreroService._procesar_actividad_actualizacion(
            1, actividades_data, 'fecha_ultimo_uso', 'uso', None, 1
        )
        
        assert not mock_registrar.called

    @patch('src.services.potrero_service.PotreroService._obtener_tenant_id')
    def test_actualizar_actividades_potrero_no_tenant(self, mock_tenant):
        """Test _actualizar_actividades_potrero sin tenant."""
        mock_tenant.return_value = None
        
        with pytest.raises(ValueError, match="Tenant requerido"):
            PotreroService._actualizar_actividades_potrero(1, {})