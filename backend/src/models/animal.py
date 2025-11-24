# Modelo Ganado
from typing import Optional, Dict, Any
from datetime import date
from enum import Enum

class EstadoGanado(str, Enum):
    SALUDABLE = 'saludable'
    REVISION = 'revision'
    ENFERMO = 'enfermo'

class SexoGanado(str, Enum):
    MACHO = 'macho'
    HEMBRA = 'hembra'

# Estados de baja ahora están en estado_ganado (id 4-8)
# Estados activos: saludable (1), revision (2), enfermo (3)
# Estados de baja: dado_de_baja (4), muerte (5), venta (6), robo (7), otra (8)

class Ganado:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.codigo_qr = kwargs.get('codigo_qr')
        self.id_potrero = kwargs.get('id_potrero')
        self.id_persona = kwargs.get('id_persona')
        self.nombre = kwargs.get('nombre', "")
        self.raza = kwargs.get('raza')
        self.fecha_nacimiento = kwargs.get('fecha_nacimiento')
        self.edad = kwargs.get('edad')
        self.sexo = kwargs.get('sexo', SexoGanado.MACHO)
        self.peso = kwargs.get('peso')
        self.estado = kwargs.get('estado', 'saludable')
        self.estado_salud = kwargs.get('estado_salud')
        self.estado_tipo = kwargs.get('estado_tipo')
        # estado_baja ahora se determina por id_estado (si id_estado >= 4, está dado de baja)
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Ganado':
        """
        Crea una instancia de Ganado desde un diccionario
        """
        return Ganado(
            id=data.get('id'),
            codigo_qr=data.get('codigo_qr'),
            id_potrero=data.get('id_potrero'),
            id_persona=data.get('id_persona'),
            nombre=data.get('nombre', ''),
            raza=data.get('raza'),
            fecha_nacimiento=data.get('fecha_nacimiento'),
            edad=data.get('edad'),
            sexo=SexoGanado(data.get('sexo', 'macho')),
            peso=float(data.get('peso')) if data.get('peso') is not None else None,
            estado=data.get('estado_tipo') or data.get('estado') or 'saludable',
            estado_salud=data.get('estado_salud'),
            estado_tipo=data.get('estado_tipo'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    @staticmethod
    def es_estado_baja(id_estado: Optional[int]) -> bool:
        """Determina si un id_estado corresponde a un estado de baja."""
        if id_estado is None:
            return False
        # Estados de baja: 4-8
        return 4 <= id_estado <= 8
    
    @staticmethod
    def es_estado_activo(id_estado: Optional[int]) -> bool:
        """Determina si un id_estado corresponde a un estado activo."""
        if id_estado is None:
            return True  # Por defecto activo
        # Estados activos: 1-3
        return 1 <= id_estado <= 3

    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte la instancia de Ganado a un diccionario
        """
        from datetime import datetime

        def safe_isoformat(date_value):
            if isinstance(date_value, datetime):
                return date_value.isoformat()
            return date_value

        return {
            'id': self.id,
            'codigo_qr': self.codigo_qr,
            'id_potrero': self.id_potrero,
            'id_persona': self.id_persona,
            'nombre': self.nombre,
            'raza': self.raza,
            'fecha_nacimiento': safe_isoformat(self.fecha_nacimiento),
            'edad': self.edad,
            'sexo': self.sexo.value,
            'peso': self.peso,
            'estado': self.estado,
            'estado_salud': self.estado_salud,
            'created_at': safe_isoformat(self.created_at),
            'updated_at': safe_isoformat(self.updated_at)
        }
