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
    tenant_id: Optional[int] = None
    id_tipo_pasto: Optional[int] = None
    responsable_persona_id: Optional[int] = None
    id_estado_potrero: Optional[int] = None
    nombre: Optional[str] = None
    capacidad: Optional[int] = None
    ocupacion: int = 0
    hectareas: Optional[float] = None
    area: Optional[Decimal] = None
    descripcion: Optional[str] = None
    # Nota: fecha_ultimo_uso, ultima_limpieza y proxima_limpieza ahora se obtienen
    # desde la tabla historial_potreros. Se mantienen aquí para compatibilidad.
    fecha_ultimo_uso: Optional[datetime] = None
    ultima_limpieza: Optional[datetime] = None
    proxima_limpieza: Optional[datetime] = None


class Potrero:
    """Potrero model representing a paddock/field in the system."""

    def __init__(
        self,
        datos: PotreroData
    ):
        """Initialize Potrero model with grouped data.

        Refactor: Constructor simplificado usando PotreroData.
        """
        self.id = datos.id
        self.tenant_id = datos.tenant_id
        self.id_tipo_pasto = datos.id_tipo_pasto
        self.responsable_persona_id = datos.responsable_persona_id
        self.id_estado_potrero = datos.id_estado_potrero
        self.nombre = datos.nombre
        self.capacidad = datos.capacidad
        self.ocupacion = datos.ocupacion
        self.hectareas = datos.hectareas
        self.area = datos.area
        self.descripcion = datos.descripcion
        # Fechas se obtienen desde historial_potreros
        self.fecha_ultimo_uso = datos.fecha_ultimo_uso
        self.ultima_limpieza = datos.ultima_limpieza
        self.proxima_limpieza = datos.proxima_limpieza

    @classmethod
    def from_params(
        cls,
        *,
        **kwargs
    ) -> 'Potrero':
        """Constructor with explicit parameters."""
        datos = PotreroData(**kwargs)
        return cls(datos=datos)

    @staticmethod
    def from_db_row(row: Dict[str, Any]) -> 'Potrero':
        """Create model from database row."""
        area_value = row.get('area')
        datos = PotreroData(
            id=row.get('id'),
            tenant_id=row.get('tenant_id'),
            id_tipo_pasto=row.get('id_tipo_pasto'),
            responsable_persona_id=row.get('responsable_persona_id'),
            id_estado_potrero=row.get('id_estado_potrero'),
            nombre=row.get('nombre'),
            capacidad=row.get('capacidad'),
            ocupacion=row.get('ocupacion', 0),
            hectareas=row.get('hectareas'),
            area=Decimal(str(area_value)) if area_value is not None else None,
            descripcion=row.get('descripcion'),
            fecha_ultimo_uso=row.get('fecha_ultimo_uso'),
            ultima_limpieza=row.get('ultima_limpieza'),
            proxima_limpieza=row.get('proxima_limpieza')
        )
        return Potrero(datos=datos)

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'id_tipo_pasto': self.id_tipo_pasto,
            'responsable_persona_id': self.responsable_persona_id,
            'id_estado_potrero': self.id_estado_potrero,
            'nombre': self.nombre,
            'capacidad': self.capacidad,
            'ocupacion': self.ocupacion,
            'hectareas': self.hectareas,
            'area': float(self.area) if self.area else None,
            'descripcion': self.descripcion,
            'fecha_ultimo_uso': self.fecha_ultimo_uso.isoformat() if self.fecha_ultimo_uso else None,
            'ultima_limpieza': self.ultima_limpieza.isoformat() if self.ultima_limpieza else None,
            'proxima_limpieza': self.proxima_limpieza.isoformat() if self.proxima_limpieza else None
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Potrero':
        """Create model from dictionary."""
        area_value = data.get('area')
        datos = PotreroData(
            id=data.get('id'),
            tenant_id=data.get('tenant_id'),
            id_tipo_pasto=data.get('id_tipo_pasto'),
            responsable_persona_id=data.get('responsable_persona_id'),
            id_estado_potrero=data.get('id_estado_potrero'),
            nombre=data.get('nombre'),
            capacidad=data.get('capacidad'),
            ocupacion=data.get('ocupacion', 0),
            hectareas=data.get('hectareas'),
            area=Decimal(str(area_value)) if area_value is not None else None,
            descripcion=data.get('descripcion'),
            fecha_ultimo_uso=data.get('fecha_ultimo_uso'),
            ultima_limpieza=data.get('ultima_limpieza'),
            proxima_limpieza=data.get('proxima_limpieza')
        )
        return Potrero(datos=datos)
