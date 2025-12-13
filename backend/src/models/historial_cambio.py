# Modelo HistorialCambio
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class TipoEntidad(str, Enum):
    POTRERO = 'potrero'
    GANADO = 'ganado'
    VACUNA = 'vacuna'
    USUARIO = 'usuario'
    TENANT = 'tenant'
    OTRO = 'otro'


class TipoAccion(str, Enum):
    CREAR = 'crear'
    ACTUALIZAR = 'actualizar'
    ELIMINAR = 'eliminar'
    ACTIVAR = 'activar'
    DESACTIVAR = 'desactivar'


class HistorialCambio:
    def __init__(self,
                 id: Optional[int] = None,
                 tenant_id: Optional[int] = None,
                 usuario_id: Optional[int] = None,
                 entidad_tipo: TipoEntidad = TipoEntidad.OTRO,
                 entidad_id: Optional[int] = None,
                 accion: TipoAccion = TipoAccion.ACTUALIZAR,
                 datos_anteriores: Optional[Dict[str, Any]] = None,
                 datos_nuevos: Optional[Dict[str, Any]] = None,
                 descripcion: Optional[str] = None,
                 fecha_cambio: Optional[datetime] = None):

        self.id = id
        self.tenant_id = tenant_id
        self.usuario_id = usuario_id
        self.entidad_tipo = entidad_tipo
        self.entidad_id = entidad_id
        self.accion = accion
        self.datos_anteriores = datos_anteriores
        self.datos_nuevos = datos_nuevos
        self.descripcion = descripcion
        self.fecha_cambio = fecha_cambio

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'HistorialCambio':
        return HistorialCambio(
            id=data.get('id'),
            tenant_id=data.get('tenant_id'),
            usuario_id=data.get('usuario_id'),
            entidad_tipo=TipoEntidad(data.get('entidad_tipo', 'otro')),
            entidad_id=data.get('entidad_id'),
            accion=TipoAccion(data.get('accion', 'actualizar')),
            datos_anteriores=data.get('datos_anteriores'),
            datos_nuevos=data.get('datos_nuevos'),
            descripcion=data.get('descripcion'),
            fecha_cambio=data.get('fecha_cambio')
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'usuario_id': self.usuario_id,
            'entidad_tipo': self.entidad_tipo.value,
            'entidad_id': self.entidad_id,
            'accion': self.accion.value,
            'datos_anteriores': self.datos_anteriores,
            'datos_nuevos': self.datos_nuevos,
            'descripcion': self.descripcion,
            'fecha_cambio': self.fecha_cambio.isoformat() if self.fecha_cambio else None
        }
