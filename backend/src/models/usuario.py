# Modelo Usuario
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum

class EstadoUsuario(str, Enum):
    ACTIVO = 'activo'
    INACTIVO = 'inactivo'

class EstadoGanado(str, Enum):
    ACTIVO = 'activo'
    VENDIDO = 'vendido'
    MUERTO = 'muerto'

class SexoGanado(str, Enum):
    MACHO = 'macho'
    HEMBRA = 'hembra'
    OTRO = 'otro'

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
                 fecha_creacion: Optional[datetime] = None):

        self.id = id
        self.id_rol = id_rol
        self.primer_nombre = primer_nombre
        self.segundo_nombre = segundo_nombre
        self.primer_apellido = primer_apellido
        self.segundo_apellido = segundo_apellido
        self.email = email
        self.telefono = telefono
        self.fecha_creacion = fecha_creacion

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
            fecha_creacion=data.get('fecha_creacion')
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
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }

class Usuario:
    def __init__(self,
                 id: Optional[int] = None,
                 id_persona: Optional[int] = None,
                 id_rol: Optional[int] = None,
                 contrasena: Optional[str] = None,
                 estado: EstadoUsuario = EstadoUsuario.ACTIVO,
                 persona: Optional[Persona] = None,
                 rol: Optional[Rol] = None):

        self.id = id
        self.id_persona = id_persona
        self.id_rol = id_rol
        self.contrasena = contrasena
        self.estado = estado
        self.persona = persona
        self.rol = rol

        # Alias para compatibilidad
        self.password_hash = self.contrasena

    @property
    def nombre_completo(self) -> str:
        """Retorna el nombre completo del usuario basado en la persona asociada"""
        if self.persona:
            return self.persona.nombre_completo
        return ""

    def set_password(self, password: str) -> None:
        """Establece la contrasena (sin hash, según nueva estructura BD)"""
        self.contrasena = password

    def check_password(self, password: str) -> bool:
        """Verifica si la contrasena proporcionada coincide"""
        if self.contrasena is None:
            return False
        # Comparación directa sin hash (según estructura BD actual)
        return self.contrasena == password

    @staticmethod
    def from_dict(data: Dict[str, Any], include_persona: bool = True) -> 'Usuario':
        usuario = Usuario(
            id=data.get('id'),
            id_persona=data.get('id_persona'),
            id_rol=data.get('id_rol'),
            contrasena=data.get('contrasena'),
            estado=EstadoUsuario(data.get('estado', 'activo'))
        )

        if include_persona and 'persona' in data and data['persona']:
            usuario.persona = Persona.from_dict(data['persona'])

        if 'rol' in data and data['rol']:
            usuario.rol = Rol.from_dict(data['rol'])

        return usuario

    @staticmethod
    def from_registration_data(data: Dict[str, Any]) -> Tuple['Persona', 'Usuario']:
        """Crea Persona y Usuario desde datos de registro"""
        # Crear persona
        persona = Persona(
            primer_nombre=data.get('primer_nombre', ''),
            segundo_nombre=data.get('segundo_nombre'),
            primer_apellido=data.get('primer_apellido', ''),
            segundo_apellido=data.get('segundo_apellido'),
            email=data.get('email', ''),
            telefono=data.get('telefono'),
            id_rol=1  # Rol por defecto (usuario normal)
        )

        # Crear usuario
        usuario = Usuario(
            contrasena=data.get('password', ''),
            estado=EstadoUsuario.ACTIVO
        )

        return persona, usuario

    def to_dict(self, include_persona: bool = True) -> Dict[str, Any]:
        data = {
            'id': self.id,
            'id_persona': self.id_persona,
            'id_rol': self.id_rol,
            'estado': self.estado.value
        }

        if include_persona and self.persona:
            data['persona'] = self.persona.to_dict()

        if self.rol:
            data['rol'] = self.rol.to_dict()

        return data
