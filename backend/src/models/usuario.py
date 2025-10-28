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
                 contraseña: Optional[str] = None,
                 estado: EstadoUsuario = EstadoUsuario.ACTIVO,
                 persona: Optional[Persona] = None,
                 rol: Optional[Rol] = None):

        self.id = id
        self.id_persona = id_persona
        self.id_rol = id_rol
        self.contraseña = contraseña
        self.estado = estado
        self.persona = persona
        self.rol = rol

        # Alias para compatibilidad
        self.password_hash = self.contraseña

    @property
    def nombre_completo(self) -> str:
        """Retorna el nombre completo del usuario basado en la persona asociada"""
        if self.persona:
            return self.persona.nombre_completo
        return ""

    def set_password(self, password: str) -> None:
        """Establece la contraseña (sin hash, según nueva estructura BD)"""
        self.contraseña = password

    def check_password(self, password: str) -> bool:
        """Verifica si la contraseña proporcionada coincide"""
        if self.contraseña is None:
            return False
        return self.contraseña == password

    @staticmethod
    def from_dict(data: Dict[str, Any], include_persona: bool = True) -> 'Usuario':
        usuario = Usuario(
            id=data.get('id'),
            id_persona=data.get('id_persona'),
            id_rol=data.get('id_rol'),
            contraseña=data.get('contraseña'),
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
            contraseña=data.get('password', ''),
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
