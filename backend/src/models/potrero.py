"""Potrero model module."""
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum

class EstadoPotrero(str, Enum):
    DISPONIBLE = 'disponible'
    OCUPADO = 'ocupado'
    LIMPIEZA = 'limpieza'

@dataclass
class PotreroData:
    """Container for Potrero initialization data."""
    id: Optional[int] = None
    id_tipo_pasto: Optional[int] = None
    nombre: Optional[str] = None
    capacidad: Optional[int] = None
    hectareas: Optional[float] = None
    area: Optional[Decimal] = None
    descripcion: Optional[str] = None
    responsable_persona_id: Optional[int] = None
    propietario_persona_id: Optional[int] = None
    # Nota: fecha_ultimo_uso, ultima_limpieza y proxima_limpieza ahora se obtienen
    # desde la tabla historial_potrero. Se mantienen aquí para compatibilidad.
    fecha_ultimo_uso: Optional[datetime] = None
    ultima_limpieza: Optional[datetime] = None
    proxima_limpieza: Optional[datetime] = None
    ocupacion: int = 0
    tenant_id: Optional[int] = None


class Potrero:
    """Potrero model representing a paddock/field in the system."""

    def __init__(
        self,
        datos: PotreroData,
        estado: EstadoPotrero = EstadoPotrero.DISPONIBLE
    ):
        """Initialize Potrero model with grouped data.

        Refactor: Constructor simplificado usando PotreroData.
        """
        self.id = datos.id
        self.id_tipo_pasto = datos.id_tipo_pasto
        self.nombre = datos.nombre
        self.estado = estado if isinstance(estado, EstadoPotrero) else EstadoPotrero(estado)
        self.capacidad = datos.capacidad
        self.hectareas = datos.hectareas
        self.ocupacion = datos.ocupacion
        self.fecha_ultimo_uso = datos.fecha_ultimo_uso
        self.responsable_persona_id = datos.responsable_persona_id
        self.proxima_limpieza = datos.proxima_limpieza
        self.area = datos.area
        self.ultima_limpieza = datos.ultima_limpieza
        self.descripcion = datos.descripcion
        self.propietario_persona_id = datos.propietario_persona_id
        self.tenant_id = datos.tenant_id

    @classmethod
    def from_params(
        cls,
        *,
        estado: EstadoPotrero = EstadoPotrero.DISPONIBLE,
        **kwargs
    ) -> 'Potrero':
        """Backward compatible constructor with explicit parameters."""
        datos = PotreroData(**kwargs)
        return cls(datos=datos, estado=estado)

    @staticmethod
    def from_db_row(row: Dict[str, Any]) -> 'Potrero':
        """Create model from database row."""
        area_value = row.get('area')
        datos = PotreroData(
            id=row.get('id'),
            id_tipo_pasto=row.get('id_tipo_pasto'),
            nombre=row.get('nombre'),
            capacidad=row.get('capacidad'),
            hectareas=row.get('hectareas'),
            ocupacion=row.get('ocupacion', 0),
            fecha_ultimo_uso=row.get('fecha_ultimo_uso'),
            responsable_persona_id=row.get('responsable_persona_id'),
            proxima_limpieza=row.get('proxima_limpieza'),
            area=Decimal(str(area_value)) if area_value is not None else None,
            ultima_limpieza=row.get('ultima_limpieza'),
            descripcion=row.get('descripcion'),
            propietario_persona_id=row.get('propietario_persona_id'),
            tenant_id=row.get('tenant_id')
        )
        return Potrero(
            datos=datos,
            estado=EstadoPotrero(row.get('estado', 'disponible'))
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'id_tipo_pasto': self.id_tipo_pasto,
            'nombre': self.nombre,
            'estado': self.estado.value,
            'capacidad': self.capacidad,
            'hectareas': self.hectareas,
            'ocupacion': self.ocupacion,
            'fecha_ultimo_uso': self.fecha_ultimo_uso.isoformat() if self.fecha_ultimo_uso else None,
            'responsable_persona_id': self.responsable_persona_id,
            'proxima_limpieza': self.proxima_limpieza.isoformat() if self.proxima_limpieza else None,
            'area': float(self.area) if self.area else None,
            'ultima_limpieza': self.ultima_limpieza.isoformat() if self.ultima_limpieza else None,
            'descripcion': self.descripcion,
            'propietario_persona_id': self.propietario_persona_id,
            'tenant_id': self.tenant_id
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Potrero':
        """Create model from dictionary."""
        area_value = data.get('area')
        datos = PotreroData(
            id=data.get('id'),
            nombre=data.get('nombre'),
            id_tipo_pasto=data.get('id_tipo_pasto'),
            capacidad=data.get('capacidad'),
            hectareas=data.get('hectareas'),
            ocupacion=data.get('ocupacion', 0),
            fecha_ultimo_uso=data.get('fecha_ultimo_uso'),
            responsable_persona_id=data.get('responsable_persona_id'),
            proxima_limpieza=data.get('proxima_limpieza'),
            area=Decimal(str(area_value)) if area_value is not None else None,
            ultima_limpieza=data.get('ultima_limpieza'),
            descripcion=data.get('descripcion'),
            propietario_persona_id=data.get('propietario_persona_id'),
            tenant_id=data.get('tenant_id')
        )
        return Potrero(
            datos=datos,
            estado=EstadoPotrero(data.get('estado', 'disponible'))
        )
