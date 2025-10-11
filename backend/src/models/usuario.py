# Modelo Usuario
from typing import Optional, Dict, Any
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum

class EstadoUsuario(str, Enum):
    ACTIVO = 'activo'
    INACTIVO = 'inactivo'

class Rol:
    def __init__(self,
                 id: Optional[int] = None,
                 rol: str = ""):
        self.id = id
        self.rol = rol

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Rol':
        return Rol(
            id=data.get('id'),
            rol=data.get('rol', '')
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'rol': self.rol
        }

class Persona:
    def __init__(self,
                 id: Optional[int] = None,
                 id_rol: Optional[int] = None,
                 primer_nombre: str = "",
                 segundo_nombre: Optional[str] = None,
                 primer_apellido: str = "",
                 segundo_apellido: Optional[str] = None,
                 email: str = "",
                 telefono: Optional[str] = None,
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None):
        
        self.id = id
        self.id_rol = id_rol
        self.primer_nombre = primer_nombre
        self.segundo_nombre = segundo_nombre
        self.primer_apellido = primer_apellido
        self.segundo_apellido = segundo_apellido
        self.email = email
        self.telefono = telefono
        self.created_at = created_at
        self.updated_at = updated_at

    @property
    def nombre_completo(self) -> str:
        """Retorna el nombre completo de la persona"""
        nombres = [self.primer_nombre]
        if self.segundo_nombre:
            nombres.append(self.segundo_nombre)
        
        apellidos = [self.primer_apellido]
        if self.segundo_apellido:
            apellidos.append(self.segundo_apellido)
            
        return f"{' '.join(nombres)} {' '.join(apellidos)}"

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Persona':
        return Persona(
            id=data.get('id'),
            id_rol=data.get('id_rol'),
            primer_nombre=data.get('primer_nombre', ''),
            segundo_nombre=data.get('segundo_nombre'),
            primer_apellido=data.get('primer_apellido', ''),
            segundo_apellido=data.get('segundo_apellido'),
            email=data.get('email', ''),
            telefono=data.get('telefono'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'id_rol': self.id_rol,
            'primer_nombre': self.primer_nombre,
            'segundo_nombre': self.segundo_nombre,
            'primer_apellido': self.primer_apellido,
            'segundo_apellido': self.segundo_apellido,
            'email': self.email,
            'telefono': self.telefono,
            'nombre_completo': self.nombre_completo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Usuario:
    def __init__(self,
                 id: Optional[int] = None,
                 id_persona: int = 0,
                 id_rol: int = 0,
                 username: Optional[str] = None,
                 password_hash: Optional[str] = None,
                 estado: EstadoUsuario = EstadoUsuario.ACTIVO,
                 last_login: Optional[datetime] = None,
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None,
                 persona: Optional[Persona] = None):
        
        self.id = id
        self.id_persona = id_persona
        self.id_rol = id_rol
        self.username = username
        self.password_hash = password_hash
        self.estado = estado
        self.last_login = last_login
        self.created_at = created_at
        self.updated_at = updated_at
        self.persona = persona

    def set_password(self, password: str) -> None:
        """Genera el hash de la contraseña proporcionada"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verifica si la contraseña proporcionada coincide con el hash almacenado"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def from_dict(data: Dict[str, Any], include_persona: bool = True) -> 'Usuario':
        usuario = Usuario(
            id=data.get('id'),
            id_persona=data.get('id_persona', 0),
            id_rol=data.get('id_rol', 0),
            username=data.get('username'),
            password_hash=data.get('password_hash'),
            estado=EstadoUsuario(data.get('estado', 'activo')),
            last_login=data.get('last_login'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
        
        if include_persona and 'persona' in data and data['persona']:
            usuario.persona = Persona.from_dict(data['persona'])
            
        return usuario

    def to_dict(self, include_persona: bool = True) -> Dict[str, Any]:
        data = {
            'id': self.id,
            'id_persona': self.id_persona,
            'id_rol': self.id_rol,
            'username': self.username,
            'estado': self.estado.value,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_persona and self.persona:
            data['persona'] = self.persona.to_dict()
            
        return data
        
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
