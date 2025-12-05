"""Modelo para historial de potrero (eventos: limpiezas, uso, inspecciones, mantenimiento)."""
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


class TipoEventoPotrero(str, Enum):
    """Tipos de evento que se pueden registrar para un potrero."""
    USO = 'uso'
    LIMPIEZA = 'limpieza'
    INSPECCION = 'inspeccion'
    MANTENIMIENTO = 'mantenimiento'


class HistorialPotrero:
    """Modelo para representar un evento del historial de potrero."""
    
    def __init__(
        self,
        id: Optional[int] = None,
        id_potrero: Optional[int] = None,
        tipo_evento: Optional[TipoEventoPotrero] = None,
        fecha_evento: Optional[datetime] = None,
        observaciones: Optional[str] = None,
        tenant_id: Optional[int] = None,
        fecha_creacion: Optional[datetime] = None,
        fecha_actualizacion: Optional[datetime] = None
    ):
        """Inicializa un evento del historial de potrero."""
        self.id = id
        self.id_potrero = id_potrero
        self.tipo_evento = tipo_evento
        if isinstance(tipo_evento, str):
            self.tipo_evento = TipoEventoPotrero(tipo_evento)
        self.fecha_evento = fecha_evento
        self.observaciones = observaciones
        self.tenant_id = tenant_id
        self.fecha_creacion = fecha_creacion
        self.fecha_actualizacion = fecha_actualizacion
    
    @staticmethod
    def from_db_row(row: Dict[str, Any]) -> 'HistorialPotrero':
        """Crea una instancia desde una fila de base de datos."""
        return HistorialPotrero(
            id=row.get('id'),
            id_potrero=row.get('id_potrero'),
            tipo_evento=row.get('tipo_evento'),
            fecha_evento=row.get('fecha_evento'),
            observaciones=row.get('observaciones'),
            tenant_id=row.get('tenant_id'),
            fecha_creacion=row.get('fecha_creacion'),
            fecha_actualizacion=row.get('fecha_actualizacion')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la instancia a un diccionario."""
        return {
            'id': self.id,
            'id_potrero': self.id_potrero,
            'tipo_evento': self.tipo_evento.value if self.tipo_evento else None,
            'fecha_evento': self.fecha_evento.isoformat() if self.fecha_evento else None,
            'observaciones': self.observaciones,
            'tenant_id': self.tenant_id,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'HistorialPotrero':
        """Crea una instancia desde un diccionario."""
        return HistorialPotrero(
            id=data.get('id'),
            id_potrero=data.get('id_potrero'),
            tipo_evento=data.get('tipo_evento'),
            fecha_evento=data.get('fecha_evento'),
            observaciones=data.get('observaciones'),
            tenant_id=data.get('tenant_id'),
            fecha_creacion=data.get('fecha_creacion'),
            fecha_actualizacion=data.get('fecha_actualizacion')
        )

