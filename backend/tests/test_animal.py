import pytest
from datetime import date, datetime
from src.models.animal import Ganado, EstadoGanado, SexoGanado

# Constants for test data
TEST_DATETIME_STR = '2023-01-01T10:00:00'


class TestGanado:
    def test_init_default_values(self):
        """Test initialization with default values"""
        ganado = Ganado()
        assert ganado.nombre == ""
        assert ganado.sexo == SexoGanado.MACHO
        assert ganado.estado == EstadoGanado.SALUDABLE
        assert ganado.id is None
        assert ganado.peso is None

    def test_init_with_kwargs(self):
        """Test initialization with keyword arguments"""
        data = {
            'id': 1,
            'codigo_qr': 'QR123',
            'id_potrero': 2,
            'id_persona': 3,
            'nombre': 'Vaca1',
            'raza': 'Holstein',
            'fecha_nacimiento': date(2020, 1, 1),
            'edad': 4,
            'sexo': 'hembra',
            'peso': 450.5,
            'estado': 'saludable',
            'estado_salud': 'buena',
            'estado_tipo': 'activo',
            'created_at': TEST_DATETIME_STR,
            'updated_at': datetime(2023, 1, 2)
        }
        ganado = Ganado(**data)
        assert ganado.id == 1
        assert ganado.nombre == 'Vaca1'
        assert ganado.sexo == SexoGanado.HEMBRA
        assert ganado.estado == EstadoGanado.SALUDABLE
        assert ganado.peso == 450.5

    def test_from_dict_basic(self):
        """Test from_dict with basic data"""
        data = {
            'id': 1,
            'codigo_qr': 'QR123',
            'nombre': 'Vaca1',
            'raza': 'Holstein',
            'sexo': 'hembra',
            'peso': '450.5',
            'estado': 'saludable'
        }
        ganado = Ganado.from_dict(data)
        assert ganado.id == 1
        assert ganado.nombre == 'Vaca1'
        assert ganado.sexo == SexoGanado.HEMBRA
        assert ganado.peso == 450.5
        assert ganado.estado == EstadoGanado.SALUDABLE

    def test_from_dict_with_dates(self):
        """Test from_dict with date fields"""
        data = {
            'fecha_nacimiento': '2020-01-01',
            'created_at': TEST_DATETIME_STR,
            'updated_at': '2023-01-02T11:00:00'
        }
        ganado = Ganado.from_dict(data)
        assert ganado.fecha_nacimiento == '2020-01-01'
        assert ganado.created_at == TEST_DATETIME_STR

    def test_to_dict_basic(self):
        """Test to_dict conversion"""
        ganado = Ganado(
            id=1,
            codigo_qr='QR123',
            nombre='Vaca1',
            sexo=SexoGanado.HEMBRA,
            estado=EstadoGanado.SALUDABLE,
            peso=450.5
        )
        result = ganado.to_dict()
        assert result['id'] == 1
        assert result['codigo_qr'] == 'QR123'
        assert result['nombre'] == 'Vaca1'
        assert result['sexo'] == 'hembra'
        assert result['estado'] == 'saludable'
        assert result['peso'] == 450.5

    def test_to_dict_with_datetime(self):
        """Test to_dict with datetime objects"""
        dt = datetime(2023, 1, 1, 10, 0, 0)
        ganado = Ganado(fecha_nacimiento=dt, created_at=dt)
        result = ganado.to_dict()
        assert result['fecha_nacimiento'] == TEST_DATETIME_STR
        assert result['created_at'] == TEST_DATETIME_STR

    def test_enum_values(self):
        """Test enum value access"""
        assert EstadoGanado.SALUDABLE.value == 'saludable'
        assert SexoGanado.MACHO.value == 'macho'
        assert SexoGanado.HEMBRA.value == 'hembra'

    def test_from_dict_enum_conversion(self):
        """Test enum conversion in from_dict"""
        data = {'estado': 'revision', 'sexo': 'hembra'}
        ganado = Ganado.from_dict(data)
        assert ganado.estado == EstadoGanado.REVISION
        assert ganado.sexo == SexoGanado.HEMBRA

    def test_from_dict_default_enum(self):
        """Test default enum values in from_dict"""
        data = {}
        ganado = Ganado.from_dict(data)
        assert ganado.estado == EstadoGanado.SALUDABLE
        assert ganado.sexo == SexoGanado.MACHO