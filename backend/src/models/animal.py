# Modelo Ganado
from typing import Optional, Dict, Any
from datetime import date
from enum import Enum

class EstadoGanado(str, Enum):
    ACTIVO = 'activo'
    VENDIDO = 'vendido'
    REVISION = 'revision'
    ENFERMO = 'enfermo'

class SexoGanado(str, Enum):
    MACHO = 'macho'
    HEMBRA = 'hembra'

class Ganado:
    def __init__(self,
                 id: Optional[int] = None,
                 codigo_qr: Optional[str] = None,
                 id_potrero: Optional[int] = None,
                 id_persona: Optional[int] = None,
                 nombre: str = "",
                 raza: Optional[str] = None,
                 fecha_nacimiento: Optional[date] = None,
                 edad: Optional[int] = None,
                 sexo: SexoGanado = SexoGanado.MACHO,
                 peso: Optional[float] = None,
                 estado: EstadoGanado = EstadoGanado.ACTIVO,
                 estado_salud: Optional[str] = None,
                 estado_tipo: Optional[str] = None,
                 created_at: Optional[date] = None,
                 updated_at: Optional[date] = None):

        self.id = id
        self.codigo_qr = codigo_qr
        self.id_potrero = id_potrero
        self.id_persona = id_persona
        self.nombre = nombre
        self.raza = raza
        self.fecha_nacimiento = fecha_nacimiento
        self.edad = edad
        self.sexo = sexo
        self.peso = peso
        self.estado = estado
        self.estado_salud = estado_salud
        self.estado_tipo = estado_tipo
        self.created_at = created_at
        self.updated_at = updated_at

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
            estado=EstadoGanado(data.get('estado', 'activo')),
            estado_salud=data.get('estado_salud'),
            estado_tipo=data.get('estado_tipo'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

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
            'estado': self.estado.value,
            'estado_salud': self.estado_salud,
            'created_at': safe_isoformat(self.created_at),
            'updated_at': safe_isoformat(self.updated_at)
        }
