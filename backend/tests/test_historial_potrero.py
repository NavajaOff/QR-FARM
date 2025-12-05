"""Tests para el modelo HistorialPotrero."""
import pytest
from datetime import datetime
from src.models.historial_potrero import HistorialPotrero, TipoEventoPotrero


class TestTipoEventoPotrero:
    """Tests para el enum TipoEventoPotrero."""
    
    def test_tipo_evento_valores(self):
        """Test que los valores del enum sean correctos."""
        assert TipoEventoPotrero.USO.value == 'uso'
        assert TipoEventoPotrero.LIMPIEZA.value == 'limpieza'
        assert TipoEventoPotrero.INSPECCION.value == 'inspeccion'
        assert TipoEventoPotrero.MANTENIMIENTO.value == 'mantenimiento'


class TestHistorialPotrero:
    """Tests para el modelo HistorialPotrero."""
    
    def test_init_basico(self):
        """Test inicialización básica."""
        historial = HistorialPotrero(
            id=1,
            id_potrero=10,
            tipo_evento=TipoEventoPotrero.USO,
            fecha_evento=datetime(2024, 1, 1),
            observaciones='Test',
            tenant_id=1
        )
        assert historial.id == 1
        assert historial.id_potrero == 10
        assert historial.tipo_evento == TipoEventoPotrero.USO
        assert historial.fecha_evento == datetime(2024, 1, 1)
        assert historial.observaciones == 'Test'
        assert historial.tenant_id == 1
    
    def test_init_con_tipo_evento_string(self):
        """Test inicialización con tipo_evento como string."""
        historial = HistorialPotrero(tipo_evento='limpieza')
        assert historial.tipo_evento == TipoEventoPotrero.LIMPIEZA
    
    def test_init_valores_opcionales(self):
        """Test inicialización con valores opcionales."""
        historial = HistorialPotrero()
        assert historial.id is None
        assert historial.id_potrero is None
        assert historial.tipo_evento is None
        assert historial.fecha_evento is None
        assert historial.observaciones is None
        assert historial.tenant_id is None
    
    def test_from_db_row(self):
        """Test creación desde fila de base de datos."""
        row = {
            'id': 1,
            'id_potrero': 10,
            'tipo_evento': 'uso',
            'fecha_evento': datetime(2024, 1, 1),
            'observaciones': 'Test observación',
            'tenant_id': 1,
            'fecha_creacion': datetime(2024, 1, 1),
            'fecha_actualizacion': datetime(2024, 1, 2)
        }
        historial = HistorialPotrero.from_db_row(row)
        assert historial.id == 1
        assert historial.id_potrero == 10
        assert historial.tipo_evento == TipoEventoPotrero.USO
        assert historial.fecha_evento == datetime(2024, 1, 1)
        assert historial.observaciones == 'Test observación'
        assert historial.tenant_id == 1
        assert historial.fecha_creacion == datetime(2024, 1, 1)
        assert historial.fecha_actualizacion == datetime(2024, 1, 2)
    
    def test_from_db_row_valores_nulos(self):
        """Test from_db_row con valores nulos."""
        row = {
            'id': None,
            'id_potrero': None,
            'tipo_evento': None,
            'fecha_evento': None,
            'observaciones': None,
            'tenant_id': None,
            'fecha_creacion': None,
            'fecha_actualizacion': None
        }
        historial = HistorialPotrero.from_db_row(row)
        assert historial.id is None
        assert historial.id_potrero is None
        assert historial.tipo_evento is None
    
    def test_to_dict_completo(self):
        """Test conversión a diccionario con todos los campos."""
        fecha = datetime(2024, 1, 1, 12, 0, 0)
        historial = HistorialPotrero(
            id=1,
            id_potrero=10,
            tipo_evento=TipoEventoPotrero.LIMPIEZA,
            fecha_evento=fecha,
            observaciones='Limpieza realizada',
            tenant_id=1,
            fecha_creacion=fecha,
            fecha_actualizacion=fecha
        )
        result = historial.to_dict()
        assert result['id'] == 1
        assert result['id_potrero'] == 10
        assert result['tipo_evento'] == 'limpieza'
        assert result['fecha_evento'] == fecha.isoformat()
        assert result['observaciones'] == 'Limpieza realizada'
        assert result['tenant_id'] == 1
        assert result['fecha_creacion'] == fecha.isoformat()
        assert result['fecha_actualizacion'] == fecha.isoformat()
    
    def test_to_dict_valores_nulos(self):
        """Test to_dict con valores nulos."""
        historial = HistorialPotrero()
        result = historial.to_dict()
        assert result['id'] is None
        assert result['id_potrero'] is None
        assert result['tipo_evento'] is None
        assert result['fecha_evento'] is None
        assert result['observaciones'] is None
        assert result['tenant_id'] is None
        assert result['fecha_creacion'] is None
        assert result['fecha_actualizacion'] is None
    
    def test_to_dict_tipo_evento_nulo(self):
        """Test to_dict cuando tipo_evento es None."""
        historial = HistorialPotrero(tipo_evento=None)
        result = historial.to_dict()
        assert result['tipo_evento'] is None
    
    def test_from_dict(self):
        """Test creación desde diccionario."""
        fecha = datetime(2024, 1, 1)
        data = {
            'id': 1,
            'id_potrero': 10,
            'tipo_evento': 'inspeccion',
            'fecha_evento': fecha,
            'observaciones': 'Inspección realizada',
            'tenant_id': 1,
            'fecha_creacion': fecha,
            'fecha_actualizacion': fecha
        }
        historial = HistorialPotrero.from_dict(data)
        assert historial.id == 1
        assert historial.id_potrero == 10
        assert historial.tipo_evento == TipoEventoPotrero.INSPECCION
        assert historial.fecha_evento == fecha
        assert historial.observaciones == 'Inspección realizada'
        assert historial.tenant_id == 1
    
    def test_from_dict_valores_parciales(self):
        """Test from_dict con solo algunos valores."""
        data = {
            'id': 1,
            'tipo_evento': 'mantenimiento'
        }
        historial = HistorialPotrero.from_dict(data)
        assert historial.id == 1
        assert historial.tipo_evento == TipoEventoPotrero.MANTENIMIENTO
        assert historial.id_potrero is None

