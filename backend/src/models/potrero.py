"""Potrero model module."""
from typing import Dict, Any, Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum

class EstadoPotrero(str, Enum):
    DISPONIBLE = 'disponible'
    EN_USO = 'en_uso'
    MANTENIMIENTO = 'mantenimiento'
    INACTIVO = 'inactivo'

class Potrero:
    """Potrero model representing a paddock/field in the system."""

    def __init__(
        self,
        id: Optional[int] = None,
        nombre: str = None,
        estado: EstadoPotrero = EstadoPotrero.DISPONIBLE,
        capacidad: Optional[int] = None,
        ocupacion: int = 0,
        tipo_pasto: Optional[str] = None,
        fecha_ultimo_uso: Optional[datetime] = None,
        responsable_persona_id: Optional[int] = None,
        proxima_limpieza: Optional[datetime] = None,
        area: Optional[Decimal] = None,
        ultima_limpieza: Optional[datetime] = None,
        ubicacion: Optional[str] = None,
        descripcion: Optional[str] = None,
        propietario_persona_id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        deleted_at: Optional[datetime] = None
    ):
        """Initialize Potrero model."""
        self.id = id
        self.nombre = nombre
        self.estado = estado if isinstance(estado, EstadoPotrero) else EstadoPotrero(estado)
        self.capacidad = capacidad
        self.ocupacion = ocupacion
        self.tipo_pasto = tipo_pasto
        self.fecha_ultimo_uso = fecha_ultimo_uso
        self.responsable_persona_id = responsable_persona_id
        self.proxima_limpieza = proxima_limpieza
        self.area = area
        self.ultima_limpieza = ultima_limpieza
        self.ubicacion = ubicacion
        self.descripcion = descripcion
        self.propietario_persona_id = propietario_persona_id
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.deleted_at = deleted_at

    @staticmethod
    def from_db_row(row: Dict[str, Any]) -> 'Potrero':
        """Create model from database row."""
        return Potrero(
            id=row.get('id'),
            nombre=row.get('nombre'),
            estado=EstadoPotrero(row.get('estado', 'disponible')),
            capacidad=row.get('capacidad'),
            ocupacion=row.get('ocupacion'),
            tipo_pasto=row.get('tipo_pasto'),
            fecha_ultimo_uso=row.get('fecha_ultimo_uso'),
            responsable_persona_id=row.get('responsable_persona_id'),
            proxima_limpieza=row.get('proxima_limpieza'),
            area=Decimal(str(row.get('area'))) if row.get('area') is not None else None,
            ultima_limpieza=row.get('ultima_limpieza'),
            ubicacion=row.get('ubicacion'),
            descripcion=row.get('descripcion'),
            propietario_persona_id=row.get('propietario_persona_id'),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at'),
            deleted_at=row.get('deleted_at')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'estado': self.estado.value,
            'capacidad': self.capacidad,
            'ocupacion': self.ocupacion,
            'tipo_pasto': self.tipo_pasto,
            'fecha_ultimo_uso': self.fecha_ultimo_uso.isoformat() if self.fecha_ultimo_uso else None,
            'responsable_persona_id': self.responsable_persona_id,
            'proxima_limpieza': self.proxima_limpieza.isoformat() if self.proxima_limpieza else None,
            'area': float(self.area) if self.area else None,
            'ultima_limpieza': self.ultima_limpieza.isoformat() if self.ultima_limpieza else None,
            'ubicacion': self.ubicacion,
            'descripcion': self.descripcion,
            'propietario_persona_id': self.propietario_persona_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Potrero':
        """Create model from dictionary."""
        return Potrero(
            nombre=data.get('nombre'),
            estado=EstadoPotrero(data.get('estado', 'disponible')),
            capacidad=data.get('capacidad'),
            ocupacion=data.get('ocupacion', 0),
            tipo_pasto=data.get('tipo_pasto'),
            fecha_ultimo_uso=data.get('fecha_ultimo_uso'),
            responsable_persona_id=data.get('responsable_persona_id'),
            proxima_limpieza=data.get('proxima_limpieza'),
            area=Decimal(str(data.get('area'))) if data.get('area') is not None else None,
            ultima_limpieza=data.get('ultima_limpieza'),
            ubicacion=data.get('ubicacion'),
            descripcion=data.get('descripcion'),
            propietario_persona_id=data.get('propietario_persona_id')
        )
