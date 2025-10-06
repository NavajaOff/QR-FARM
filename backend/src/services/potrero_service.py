"""Service layer for Potrero operations."""
from typing import List, Optional, Dict, Any
from mysql.connector import Error
from src.database.db import db
from datetime import datetime

class PotreroService:
    """Service class for handling Potrero business logic."""

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """Get all potreros."""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM potrero 
                WHERE deleted_at IS NULL 
                ORDER BY created_at DESC
            """)
            return cursor.fetchall()

    @staticmethod
    def get_by_id(potrero_id: int) -> Optional[Dict[str, Any]]:
        """Get potrero by ID."""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM potrero 
                WHERE id = %s AND deleted_at IS NULL
            """, (potrero_id,))
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"Potrero with id {potrero_id} not found")
            return result

    @staticmethod
    def create(data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new potrero."""
        required_fields = ['nombre']
        for field in required_fields:
            if not data.get(field):
                raise ValueError(f"Field {field} is required")

        with db.get_cursor() as cursor:
            sql = """
                INSERT INTO potrero (
                    nombre, estado, capacidad, ocupacion, tipo_pasto,
                    fecha_ultimo_uso, responsable_persona_id, proxima_limpieza,
                    area, ultima_limpieza, ubicacion, descripcion,
                    propietario_persona_id, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            values = (
                data.get('nombre'),
                data.get('estado', 'disponible'),
                data.get('capacidad'),
                data.get('ocupacion', 0),
                data.get('tipo_pasto'),
                data.get('fecha_ultimo_uso'),
                data.get('responsable_persona_id'),
                data.get('proxima_limpieza'),
                data.get('area'),
                data.get('ultima_limpieza'),
                data.get('ubicacion'),
                data.get('descripcion'),
                data.get('propietario_persona_id'),
                datetime.now(),
                datetime.now()
            )
            cursor.execute(sql, values)
            potrero_id = cursor.lastrowid
            return PotreroService.get_by_id(potrero_id)

    @staticmethod
    def update(potrero_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing potrero."""
        # First check if potrero exists
        PotreroService.get_by_id(potrero_id)

        update_fields = []
        values = []
        for key, value in data.items():
            if key in ['created_at', 'updated_at', 'deleted_at', 'id']:
                continue
            update_fields.append(f"{key} = %s")
            values.append(value)

        if not update_fields:
            return PotreroService.get_by_id(potrero_id)

        update_fields.append("updated_at = %s")
        values.append(datetime.now())
        values.append(potrero_id)

        with db.get_cursor() as cursor:
            sql = f"""
                UPDATE potrero 
                SET {', '.join(update_fields)}
                WHERE id = %s AND deleted_at IS NULL
            """
            cursor.execute(sql, values)
            return PotreroService.get_by_id(potrero_id)

    @staticmethod
    def delete(potrero_id: int) -> bool:
        """Soft delete potrero by ID."""
        # First check if potrero exists
        PotreroService.get_by_id(potrero_id)

        with db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE potrero 
                SET deleted_at = %s 
                WHERE id = %s AND deleted_at IS NULL
            """, (datetime.now(), potrero_id))
            return True

    @staticmethod
    def get_by_estado(estado: str) -> List[Dict[str, Any]]:
        """Get potreros by estado."""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM potrero 
                WHERE estado = %s AND deleted_at IS NULL 
                ORDER BY created_at DESC
            """, (estado,))
            return cursor.fetchall()

    @staticmethod
    def actualizar_ocupacion(potrero_id: int, delta: int) -> Dict[str, Any]:
        """Update ocupacion of potrero."""
        potrero = PotreroService.get_by_id(potrero_id)
        nueva_ocupacion = potrero['ocupacion'] + delta
        
        if nueva_ocupacion < 0:
            raise ValueError("La ocupación no puede ser negativa")
        if potrero['capacidad'] and nueva_ocupacion > potrero['capacidad']:
            raise ValueError("La ocupación no puede superar la capacidad")
        
        with db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE potrero 
                SET ocupacion = %s, updated_at = %s
                WHERE id = %s AND deleted_at IS NULL
            """, (nueva_ocupacion, datetime.now(), potrero_id))
            return PotreroService.get_by_id(potrero_id)
