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
                SELECT p.*
                FROM potrero p
                ORDER BY p.id DESC
            """)
            potreros = cursor.fetchall()

            # Agregar el nombre del tipo de pasto a cada potrero
            for potrero in potreros:
                if potrero.get('id_tipo_pasto'):
                    try:
                        tipos_pasto = PotreroService.get_tipos_pasto()
                        tipo_encontrado = next((tp for tp in tipos_pasto if tp['id'] == potrero['id_tipo_pasto']), None)
                        potrero['tipo_pasto_nombre'] = tipo_encontrado['tipo_pasto'] if tipo_encontrado else 'No definido'
                    except Exception:
                        potrero['tipo_pasto_nombre'] = 'No definido'
                else:
                    potrero['tipo_pasto_nombre'] = 'No definido'

            return potreros

    @staticmethod
    def get_by_id(potrero_id: int) -> Optional[Dict[str, Any]]:
        """Get potrero by ID."""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT p.*
                FROM potrero p
                WHERE p.id = %s
            """, (potrero_id,))
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"Potrero with id {potrero_id} not found")

            # Agregar el nombre del tipo de pasto
            if result.get('id_tipo_pasto'):
                try:
                    tipos_pasto = PotreroService.get_tipos_pasto()
                    tipo_encontrado = next((tp for tp in tipos_pasto if tp['id'] == result['id_tipo_pasto']), None)
                    result['tipo_pasto_nombre'] = tipo_encontrado['tipo_pasto'] if tipo_encontrado else 'No definido'
                except Exception:
                    result['tipo_pasto_nombre'] = 'No definido'
            else:
                result['tipo_pasto_nombre'] = 'No definido'

            return result

    @staticmethod
    def create(data):
        """Create new potrero."""
        # Generar nombre automático si no se proporciona
        nombre = data.get('nombre')
        if nombre is None:
            with db.get_cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM potrero")
                result = cursor.fetchone()
                numero = result['COUNT(*)'] + 1
                nombre = f"Potrero {numero}"

        # Establecer fecha de último uso como la fecha actual al crear
        from datetime import datetime
        fecha_ultimo_uso = datetime.now().date().isoformat()

        with db.get_cursor() as cursor:
            sql = """
                INSERT INTO potrero (
                    id_tipo_pasto, nombre, capacidad, hectareas, ocupacion,
                    fecha_ultimo_uso, responsable_persona_id, proxima_limpieza,
                    area, ultima_limpieza, descripcion, propietario_persona_id, estado
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            values = (
                data.get('id_tipo_pasto'),
                nombre,
                data.get('capacidad'),
                data.get('hectareas'),
                data.get('ocupacion', 0),
                fecha_ultimo_uso,
                data.get('responsable_persona_id'),
                data.get('proxima_limpieza'),
                data.get('area'),
                data.get('ultima_limpieza'),
                data.get('descripcion'),
                data.get('propietario_persona_id'),
                data.get('estado', 'disponible')
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
            if key in ['id']:
                continue
            update_fields.append(f"{key} = %s")
            values.append(value)

        if not update_fields:
            return PotreroService.get_by_id(potrero_id)

        values.append(potrero_id)

        with db.get_cursor() as cursor:
            sql = f"""
                UPDATE potrero
                SET {', '.join(update_fields)}
                WHERE id = %s
            """
            cursor.execute(sql, values)
            return PotreroService.get_by_id(potrero_id)

    @staticmethod
    def delete(potrero_id: int) -> bool:
        """Delete potrero by ID."""
        # First check if potrero exists
        PotreroService.get_by_id(potrero_id)

        with db.get_cursor() as cursor:
            cursor.execute("""
                DELETE FROM potrero
                WHERE id = %s
            """, (potrero_id,))
            return True

    @staticmethod
    def get_by_estado(estado: str) -> List[Dict[str, Any]]:
        """Get potreros by estado."""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT p.*
                FROM potrero p
                WHERE p.estado = %s
                ORDER BY p.id DESC
            """, (estado,))
            potreros = cursor.fetchall()

            # Agregar el nombre del tipo de pasto a cada potrero
            for potrero in potreros:
                if potrero.get('id_tipo_pasto'):
                    try:
                        tipos_pasto = PotreroService.get_tipos_pasto()
                        tipo_encontrado = next((tp for tp in tipos_pasto if tp['id'] == potrero['id_tipo_pasto']), None)
                        potrero['tipo_pasto_nombre'] = tipo_encontrado['tipo_pasto'] if tipo_encontrado else 'No definido'
                    except Exception:
                        potrero['tipo_pasto_nombre'] = 'No definido'
                else:
                    potrero['tipo_pasto_nombre'] = 'No definido'

            return potreros

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
                SET ocupacion = %s
                WHERE id = %s
            """, (nueva_ocupacion, potrero_id))
            return PotreroService.get_by_id(potrero_id)

    @staticmethod
    def get_tipos_pasto() -> List[Dict[str, Any]]:
        """Get all tipos de pasto."""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT id, tipo_pasto FROM tipo_pasto
                    ORDER BY tipo_pasto
                """)
                results = cursor.fetchall()
                # Los resultados ya son diccionarios
                return results
        except Exception as e:
            print(f"Error obteniendo tipos de pasto: {e}")
            return []

    @staticmethod
    def get_personas_usuario() -> List[Dict[str, Any]]:
        """Get all personas with rol usuario."""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT p.id, p.primer_nombre, p.segundo_nombre, p.primer_apellido, p.segundo_apellido,
                           CONCAT(p.primer_nombre, ' ', p.primer_apellido) as nombre_completo
                    FROM personas p
                    JOIN usuarios u ON p.id = u.id_persona
                    WHERE u.estado = 'activo'
                    ORDER BY p.primer_apellido, p.primer_nombre
                """)
                results = cursor.fetchall()
                # Los resultados ya son diccionarios cuando dictionary=True
                return results
        except Exception as e:
            print(f"Error obteniendo personas usuario: {e}")
            return []

    @staticmethod
    def get_estados_potrero() -> List[Dict[str, Any]]:
        """Get all estados de potrero desde el enum de la BD."""
        try:
            with db.get_cursor() as cursor:
                # Obtener los valores del enum de la columna estado
                cursor.execute("""
                    SELECT COLUMN_TYPE
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = 'gestion_ganadera'
                    AND TABLE_NAME = 'potrero'
                    AND COLUMN_NAME = 'estado'
                """)
                result = cursor.fetchone()

                if result and result['COLUMN_TYPE']:
                    # Extraer valores del enum, ej: enum('disponible','ocupado','limpieza')
                    enum_str = result['COLUMN_TYPE']
                    print(f"Enum string: {enum_str}")

                    # Extraer valores entre paréntesis
                    if '(' in enum_str and ')' in enum_str:
                        values_str = enum_str.split('(')[1].split(')')[0]
                        # Separar por comas y quitar comillas
                        valores = [v.strip("'\"") for v in values_str.split(',')]
                        print(f"Valores extraídos: {valores}")

                        # Retornar como lista de diccionarios
                        return [{'id': i+1, 'estado': valor} for i, valor in enumerate(valores)]
                    else:
                        print("No se encontraron paréntesis en el enum")
                else:
                    print("No se encontró COLUMN_TYPE")

                # Fallback si no se puede obtener del enum
                return [
                    {'id': 1, 'estado': 'disponible'},
                    {'id': 2, 'estado': 'ocupado'},
                    {'id': 3, 'estado': 'limpieza'}
                ]
        except Exception as e:
            print(f"Error obteniendo estados del enum: {e}")
            import traceback
            traceback.print_exc()
            # Fallback
            return [
                {'id': 1, 'estado': 'disponible'},
                {'id': 2, 'estado': 'ocupado'},
                {'id': 3, 'estado': 'limpieza'}
            ]

    @staticmethod
    def get_estados_ganado() -> List[Dict[str, Any]]:
        """Get all estados de ganado."""
        # Retornar estados del enum EstadoGanado
        return [
            {'id': 1, 'estado': 'activo'},
            {'id': 2, 'estado': 'vendido'},
            {'id': 3, 'estado': 'muerto'},
            {'id': 4, 'estado': 'en_tratamiento'}
        ]
