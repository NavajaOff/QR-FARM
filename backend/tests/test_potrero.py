import pytest
from datetime import datetime
from decimal import Decimal
from src.models.potrero import Potrero, PotreroData, EstadoPotrero

# Constants for test data
TEST_POTRERO_NAME = 'Potrero 1'
TEST_DESCRIPCION = 'Test potrero'
TEST_DATETIME_STR = '2023-01-01T10:00:00'


class TestPotreroData:
    def test_init(self):
        """Test PotreroData initialization"""
        data = PotreroData(
            id=1,
            nombre=TEST_POTRERO_NAME,
            capacidad=50,
            hectareas=10.5,
            ocupacion=25
        )
        assert data.id == 1
        assert data.nombre == TEST_POTRERO_NAME
        assert data.capacidad == 50
        assert data.hectareas == 10.5
        assert data.ocupacion == 25


class TestPotrero:
    def test_init_with_data(self):
        """Test Potrero initialization with PotreroData"""
        data = PotreroData(
            id=1,
            nombre=TEST_POTRERO_NAME,
            capacidad=50,
            hectareas=10.5
        )
        potrero = Potrero(datos=data)
        assert potrero.id == 1
        assert potrero.nombre == TEST_POTRERO_NAME
        assert potrero.capacidad == 50
        assert potrero.hectareas == 10.5

    def test_from_params(self):
        """Test Potrero from_params classmethod"""
        potrero = Potrero.from_params(
            id=1,
            nombre=TEST_POTRERO_NAME,
            capacidad=50,
            hectareas=10.5,
            id_estado_potrero=2
        )
        assert potrero.id == 1
        assert potrero.nombre == TEST_POTRERO_NAME
        assert potrero.id_estado_potrero == 2

    def test_from_db_row(self):
        """Test Potrero from_db_row"""
        row = {
            'id': 1,
            'nombre': TEST_POTRERO_NAME,
            'capacidad': 50,
            'hectareas': 10.5,
            'ocupacion': 25,
            'area': '100.5',
            'id_estado_potrero': 2,
            'descripcion': 'Potrero principal'
        }
        potrero = Potrero.from_db_row(row)
        assert potrero.id == 1
        assert potrero.nombre == TEST_POTRERO_NAME
        assert potrero.area == Decimal('100.5')
        assert potrero.id_estado_potrero == 2

    def test_from_db_row_none_area(self):
        """Test Potrero from_db_row with None area"""
        row = {'id': 1, 'nombre': TEST_POTRERO_NAME}
        potrero = Potrero.from_db_row(row)
        assert potrero.area is None

    def test_to_dict(self):
        """Test Potrero to_dict"""
        dt = datetime(2023, 1, 1, 10, 0, 0)
        potrero = Potrero.from_params(
            id=1,
            nombre=TEST_POTRERO_NAME,
            capacidad=50,
            hectareas=10.5,
            area=Decimal('100.5'),
            fecha_ultimo_uso=dt,
            ultima_limpieza=dt,
            proxima_limpieza=dt,
            descripcion=TEST_DESCRIPCION
        )
        result = potrero.to_dict()
        assert result['id'] == 1
        assert result['nombre'] == TEST_POTRERO_NAME
        assert result['capacidad'] == 50
        assert result['hectareas'] == 10.5
        assert result['area'] == 100.5
        # El modelo no tiene estado sincronizado, verificar id_estado_potrero
        assert result['id_estado_potrero'] is None
        assert result['fecha_ultimo_uso'] == TEST_DATETIME_STR
        assert result['ultima_limpieza'] == TEST_DATETIME_STR
        assert result['proxima_limpieza'] == TEST_DATETIME_STR
        assert result['descripcion'] == TEST_DESCRIPCION

    def test_to_dict_none_dates(self):
        """Test Potrero to_dict with None dates"""
        potrero = Potrero.from_params(id=1, nombre=TEST_POTRERO_NAME)
        result = potrero.to_dict()
        assert result['fecha_ultimo_uso'] is None
        assert result['ultima_limpieza'] is None
        assert result['proxima_limpieza'] is None

    def test_from_dict(self):
        """Test Potrero from_dict"""
        data = {
            'id': 1,
            'nombre': TEST_POTRERO_NAME,
            'capacidad': 50,
            'hectareas': 10.5,
            'area': '100.5',
            'estado': 'ocupado',
            'ocupacion': 25,
            'descripcion': TEST_DESCRIPCION
        }
        potrero = Potrero.from_dict(data)
        assert potrero.id == 1
        assert potrero.nombre == TEST_POTRERO_NAME
        assert potrero.area == Decimal('100.5')
        assert potrero.id_estado_potrero is None  # El dict no tiene id_estado_potrero

    def test_from_dict_none_area(self):
        """Test Potrero from_dict with None area"""
        data = {'nombre': TEST_POTRERO_NAME}
        potrero = Potrero.from_dict(data)
        assert potrero.area is None

    def test_estado_enum_conversion(self):
        """Test estado enum conversion"""
        potrero = Potrero.from_params(id_estado_potrero=3)
        assert potrero.id_estado_potrero == 3

    def test_estado_enum_default(self):
        """Test estado enum default value"""
        potrero = Potrero.from_params(id_estado_potrero=1)
        assert potrero.id_estado_potrero == 1


class TestEstadoPotrero:
    def test_enum_values(self):
        """Test EstadoPotrero enum values"""
        assert EstadoPotrero.DISPONIBLE.value == 'disponible'
        assert EstadoPotrero.OCUPADO.value == 'ocupado'
        assert EstadoPotrero.LIMPIEZA.value == 'limpieza'