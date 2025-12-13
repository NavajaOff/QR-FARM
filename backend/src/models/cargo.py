# Modelo Cargo
from typing import Optional, Dict, Any


class Cargo:
    def __init__(self,
                 id: Optional[int] = None,
                 nombre_cargo: str = "",
                 descripcion: Optional[str] = None):

        self.id = id
        self.nombre_cargo = nombre_cargo
        self.descripcion = descripcion

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Cargo':
        return Cargo(
            id=data.get('id'),
            nombre_cargo=data.get('nombre_cargo', ''),
            descripcion=data.get('descripcion')
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'nombre_cargo': self.nombre_cargo,
            'descripcion': self.descripcion
        }
