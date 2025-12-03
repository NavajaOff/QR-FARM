import pytest
from unittest.mock import Mock, patch
from src.services.animal_service import GanadoService
from src.models.animal import Ganado, EstadoGanado, SexoGanado


class TestGanadoService:
    def test_mapear_estado_a_id_saludable(self):
        """Test mapping EstadoGanado.SALUDABLE to ID"""
        result = GanadoService._mapear_estado_a_id(EstadoGanado.SALUDABLE)
        assert result == 1

    def test_mapear_estado_a_id_revision(self):
        """Test mapping EstadoGanado.REVISION to ID"""
        result = GanadoService._mapear_estado_a_id(EstadoGanado.REVISION)
        assert result == 2

    def test_mapear_estado_a_id_enfermo(self):
        """Test mapping EstadoGanado.ENFERMO to ID"""
        result = GanadoService._mapear_estado_a_id(EstadoGanado.ENFERMO)
        assert result == 3

    def test_mapear_estado_a_id_default(self):
        """Test mapping unknown estado returns default"""
        # Create a mock estado not in mapping
        mock_estado = Mock()
        result = GanadoService._mapear_estado_a_id(mock_estado)
        assert result == 1

    def test_convertir_fecha_nacimiento_datetime(self):
        """Test converting datetime to isoformat"""
        from datetime import datetime
        dt = datetime(2023, 1, 1, 10, 0, 0)
        result = GanadoService._convertir_fecha_nacimiento(dt)
        assert result == '2023-01-01T10:00:00'

    def test_convertir_fecha_nacimiento_string(self):
        """Test converting string fecha"""
        fecha_str = '2023-01-01'
        result = GanadoService._convertir_fecha_nacimiento(fecha_str)
        assert result == '2023-01-01'

    def test_convertir_fecha_nacimiento_none(self):
        """Test converting None fecha"""
        result = GanadoService._convertir_fecha_nacimiento(None)
        assert result is None

    @patch('src.services.animal_service.get_connection')
    def test_obtener_estados_ganado_success(self, mock_get_connection):
        """Test obtener_estados_ganado with successful database call"""
        # Mock the connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock the fetchall result
        mock_cursor.fetchall.return_value = [
            {'id': 1, 'tipo_estado': 'activo'},
            {'id': 2, 'tipo_estado': 'saludable'}
        ]

        result = GanadoService.obtener_estados_ganado()

        # Verify the result
        assert len(result) == 2
        assert result[0]['id'] == 1
        assert result[0]['estado'] == 'activo'
        assert result[0]['nombre_estado'] == 'activo'

        # Verify database calls
        mock_get_connection.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with("SELECT id, tipo_estado FROM estado_ganado ORDER BY tipo_estado")
        mock_conn.close.assert_called_once()

    @patch('src.services.animal_service.get_connection')
    def test_obtener_estados_ganado_connection_none(self, mock_get_connection):
        """Test obtener_estados_ganado when connection is None"""
        mock_get_connection.return_value = None

        result = GanadoService.obtener_estados_ganado()

        assert result == []

    @patch('src.services.animal_service.get_connection')
    def test_obtener_estados_ganado_exception(self, mock_get_connection):
        """Test obtener_estados_ganado with database exception"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.side_effect = Exception("Database error")

        result = GanadoService.obtener_estados_ganado()

        assert result == []
        mock_conn.close.assert_called_once()

    @patch('src.services.animal_service.get_connection')
    def test_obtener_estados_ganado_solo_activos(self, mock_get_connection):
        """Test obtener_estados_ganado with solo_activos=True"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            {'id': 1, 'tipo_estado': 'saludable'},
            {'id': 2, 'tipo_estado': 'revision'},
            {'id': 3, 'tipo_estado': 'enfermo'}
        ]

        result = GanadoService.obtener_estados_ganado(solo_activos=True)

        assert len(result) == 3
        assert result[0]['estado'] == 'saludable'
        mock_cursor.execute.assert_called_once_with("SELECT id, tipo_estado FROM estado_ganado WHERE id BETWEEN 1 AND 3 ORDER BY tipo_estado")

    @patch('src.services.animal_service.get_connection')
    def test_obtener_estados_ganado_solo_bajas(self, mock_get_connection):
        """Test obtener_estados_ganado with solo_bajas=True"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            {'id': 4, 'tipo_estado': 'dado_de_baja'},
            {'id': 5, 'tipo_estado': 'muerte'},
            {'id': 6, 'tipo_estado': 'venta'}
        ]

        result = GanadoService.obtener_estados_ganado(solo_bajas=True)

        assert len(result) == 3
        assert result[0]['estado'] == 'dado_de_baja'
        mock_cursor.execute.assert_called_once_with("SELECT id, tipo_estado FROM estado_ganado WHERE id BETWEEN 4 AND 8 ORDER BY tipo_estado")

    @patch('src.services.animal_service.get_connection')
    def test_obtener_estados_ganado_ambos_parametros_true(self, mock_get_connection):
        """Test obtener_estados_ganado with both solo_activos and solo_bajas True (should prioritize solo_activos)"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            {'id': 1, 'tipo_estado': 'saludable'},
            {'id': 2, 'tipo_estado': 'revision'}
        ]

        result = GanadoService.obtener_estados_ganado(solo_activos=True, solo_bajas=True)

        # Should prioritize solo_activos when both are True
        mock_cursor.execute.assert_called_once_with("SELECT id, tipo_estado FROM estado_ganado WHERE id BETWEEN 1 AND 3 ORDER BY tipo_estado")


class TestGanadoModel:
    def test_ganado_init_with_id_estado(self):
        """Test Ganado model initialization with id_estado"""
        data = {
            'id': 1,
            'nombre': 'Test Animal',
            'id_estado': 2,
            'estado': 'revision'
        }
        ganado = Ganado(**data)

        assert ganado.id == 1
        assert ganado.nombre == 'Test Animal'
        assert ganado.id_estado == 2
        assert ganado.estado == 'revision'

    def test_ganado_from_dict_with_id_estado(self):
        """Test Ganado.from_dict with id_estado"""
        data = {
            'id': 1,
            'nombre': 'Test Animal',
            'id_estado': 3,
            'estado': 'enfermo',
            'sexo': 'macho'
        }
        ganado = Ganado.from_dict(data)

        assert ganado.id == 1
        assert ganado.nombre == 'Test Animal'
        assert ganado.id_estado == 3
        assert ganado.estado == 'enfermo'
        assert ganado.sexo == SexoGanado.MACHO

    def test_ganado_to_dict_includes_id_estado(self):
        """Test Ganado.to_dict includes id_estado"""
        ganado = Ganado(id=1, nombre='Test', id_estado=2, estado='revision')
        result = ganado.to_dict()

        assert result['id'] == 1
        assert result['nombre'] == 'Test'
        assert result['id_estado'] == 2
        assert result['estado'] == 'revision'

    def test_ganado_es_estado_baja_true(self):
        """Test es_estado_baja returns True for id_estado >= 4"""
        assert Ganado.es_estado_baja(4) is True
        assert Ganado.es_estado_baja(5) is True
        assert Ganado.es_estado_baja(8) is True

    def test_ganado_es_estado_baja_false(self):
        """Test es_estado_baja returns False for id_estado < 4"""
        assert Ganado.es_estado_baja(1) is False
        assert Ganado.es_estado_baja(2) is False
        assert Ganado.es_estado_baja(3) is False
        assert Ganado.es_estado_baja(None) is False

    def test_ganado_es_estado_activo_true(self):
        """Test es_estado_activo returns True for id_estado 1-3"""
        assert Ganado.es_estado_activo(1) is True
        assert Ganado.es_estado_activo(2) is True
        assert Ganado.es_estado_activo(3) is True

    def test_ganado_es_estado_activo_false(self):
        """Test es_estado_activo returns False for id_estado >= 4"""
        assert Ganado.es_estado_activo(4) is False
        assert Ganado.es_estado_activo(5) is False
    @patch('src.services.animal_service.get_connection')
    @patch('src.services.animal_service.PotreroService.verificar_capacidad_disponible')
    @patch('src.services.animal_service.PotreroService.sincronizar_ocupacion')
    @patch('src.services.animal_service.GanadoService._obtener_tenant_id')
    @patch('src.services.animal_service.GanadoService._obtener_estado_id_desde_db')
    def test_crear_ganado_success(self, mock_obtener_estado, mock_tenant, mock_sync, mock_verify, mock_get_conn):
        """Test crear_ganado with successful creation"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.lastrowid = 123
        mock_tenant.return_value = 1
        mock_obtener_estado.return_value = None  # Will use mapping
        mock_verify.return_value = None
        mock_sync.return_value = None

        ganado = Ganado(
            nombre="Test Animal",
            raza="Holstein",
            fecha_nacimiento="2023-01-01",
            sexo=SexoGanado.HEMBRA,
            peso=450.0,
            estado="saludable",
            id_potrero=1,
            id_persona=1
        )

        result = GanadoService.crear_ganado(ganado)

        assert result is not None
        assert result.id == 123
        assert result.nombre == "Test Animal"
        mock_get_conn.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
        mock_verify.assert_called_once_with(1)
        mock_sync.assert_called_once_with(1)
        mock_conn.close.assert_called_once()

    @patch('src.services.animal_service.get_connection')
    @patch('src.services.animal_service.GanadoService._obtener_tenant_id')
    def test_crear_ganado_tenant_none(self, mock_tenant, mock_get_conn):
        """Test crear_ganado when tenant is None"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_tenant.return_value = None

        ganado = Ganado(nombre="Test", estado="saludable", sexo=SexoGanado.HEMBRA)

        result = GanadoService.crear_ganado(ganado)

        assert result is None
        mock_conn.close.assert_called_once()

    @patch('src.services.animal_service.get_connection')
    @patch('src.services.animal_service.GanadoService._obtener_tenant_id')
    def test_obtener_ganado_success(self, mock_tenant, mock_get_conn):
        """Test obtener_ganado with successful retrieval"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_tenant.return_value = 1

        mock_cursor.fetchone.return_value = {
            'id': 1,
            'nombre': 'Test Animal',
            'estado_tipo': 'saludable'
        }

        result = GanadoService.obtener_ganado(1)

        assert result is not None
        assert result.id == 1
        assert result.nombre == 'Test Animal'
        mock_cursor.execute.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('src.services.animal_service.get_connection')
    def test_obtener_ganado_not_found(self, mock_get_conn):
        """Test obtener_ganado when animal not found"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        result = GanadoService.obtener_ganado(999)

        assert result is None
        mock_conn.close.assert_called_once()

    @patch('src.services.animal_service.get_connection')
    def test_obtener_ganado_exception(self, mock_get_conn):
        """Test obtener_ganado with database exception"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        result = GanadoService.obtener_ganado(1)

        assert result is None
        mock_conn.close.assert_called_once()

    @patch('src.services.animal_service.GanadoService.obtener_ganado')
    @patch('src.services.animal_service.GanadoService._obtener_potrero_anterior')
    @patch('src.services.animal_service.GanadoService._verificar_cambio_potrero')
    @patch('src.services.animal_service.GanadoService._actualizar_ganado_en_db')
    @patch('src.services.animal_service.GanadoService._sincronizar_potreros_despues_actualizacion')
    def test_actualizar_ganado_success(self, mock_sync, mock_update_db, mock_verify, mock_potrero_ant, mock_obtener):
        """Test actualizar_ganado with successful update"""
        mock_ganado_existente = Mock()
        mock_obtener.return_value = mock_ganado_existente
        mock_potrero_ant.return_value = 1
        mock_update_db.return_value = True
        mock_verify.return_value = None
        mock_sync.return_value = None

        ganado = Ganado(id=1, nombre="Updated", estado="saludable", sexo=SexoGanado.HEMBRA)

        result = GanadoService.actualizar_ganado(1, ganado)

        assert result is True
        mock_obtener.assert_called_once_with(1, None)
        mock_potrero_ant.assert_called_once_with(1)
        mock_verify.assert_called_once_with(None, 1)
        mock_update_db.assert_called_once_with(1, ganado, None)
        mock_sync.assert_called_once_with(True, None, 1)

    @patch('src.services.animal_service.GanadoService.obtener_ganado')
    def test_actualizar_ganado_not_found(self, mock_obtener):
        """Test actualizar_ganado when animal not found"""
        mock_obtener.return_value = None

        ganado = Ganado(id=1, nombre="Test", estado="saludable", sexo=SexoGanado.HEMBRA)

        result = GanadoService.actualizar_ganado(1, ganado)

        assert result is False
        mock_obtener.assert_called_once_with(1, None)

    @patch('src.services.animal_service.get_connection')
    @patch('src.services.animal_service.GanadoService._obtener_tenant_id')
    def test_crear_ganado_exception(self, mock_tenant, mock_get_conn):
        """Test crear_ganado with database exception"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")
        mock_tenant.return_value = 1

        ganado = Ganado(nombre="Test", estado="saludable", sexo=SexoGanado.HEMBRA)

        result = GanadoService.crear_ganado(ganado)

        assert result is None
        mock_conn.close.assert_called_once()

    def test_ganado_es_estado_activo_none(self):
        """Test es_estado_activo returns True for None (default to active)"""
    def test_obtener_tenant_id(self):
        """Test _obtener_tenant_id"""
        with patch('src.services.animal_service.get_current_tenant_id') as mock_get_tenant:
            mock_get_tenant.return_value = 1
            result = GanadoService._obtener_tenant_id()
            assert result == 1

    def test_obtener_tenant_id_exception(self):
        """Test _obtener_tenant_id with exception"""
        with patch('src.services.animal_service.get_current_tenant_id', side_effect=Exception):
            result = GanadoService._obtener_tenant_id()
            assert result is None

    def test_agregar_filtro_tenant_with_tenant(self):
        """Test _agregar_filtro_tenant with tenant"""
        sql, params = GanadoService._agregar_filtro_tenant("SELECT * FROM table", 1, True)
        assert sql == "SELECT * FROM table WHERE g.tenant_id = %s"
        assert params == (1,)

    def test_agregar_filtro_tenant_without_tenant(self):
        """Test _agregar_filtro_tenant without tenant"""
        sql, params = GanadoService._agregar_filtro_tenant("SELECT * FROM table", None)
        assert sql == "SELECT * FROM table"
        assert params == ()

    def test_to_iso_string_datetime(self):
        """Test _to_iso_string with datetime"""
        from datetime import datetime
        dt = datetime(2023, 1, 1, 10, 0)
        result = GanadoService._to_iso_string(dt)
        assert result == '2023-01-01T10:00:00'

    def test_to_iso_string_date(self):
        """Test _to_iso_string with date"""
        from datetime import date
        d = date(2023, 1, 1)
        result = GanadoService._to_iso_string(d)
        assert result == '2023-01-01'

    def test_to_iso_string_string(self):
        """Test _to_iso_string with string"""
        result = GanadoService._to_iso_string("2023-01-01")
        assert result == "2023-01-01"

    def test_to_iso_string_none(self):
        """Test _to_iso_string with None"""
        result = GanadoService._to_iso_string(None)
        assert result is None

    def test_calcular_edad_datetime(self):
        """Test _calcular_edad with datetime"""
        from datetime import datetime, date
        birth = datetime(2000, 1, 1)
        result = GanadoService._calcular_edad(birth)
        expected = date.today().year - 2000
        assert result == expected

    def test_calcular_edad_string(self):
        """Test _calcular_edad with string"""
        from datetime import date
        result = GanadoService._calcular_edad("2000-01-01")
        expected = date.today().year - 2000
        assert result == expected

    def test_calcular_edad_invalid(self):
        """Test _calcular_edad with invalid input"""
        result = GanadoService._calcular_edad("invalid")
        assert result is None
        assert Ganado.es_estado_activo(None) is True

    def test_calcular_edad_date(self):
        """Test _calcular_edad with date object"""
        from datetime import date
        birth = date(2000, 1, 1)
        result = GanadoService._calcular_edad(birth)
        expected = date.today().year - 2000
        assert result == expected

    def test_calcular_edad_string_with_z(self):
        """Test _calcular_edad with ISO string containing Z"""
        from datetime import date
        result = GanadoService._calcular_edad("2000-01-01T00:00:00Z")
        expected = date.today().year - 2000
        assert result == expected

    def test_calcular_edad_negative_age(self):
        """Test _calcular_edad returns None for future dates"""
        from datetime import date, timedelta
        future_date = date.today() + timedelta(days=365)
        result = GanadoService._calcular_edad(future_date)
        assert result is None

    def test_calcular_edad_other_type(self):
        """Test _calcular_edad with unsupported type"""
        result = GanadoService._calcular_edad(12345)
        assert result is None

    def test_to_nullable_int_valid(self):
        """Test _to_nullable_int with valid values"""
        assert GanadoService._to_nullable_int(5) == 5
        assert GanadoService._to_nullable_int("10") == 10
        assert GanadoService._to_nullable_int(0) == 0

    def test_to_nullable_int_none(self):
        """Test _to_nullable_int with None"""
        assert GanadoService._to_nullable_int(None) is None

    def test_to_nullable_int_invalid(self):
        """Test _to_nullable_int with invalid values"""
        assert GanadoService._to_nullable_int("invalid") is None
        assert GanadoService._to_nullable_int({}) is None

    def test_to_nullable_float_valid(self):
        """Test _to_nullable_float with valid values"""
        assert GanadoService._to_nullable_float(5.5) == 5.5
        assert GanadoService._to_nullable_float("10.5") == 10.5
        assert GanadoService._to_nullable_float(0.0) == 0.0

    def test_to_nullable_float_none(self):
        """Test _to_nullable_float with None"""
        assert GanadoService._to_nullable_float(None) is None

    def test_to_nullable_float_invalid(self):
        """Test _to_nullable_float with invalid values"""
        assert GanadoService._to_nullable_float("invalid") is None
        assert GanadoService._to_nullable_float({}) is None

    def test_empty_propietario(self):
        """Test _empty_propietario returns empty dict"""
        result = GanadoService._empty_propietario()
        assert result == {
            "nombre": None,
            "telefono": None,
            "rol": None
        }

    def test_empty_potrero(self):
        """Test _empty_potrero returns empty dict"""
        result = GanadoService._empty_potrero()
        assert result == {
            "nombre": None,
            "tipo_pasto": None,
            "ultima_limpieza": None,
            "fecha_ultimo_uso": None,
            "proxima_limpieza": None,
            "capacidad": None,
            "estado": None
        }

    @patch('src.services.animal_service.get_connection')
    def test_fetch_vacunas_success(self, mock_get_connection):
        """Test _fetch_vacunas with successful fetch"""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'nombre_vacuna': 'Vacuna A',
                'fecha_aplicacion': '2024-01-01',
                'proxima_dosis': '2024-07-01',
                'estado': 'aplicado',
                'responsable_nombre': 'Juan Perez',
                'responsable': 1
            }
        ]

        result = GanadoService._fetch_vacunas(mock_conn, 1)

        assert len(result) == 1
        assert result[0]['id'] == 1
        assert result[0]['nombre'] == 'Vacuna A'
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()

    @patch('src.services.animal_service.get_connection')
    def test_fetch_vacunas_exception(self, mock_get_connection):
        """Test _fetch_vacunas with exception"""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        result = GanadoService._fetch_vacunas(mock_conn, 1)

        assert result == []
        mock_cursor.close.assert_called_once()

    @patch('src.services.animal_service.get_connection')
    def test_fetch_vacunas_no_responsable_nombre(self, mock_get_connection):
        """Test _fetch_vacunas when responsable_nombre is None"""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'nombre_vacuna': 'Vacuna A',
                'fecha_aplicacion': None,
                'proxima_dosis': None,
                'estado': 'aplicado',
                'responsable_nombre': None,
                'responsable': 1
            }
        ]

        result = GanadoService._fetch_vacunas(mock_conn, 1)

        assert len(result) == 1
        assert result[0]['responsable'] == 1  # Should use responsable ID

    @patch('src.services.animal_service.get_connection')
    @patch('src.services.animal_service.GanadoService._obtener_tenant_id')
    def test_buscar_por_potrero_success(self, mock_tenant, mock_get_connection):
        """Test buscar_por_potrero with successful search"""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            {'id': 1, 'nombre': 'Animal 1', 'id_potrero': 1}
        ]

        with patch.object(Ganado, 'from_dict') as mock_from_dict:
            mock_ganado = Mock()
            mock_from_dict.return_value = mock_ganado

            result = GanadoService.buscar_por_potrero(1)

            assert len(result) == 1
            mock_cursor.execute.assert_called_once()
            mock_conn.close.assert_called_once()

    @patch('src.services.animal_service.get_connection')
    def test_buscar_por_potrero_exception(self, mock_get_connection):
        """Test buscar_por_potrero with exception"""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        result = GanadoService.buscar_por_potrero(1)

        assert result == []
        mock_conn.close.assert_called_once()

    @patch('src.services.animal_service.get_connection')
    @patch('src.services.animal_service.PotreroService.sincronizar_ocupacion')
    @patch('src.services.animal_service.GanadoService._obtener_tenant_id')
    def test_dar_baja_ganado_success(self, mock_tenant, mock_sync, mock_get_connection):
        """Test dar_baja_ganado with successful operation"""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_tenant.return_value = 1

        mock_cursor.fetchone.side_effect = [
            {'id_estado': 1, 'id_potrero': 1, 'tenant_id': 1},
            None  # Second fetchone for validation
        ]

        result = GanadoService.dar_baja_ganado(1, 'muerte', 'Test observaciones')

        assert result is True
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called_once()
        assert mock_conn.close.call_count >= 1

    @patch('src.services.animal_service.get_connection')
    @patch('src.services.animal_service.GanadoService._obtener_tenant_id')
    def test_dar_baja_ganado_not_found(self, mock_tenant, mock_get_connection):
        """Test dar_baja_ganado when animal not found"""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_tenant.return_value = 1

        mock_cursor.fetchone.return_value = None

        result = GanadoService.dar_baja_ganado(1, 'muerte')

        assert result == "Animal no encontrado"
        assert mock_conn.close.call_count >= 1

    @patch('src.services.animal_service.get_connection')
    @patch('src.services.animal_service.GanadoService._obtener_tenant_id')
    def test_dar_baja_ganado_already_baja(self, mock_tenant, mock_get_connection):
        """Test dar_baja_ganado when animal already has baja status"""
        mock_conn = Mock()
        mock_cursor = Mock(dictionary=True)
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_tenant.return_value = 1

        mock_cursor.fetchone.return_value = {'id_estado': 5, 'id_potrero': None, 'tenant_id': 1}

        result = GanadoService.dar_baja_ganado(1, 'muerte')

        assert result == "El animal ya está dado de baja"
        assert mock_conn.close.call_count >= 1

    @patch('src.services.animal_service.GanadoService.dar_baja_ganado')
    def test_eliminar_ganado_success(self, mock_dar_baja):
        """Test eliminar_ganado with successful operation"""
        mock_dar_baja.return_value = True

        result = GanadoService.eliminar_ganado(1)

        assert result is True
        mock_dar_baja.assert_called_once_with(1, 'otra', 'Eliminación automática', tenant_id_override=None)

    @patch('src.services.animal_service.GanadoService.dar_baja_ganado')
    def test_eliminar_ganado_not_found(self, mock_dar_baja):
        """Test eliminar_ganado when animal not found"""
        mock_dar_baja.return_value = "Animal no encontrado"

        result = GanadoService.eliminar_ganado(1)

        assert result is False

    def test_mapear_estado_string_a_id(self):
        """Test _mapear_estado_string_a_id with valid states"""
        assert GanadoService._mapear_estado_string_a_id('saludable') == 1
        assert GanadoService._mapear_estado_string_a_id('revision') == 2
        assert GanadoService._mapear_estado_string_a_id('enfermo') == 3

    def test_mapear_estado_string_a_id_case_insensitive(self):
        """Test _mapear_estado_string_a_id is case insensitive"""
        assert GanadoService._mapear_estado_string_a_id('SALUDABLE') == 1
        assert GanadoService._mapear_estado_string_a_id('Revision') == 2

    def test_mapear_estado_string_a_id_default(self):
        """Test _mapear_estado_string_a_id returns default for unknown"""
        assert GanadoService._mapear_estado_string_a_id('unknown') == 1

    @patch('src.services.animal_service.get_connection')
    def test_obtener_estado_id_desde_db_success(self, mock_get_connection):
        """Test _obtener_estado_id_desde_db with successful fetch"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = (2,)

        result = GanadoService._obtener_estado_id_desde_db('revision')

        assert result == 2
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('src.services.animal_service.get_connection')
    def test_obtener_estado_id_desde_db_not_found(self, mock_get_connection):
        """Test _obtener_estado_id_desde_db when not found"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchone.return_value = None

        result = GanadoService._obtener_estado_id_desde_db('unknown')

        assert result is None

    @patch('src.services.animal_service.get_connection')
    def test_obtener_estado_id_desde_db_exception(self, mock_get_connection):
        """Test _obtener_estado_id_desde_db with exception"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_get_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("DB Error")

        result = GanadoService._obtener_estado_id_desde_db('test')

        assert result is None

    def test_obtener_id_estado_por_causa(self):
        """Test _obtener_id_estado_por_causa with valid causes"""
        assert GanadoService._obtener_id_estado_por_causa('muerte') == 5
        assert GanadoService._obtener_id_estado_por_causa('venta') == 6
        assert GanadoService._obtener_id_estado_por_causa('robo') == 7
        assert GanadoService._obtener_id_estado_por_causa('otra') == 8
        assert GanadoService._obtener_id_estado_por_causa('dado_de_baja') == 4

    def test_obtener_id_estado_por_causa_default(self):
        """Test _obtener_id_estado_por_causa returns default for unknown"""
        assert GanadoService._obtener_id_estado_por_causa('unknown') == 8

    def test_obtener_id_estado_por_causa_case_insensitive(self):
        """Test _obtener_id_estado_por_causa is case insensitive"""
        assert GanadoService._obtener_id_estado_por_causa('MUERTE') == 5
        assert GanadoService._obtener_id_estado_por_causa('Venta') == 6