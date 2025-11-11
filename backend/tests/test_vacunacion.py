import pytest
from datetime import datetime
from src.models.vacunacion import Vacunacion, EstadoVacunacion

# Constants for test data
TEST_VACUNA_NAME = 'Vacuna A'
TEST_DATETIME_STR = '2023-01-01T10:00:00'


class TestVacunacion:
    def test_init_default_values(self):
        """Test initialization with default values"""
        vacunacion = Vacunacion()
        assert vacunacion.estado == EstadoVacunacion.pendiente
        assert vacunacion.id is None
        assert vacunacion.id_animal is None

    def test_init_with_params(self):
        """Test initialization with parameters"""
        dt = datetime(2023, 1, 1, 10, 0, 0)
        vacunacion = Vacunacion(
            id=1,
            id_animal=10,
            nombre_animal='Vaca1',
            fecha_aplicacion=dt,
            proxima_dosis=dt,
            responsable=5,
            estado=EstadoVacunacion.aplicado,
            id_tipo_vacuna=2,
            nombre_tipo_vacuna=TEST_VACUNA_NAME,
            nombre_responsable='Dr. Juan'
        )
        assert vacunacion.id == 1
        assert vacunacion.id_animal == 10
        assert vacunacion.nombre_animal == 'Vaca1'
        assert vacunacion.fecha_aplicacion == dt
        assert vacunacion.estado == EstadoVacunacion.aplicado

    def test_from_dict_basic(self):
        """Test from_dict with basic data"""
        data = {
            'id': 1,
            'id_animal': 10,
            'nombre_animal': 'Vaca1',
            'estado': 'aplicado',
            'id_tipo_vacuna': 2,
            'nombre_tipo_vacuna': TEST_VACUNA_NAME
        }
        vacunacion = Vacunacion.from_dict(data)
        assert vacunacion.id == 1
        assert vacunacion.id_animal == 10
        assert vacunacion.estado == EstadoVacunacion.aplicado

    def test_from_dict_with_dates(self):
        """Test from_dict with date fields"""
        data = {
            'fecha_aplicacion': TEST_DATETIME_STR,
            'proxima_dosis': '2023-02-01T10:00:00'
        }
        vacunacion = Vacunacion.from_dict(data)
        assert vacunacion.fecha_aplicacion == TEST_DATETIME_STR
        assert vacunacion.proxima_dosis == '2023-02-01T10:00:00'

    def test_from_dict_default_estado(self):
        """Test from_dict with default estado"""
        data = {}
        vacunacion = Vacunacion.from_dict(data)
        assert vacunacion.estado == EstadoVacunacion.pendiente

    def test_to_dict_basic(self):
        """Test to_dict conversion"""
        dt = datetime(2023, 1, 1, 10, 0, 0)
        vacunacion = Vacunacion(
            id=1,
            id_animal=10,
            nombre_animal='Vaca1',
            fecha_aplicacion=dt,
            estado=EstadoVacunacion.aplicado,
            id_tipo_vacuna=2,
            nombre_tipo_vacuna=TEST_VACUNA_NAME
        )
        result = vacunacion.to_dict()
        assert result['id'] == 1
        assert result['id_animal'] == 10
        assert result['nombre_animal'] == 'Vaca1'
        assert result['fecha_aplicacion'] == TEST_DATETIME_STR
        assert result['estado'] == 'aplicado'
        assert result['id_tipo_vacuna'] == 2
        assert result['nombre_tipo_vacuna'] == TEST_VACUNA_NAME

    def test_to_dict_none_dates(self):
        """Test to_dict with None dates"""
        vacunacion = Vacunacion()
        result = vacunacion.to_dict()
        assert result['fecha_aplicacion'] is None
        assert result['proxima_dosis'] is None

    def test_to_dict_string_dates(self):
        """Test to_dict with string dates"""
        vacunacion = Vacunacion(
            fecha_aplicacion='2023-01-01',
            proxima_dosis='2023-02-01'
        )
        result = vacunacion.to_dict()
        assert result['fecha_aplicacion'] == '2023-01-01'
        assert result['proxima_dosis'] == '2023-02-01'

    def test_estado_enum_values(self):
        """Test EstadoVacunacion enum values"""
        assert EstadoVacunacion.aplicado.value == 'aplicado'
        assert EstadoVacunacion.pendiente.value == 'pendiente'

    def test_enum_conversion_in_from_dict(self):
        """Test enum conversion in from_dict"""
        data = {'estado': 'aplicado'}
        vacunacion = Vacunacion.from_dict(data)
        assert vacunacion.estado == EstadoVacunacion.aplicado

    def test_to_dict_enum_handling(self):
        """Test enum handling in to_dict"""
        # Test with enum
        vacunacion = Vacunacion(estado=EstadoVacunacion.aplicado)
        result = vacunacion.to_dict()
        assert result['estado'] == 'aplicado'

        # Test with string (fallback)
        vacunacion.estado = 'pendiente'
        result = vacunacion.to_dict()
        assert result['estado'] == 'pendiente'