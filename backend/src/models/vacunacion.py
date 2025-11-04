# Modelo Vacunacion
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

class EstadoVacunacion(str, Enum):
    aplicada = "aplicada"
    pendiente = "pendiente"

class Vacunacion:
    def __init__(self,
                 id: Optional[int] = None,
                 id_animal: Optional[int] = None,
                 nombre_animal: Optional[str] = None,
                 fecha_inicio: Optional[datetime] = None,
                 fecha_fin: Optional[datetime] = None,
                 fecha_aplicacion: Optional[datetime] = None,
                 proxima_dosis: Optional[datetime] = None,
                 responsable: Optional[int] = None,
                 estado: EstadoVacunacion = EstadoVacunacion.pendiente,
                 id_tipo_vacuna: Optional[int] = None,
                 nombre_tipo_vacuna: Optional[str] = None,
                 nombre_responsable: Optional[str] = None):
        self.id = id
        self.id_animal = id_animal
        self.nombre_animal = nombre_animal
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.fecha_aplicacion = fecha_aplicacion
        self.proxima_dosis = proxima_dosis
        self.responsable = responsable
        self.estado = estado
        self.id_tipo_vacuna = id_tipo_vacuna
        self.nombre_tipo_vacuna = nombre_tipo_vacuna
        self.nombre_responsable = nombre_responsable

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Vacunacion':
        """Crear instancia desde diccionario"""
        return Vacunacion(
            id=data.get('id'),
            id_animal=data.get('id_animal'),
            nombre_animal=data.get('nombre_animal'),
            fecha_inicio=data.get('fecha_inicio'),
            fecha_fin=data.get('fecha_fin'),
            fecha_aplicacion=data.get('fecha_aplicacion'),
            proxima_dosis=data.get('proxima_dosis'),
            responsable=data.get('responsable'),
            estado=EstadoVacunacion(data.get('estado', 'pendiente')),
            id_tipo_vacuna=data.get('id_tipo_vacuna'),
            nombre_tipo_vacuna=data.get('nombre_tipo_vacuna'),
            nombre_responsable=data.get('nombre_responsable')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        def safe_isoformat(date_value):
            if date_value is None:
                return None
            if isinstance(date_value, str):
                return date_value
            return date_value.isoformat()

        return {
            "id": self.id,
            "id_animal": self.id_animal,
            "nombre_animal": self.nombre_animal,
            "fecha_inicio": safe_isoformat(self.fecha_inicio),
            "fecha_fin": safe_isoformat(self.fecha_fin),
            "fecha_aplicacion": safe_isoformat(self.fecha_aplicacion),
            "proxima_dosis": safe_isoformat(self.proxima_dosis),
            "responsable": self.responsable,
            "estado": self.estado.value if hasattr(self.estado, 'value') else str(self.estado),
            "id_tipo_vacuna": self.id_tipo_vacuna,
            "nombre_tipo_vacuna": self.nombre_tipo_vacuna,
            "nombre_responsable": self.nombre_responsable
        }