# Modelo Usuario
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from passlib.hash import bcrypt
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
                 nombre_rol: str = "",
                 descripcion: Optional[str] = None):
        self.id = id
        self.nombre_rol = nombre_rol
        self.descripcion = descripcion

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Rol':
        return Rol(
            id=data.get('id'),
            nombre_rol=data.get('rol', ''),
            descripcion=data.get('descripcion')
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'rol': self.nombre_rol,
            'descripcion': self.descripcion
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
                 fecha_creacion: Optional[datetime] = None,
                 rol: Optional[Rol] = None):

        self.id = id
        self.id_rol = id_rol
        self.primer_nombre = primer_nombre
        self.segundo_nombre = segundo_nombre
        self.primer_apellido = primer_apellido
        self.segundo_apellido = segundo_apellido
        self.email = email
        self.telefono = telefono
        self.fecha_creacion = fecha_creacion
        self.rol = rol

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
        persona = Persona(
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
        if 'rol' in data and data['rol']:
            persona.rol = Rol.from_dict(data['rol'])
        return persona

    def to_dict(self) -> Dict[str, Any]:
        data = {
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
        if self.rol:
            data['rol'] = self.rol.to_dict()
        return data

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
        """Establece la contraseña con hash bcrypt"""
        self.contrasena = bcrypt.hash(password)
        self.password_hash = self.contrasena

    def check_password(self, password: str) -> bool:
        """Verifica si la contraseña proporcionada coincide"""
        if self.contrasena is None:
            return False
        
        # Intentar verificar como hash primero
        try:
            return bcrypt.verify(password, self.contrasena)
        except ValueError:
            # Si falla, comparar directamente (para usuarios antiguos sin hash)
            # Esto permite compatibilidad con usuarios existentes
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
            id_rol=2  # Rol por defecto (usuario normal) - ID 2 según la BD
        )

        # Crear usuario con contraseña hasheada
        usuario = Usuario(
            estado=EstadoUsuario.ACTIVO,
            id_rol=2  # También asignar el rol al usuario
        )
        # Usar set_password para hashear la contraseña
        usuario.set_password(data.get('password', ''))

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
