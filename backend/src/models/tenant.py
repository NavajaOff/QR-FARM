"""Modelo Tenant para multi-tenancy."""
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class EstadoTenant(str, Enum):
    """Estados posibles de un tenant."""
    ACTIVO = 'activo'
    INACTIVO = 'inactivo'


@dataclass
class Tenant:
    """Modelo Tenant para aislamiento de datos."""
    id: Optional[int] = None
    nombre: str = ""
    codigo_tenant: str = ""
    estado: EstadoTenant = EstadoTenant.ACTIVO
    fecha_creacion: Optional[str] = None
    fecha_actualizacion: Optional[str] = None

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Tenant':
        """Crea instancia desde diccionario."""
        estado = data.get('estado', 'activo')
        if isinstance(estado, str):
            estado = EstadoTenant(estado)
        
        return Tenant(
            id=data.get('id'),
            nombre=data.get('nombre', ''),
            codigo_tenant=data.get('codigo_tenant', ''),
            estado=estado,
            fecha_creacion=data.get('fecha_creacion'),
            fecha_actualizacion=data.get('fecha_actualizacion')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario."""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'codigo_tenant': self.codigo_tenant,
            'estado': self.estado.value if hasattr(self.estado, 'value') else str(self.estado),
            'fecha_creacion': self.fecha_creacion,
            'fecha_actualizacion': self.fecha_actualizacion
        }

