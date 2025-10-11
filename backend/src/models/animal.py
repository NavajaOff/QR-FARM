# Modelo Animal
from typing import Optional, Dict, Any
from datetime import date

class Animal:
    def __init__(self, 
                 id: Optional[int] = None,
                 codigo_qr: str = "",
                 nombre: str = "",
                 raza: str = "",
                 genero: str = "",
                 fecha_nacimiento: Optional[date] = None,
                 peso: float = 0.0,
                 estado_salud: str = "",
                 historial_vacunas: str = "",
                 potrero_id: Optional[int] = None,
                 madre_id: Optional[int] = None,
                 padre_id: Optional[int] = None,
                 fecha_registro: Optional[date] = None,
                 ultima_actualizacion: Optional[date] = None):
        
        self.id = id
        self.codigo_qr = codigo_qr
        self.nombre = nombre
        self.raza = raza
        self.genero = genero
        self.fecha_nacimiento = fecha_nacimiento
        self.peso = peso
        self.estado_salud = estado_salud
        self.historial_vacunas = historial_vacunas
        self.potrero_id = potrero_id
        self.madre_id = madre_id
        self.padre_id = padre_id
        self.fecha_registro = fecha_registro
        self.ultima_actualizacion = ultima_actualizacion

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Animal':
        """
        Crea una instancia de Animal desde un diccionario
        """
        return Animal(
            id=data.get('id'),
            codigo_qr=data.get('codigo_qr', ''),
            nombre=data.get('nombre', ''),
            raza=data.get('raza', ''),
            genero=data.get('genero', ''),
            fecha_nacimiento=data.get('fecha_nacimiento'),
            peso=float(data.get('peso', 0.0)),
            estado_salud=data.get('estado_salud', ''),
            historial_vacunas=data.get('historial_vacunas', ''),
            potrero_id=data.get('potrero_id'),
            madre_id=data.get('madre_id'),
            padre_id=data.get('padre_id'),
            fecha_registro=data.get('fecha_registro'),
            ultima_actualizacion=data.get('ultima_actualizacion')
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte la instancia de Animal a un diccionario
        """
        return {
            'id': self.id,
            'codigo_qr': self.codigo_qr,
            'nombre': self.nombre,
            'raza': self.raza,
            'genero': self.genero,
            'fecha_nacimiento': self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None,
            'peso': self.peso,
            'estado_salud': self.estado_salud,
            'historial_vacunas': self.historial_vacunas,
            'potrero_id': self.potrero_id,
            'madre_id': self.madre_id,
            'padre_id': self.padre_id,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'ultima_actualizacion': self.ultima_actualizacion.isoformat() if self.ultima_actualizacion else None
        }
