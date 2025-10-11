# Modelo Usuario
from typing import Optional, Dict, Any
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario:
    def __init__(self,
                 id: Optional[int] = None,
                 primer_nombre: str = "",
                 segundo_nombre: Optional[str] = None,
                 primer_apellido: str = "",
                 segundo_apellido: Optional[str] = None,
                 direccion: str = "",
                 telefono: str = "",
                 email: str = "",
                 password_hash: str = "",
                 pais: str = "",
                 tipo_documento: str = "",
                 numero_documento: str = "",
                 observaciones: Optional[str] = None,
                 fecha_registro: Optional[datetime] = None,
                 activo: bool = True):
        
        self.id = id
        self.primer_nombre = primer_nombre
        self.segundo_nombre = segundo_nombre
        self.primer_apellido = primer_apellido
        self.segundo_apellido = segundo_apellido
        self.direccion = direccion
        self.telefono = telefono
        self.email = email
        self.password_hash = password_hash
        self.pais = pais
        self.tipo_documento = tipo_documento
        self.numero_documento = numero_documento
        self.observaciones = observaciones
        self.fecha_registro = fecha_registro
        self.activo = activo

    def set_password(self, password: str) -> None:
        """Genera el hash de la contraseña proporcionada"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verifica si la contraseña proporcionada coincide con el hash almacenado"""
        return check_password_hash(self.password_hash, password)

    @property
    def nombre_completo(self) -> str:
        """Retorna el nombre completo del usuario"""
        nombres = [self.primer_nombre]
        if self.segundo_nombre:
            nombres.append(self.segundo_nombre)
        
        apellidos = [self.primer_apellido]
        if self.segundo_apellido:
            apellidos.append(self.segundo_apellido)
            
        return f"{' '.join(nombres)} {' '.join(apellidos)}"

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Usuario':
        """Crea una instancia de Usuario desde un diccionario"""
        usuario = Usuario(
            id=data.get('id'),
            primer_nombre=data.get('primer_nombre', ''),
            segundo_nombre=data.get('segundo_nombre'),
            primer_apellido=data.get('primer_apellido', ''),
            segundo_apellido=data.get('segundo_apellido'),
            direccion=data.get('direccion', ''),
            telefono=data.get('telefono', ''),
            email=data.get('email', ''),
            password_hash=data.get('password_hash', ''),
            pais=data.get('pais', ''),
            tipo_documento=data.get('tipo_documento', ''),
            numero_documento=data.get('numero_documento', ''),
            observaciones=data.get('observaciones'),
            fecha_registro=data.get('fecha_registro'),
            activo=data.get('activo', True)
        )
        return usuario

    def to_dict(self, include_password: bool = False) -> Dict[str, Any]:
        """Convierte la instancia de Usuario a un diccionario"""
        data = {
            'id': self.id,
            'primer_nombre': self.primer_nombre,
            'segundo_nombre': self.segundo_nombre,
            'primer_apellido': self.primer_apellido,
            'segundo_apellido': self.segundo_apellido,
            'direccion': self.direccion,
            'telefono': self.telefono,
            'email': self.email,
            'pais': self.pais,
            'tipo_documento': self.tipo_documento,
            'numero_documento': self.numero_documento,
            'observaciones': self.observaciones,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'activo': self.activo,
            'nombre_completo': self.nombre_completo
        }
        
        if include_password:
            data['password_hash'] = self.password_hash
            
        return data
