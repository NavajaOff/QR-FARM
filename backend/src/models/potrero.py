"""Potrero model module."""
from typing import Dict, Any, Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum

class EstadoPotrero(str, Enum):
    DISPONIBLE = 'disponible'
    OCUPADO = 'ocupado'
    LIMPIEZA = 'limpieza'

class Potrero:
    """Potrero model representing a paddock/field in the system."""

    def __init__(
        self,
        id: Optional[int] = None,
        id_tipo_pasto: Optional[int] = None,
        nombre: str = None,
        capacidad: Optional[int] = None,
        hectareas: Optional[float] = None,
        ocupacion: int = 0,
        fecha_ultimo_uso: Optional[datetime] = None,
        responsable_persona_id: Optional[int] = None,
        proxima_limpieza: Optional[datetime] = None,
        area: Optional[Decimal] = None,
        ultima_limpieza: Optional[datetime] = None,
        descripcion: Optional[str] = None,
        propietario_persona_id: Optional[int] = None,
        estado: EstadoPotrero = EstadoPotrero.DISPONIBLE
    ):
        """Initialize Potrero model."""
        self.id = id
        self.id_tipo_pasto = id_tipo_pasto
        self.nombre = nombre
        self.estado = estado if isinstance(estado, EstadoPotrero) else EstadoPotrero(estado)
        self.capacidad = capacidad
        self.hectareas = hectareas
        self.ocupacion = ocupacion
        self.fecha_ultimo_uso = fecha_ultimo_uso
        self.responsable_persona_id = responsable_persona_id
        self.proxima_limpieza = proxima_limpieza
        self.area = area
        self.ultima_limpieza = ultima_limpieza
        self.descripcion = descripcion
        self.propietario_persona_id = propietario_persona_id

    @staticmethod
    def from_db_row(row: Dict[str, Any]) -> 'Potrero':
        """Create model from database row."""
        return Potrero(
            id=row.get('id'),
            id_tipo_pasto=row.get('id_tipo_pasto'),
            nombre=row.get('nombre'),
            estado=EstadoPotrero(row.get('estado', 'disponible')),
            capacidad=row.get('capacidad'),
            hectareas=row.get('hectareas'),
            ocupacion=row.get('ocupacion', 0),
            fecha_ultimo_uso=row.get('fecha_ultimo_uso'),
            responsable_persona_id=row.get('responsable_persona_id'),
            proxima_limpieza=row.get('proxima_limpieza'),
            area=Decimal(str(row.get('area'))) if row.get('area') is not None else None,
            ultima_limpieza=row.get('ultima_limpieza'),
            descripcion=row.get('descripcion'),
            propietario_persona_id=row.get('propietario_persona_id')
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
            'propietario_persona_id': self.propietario_persona_id
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Potrero':
        """Create model from dictionary."""
        return Potrero(
            nombre=data.get('nombre'),
            id_tipo_pasto=data.get('id_tipo_pasto'),
            estado=EstadoPotrero(data.get('estado', 'disponible')),
            capacidad=data.get('capacidad'),
            hectareas=data.get('hectareas'),
            ocupacion=data.get('ocupacion', 0),
            fecha_ultimo_uso=data.get('fecha_ultimo_uso'),
            responsable_persona_id=data.get('responsable_persona_id'),
            proxima_limpieza=data.get('proxima_limpieza'),
            area=Decimal(str(data.get('area'))) if data.get('area') is not None else None,
            ultima_limpieza=data.get('ultima_limpieza'),
            descripcion=data.get('descripcion'),
            propietario_persona_id=data.get('propietario_persona_id')
        )
