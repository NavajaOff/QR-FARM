"""Service layer for Potrero operations."""
from typing import List, Optional, Dict, Any
from mysql.connector import Error
from src.database.db import db, get_connection
from datetime import datetime

class PotreroService:
    """Service class for handling Potrero business logic."""

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        """Get all potreros."""
        conn = None
        cursor = None
        try:
            conn = get_connection()
            if conn is None:
                print("Advertencia: Base de datos no disponible, retornando lista vacía")
                return []
            cursor = conn.cursor(dictionary=True)
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
        except Exception as e:
            print(f"Error en get_all potreros service: {str(e)}")
            import traceback
            traceback.print_exc()
            raise e
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

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

        # Usar conexión directa para asegurar transacción
        conn = get_connection()
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)

            sql = """
                INSERT INTO potrero (
                    id_tipo_pasto, nombre, capacidad, hectareas, ocupacion,
                    fecha_ultimo_uso, responsable_persona_id, proxima_limpieza,
                    area, ultima_limpieza, descripcion, estado
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
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
                data.get('estado', 'disponible')
            )

            cursor.execute(sql, values)
            potrero_id = cursor.lastrowid
            print(f"Potrero INSERT ejecutado con ID: {potrero_id}")

            # Hacer commit explícito
            conn.commit()
            print(f"Commit realizado para potrero ID: {potrero_id}")

        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error en create potrero: {e}")
            raise e
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            if conn and conn is not None:
                try:
                    if conn.is_connected():
                        conn.close()
                except:
                    pass

        # Usar una nueva conexión para obtener el registro completo
        try:
            with db.get_cursor() as select_cursor:
                select_cursor.execute("""
                    SELECT p.* FROM potrero p WHERE p.id = %s
                """, (potrero_id,))
                result = select_cursor.fetchone()

                if result:
                    print(f"Potrero encontrado después del commit: {result}")
                    # Agregar el nombre del tipo de pasto
                    if result.get('id_tipo_pasto'):
                        try:
                            tipos_pasto = PotreroService.get_tipos_pasto()
                            tipo_encontrado = next((tp for tp in tipos_pasto if tp['id'] == result['id_tipo_pasto']), None)
                            result['tipo_pasto_nombre'] = tipo_encontrado['tipo_pasto'] if tipo_encontrado else 'No definido'
                        except Exception as e:
                            print(f"Error obteniendo tipo de pasto: {e}")
                            result['tipo_pasto_nombre'] = 'No definido'
                    else:
                        result['tipo_pasto_nombre'] = 'No definido'
    
                    # Agregar nombre del responsable si existe
                    if result.get('responsable_persona_id'):
                        try:
                            # Obtener nombre del responsable
                            with db.get_cursor() as resp_cursor:
                                resp_cursor.execute("""
                                    SELECT CONCAT(primer_nombre, ' ', primer_apellido) as nombre_completo
                                    FROM personas WHERE id = %s
                                """, (result['responsable_persona_id'],))
                                resp_result = resp_cursor.fetchone()
                                if resp_result:
                                    result['responsable_nombre'] = resp_result['nombre_completo']
                                else:
                                    result['responsable_nombre'] = f"Persona {result['responsable_persona_id']}"
                        except Exception as e:
                            print(f"Error obteniendo nombre del responsable: {e}")
                            result['responsable_nombre'] = f"Persona {result['responsable_persona_id']}"
                    else:
                        result['responsable_nombre'] = 'No asignado'

                    return result
                else:
                    print(f"Potrero con ID {potrero_id} no encontrado después del commit")
                    raise ValueError(f"Potrero with id {potrero_id} not found after commit")

        except Exception as e:
            print(f"Error obteniendo potrero después del commit: {e}")
            raise e

    @staticmethod
    def update(potrero_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing potrero."""
        # First check if potrero exists
        PotreroService.get_by_id(potrero_id)

        update_fields = []
        values = []

        # Procesar campos especiales para fechas y enums
        for key, value in data.items():
            if key in ['id']:
                continue

            # Convertir strings vacías a None para campos de fecha
            if key in ['proxima_limpieza', 'ultima_limpieza', 'fecha_ultimo_uso'] and value == '':
                value = None
            # Para campos de fecha que vienen como strings, mantener formato simple YYYY-MM-DD
            elif key in ['proxima_limpieza', 'ultima_limpieza', 'fecha_ultimo_uso'] and isinstance(value, str) and value:
                # Extraer solo la fecha YYYY-MM-DD, sin conversiones de zona horaria
                if 'T' in value:
                    value = value.split('T')[0]
                # Asegurar que sea formato YYYY-MM-DD
                # Si no cumple el formato esperado, mantener el valor original sin cambios
                # Esta validación se elimina porque ambos bloques hacen lo mismo (pass)
            # Para el campo estado, asegurar que sea válido para el enum
            elif key == 'estado':
                # Los valores válidos del enum son: 'disponible', 'ocupado', 'limpieza'
                valid_states = ['disponible', 'ocupado', 'limpieza']
                if value and value not in valid_states:
                    # Si no es válido, usar 'disponible' por defecto
                    value = 'disponible'
                elif not value:
                    # Si viene vacío, usar 'disponible' por defecto
                    value = 'disponible'

            update_fields.append(f"{key} = %s")
            values.append(value)

        if not update_fields:
            return PotreroService.get_by_id(potrero_id)

        values.append(potrero_id)

        print(f"Actualizando potrero {potrero_id} con campos: {update_fields}")
        print(f"Valores: {values[:-1]}")  # No mostrar el ID al final

        with db.get_cursor() as cursor:
            sql = f"""
                UPDATE potrero
                SET {', '.join(update_fields)}
                WHERE id = %s
            """
            cursor.execute(sql, values)
            print(f"SQL ejecutado: {sql}")
            print(f"Filas afectadas: {cursor.rowcount}")

            # Obtener el registro actualizado con JOIN para incluir el nombre del responsable
            cursor.execute("""
                SELECT p.*,
                       CONCAT(per.primer_nombre, ' ', COALESCE(per.segundo_nombre, ''), ' ', per.primer_apellido, ' ', COALESCE(per.segundo_apellido, '')) as responsable
                FROM potrero p
                LEFT JOIN personas per ON p.responsable_persona_id = per.id
                WHERE p.id = %s
            """, (potrero_id,))

            result = cursor.fetchone()
            if result:
                # Agregar el nombre del tipo de pasto si existe
                if result.get('id_tipo_pasto'):
                    try:
                        tipos_pasto = PotreroService.get_tipos_pasto()
                        tipo_encontrado = next((tp for tp in tipos_pasto if tp['id'] == result['id_tipo_pasto']), None)
                        result['tipo_pasto'] = tipo_encontrado['tipo_pasto'] if tipo_encontrado else 'No definido'
                    except Exception as e:
                        print(f"Error obteniendo tipo de pasto: {e}")
                        result['tipo_pasto'] = 'No definido'
                else:
                    result['tipo_pasto'] = 'No definido'

                print(f"Potrero actualizado exitosamente: {result}")
                return result
            else:
                raise ValueError(f"Potrero with id {potrero_id} not found after update")

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

            # Agregar el nombre del tipo de pasto y responsable a cada potrero
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

                # Agregar nombre del responsable si existe
                if potrero.get('responsable_persona_id'):
                    try:
                        # Obtener nombre del responsable
                        resp_conn = get_connection()
                        resp_cursor = resp_conn.cursor(dictionary=True)
                        resp_cursor.execute("""
                            SELECT CONCAT(primer_nombre, ' ', primer_apellido) as nombre_completo
                            FROM personas WHERE id = %s
                        """, (potrero['responsable_persona_id'],))
                        resp_result = resp_cursor.fetchone()
                        if resp_result and resp_result['nombre_completo']:
                            potrero['responsable_nombre'] = resp_result['nombre_completo']
                        else:
                            potrero['responsable_nombre'] = f"Persona {potrero['responsable_persona_id']}"
                        resp_cursor.close()
                        resp_conn.close()
                    except Exception as e:
                        print(f"Error obteniendo nombre del responsable para potrero {potrero['id']}: {e}")
                        potrero['responsable_nombre'] = f"Persona {potrero['responsable_persona_id']}"
                else:
                    potrero['responsable_nombre'] = 'No asignado'

                print(f"Potrero {potrero['id']}: responsable_id={potrero.get('responsable_persona_id')}, nombre={potrero.get('responsable_nombre')}")

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
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
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
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

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

                # Transformar la estructura para que coincida con lo que espera el frontend
                personas_transformadas = []
                for result in results:
                    personas_transformadas.append({
                        'id': result['id'],
                        'primer_nombre': result['primer_nombre'],
                        'segundo_nombre': result['segundo_nombre'],
                        'primer_apellido': result['primer_apellido'],
                        'segundo_apellido': result['segundo_apellido'],
                        'nombre_completo': result['nombre_completo'],
                        'nombre_persona': result['nombre_completo']  # Campo adicional para compatibilidad
                    })

                return personas_transformadas
        except Exception as e:
            print(f"Error obteniendo personas usuario: {e}")
            return []

    @staticmethod
    def get_estados_potrero() -> List[Dict[str, Any]]:
        """Get all estados de potrero desde el enum de la columna estado."""
        try:
            with db.get_cursor() as cursor:
                # Obtener los valores del enum de la columna estado
                cursor.execute("""
                    SELECT COLUMN_TYPE
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = 'potrero'
                    AND COLUMN_NAME = 'estado'
                """)
                result = cursor.fetchone()

                if result and result['COLUMN_TYPE']:
                    # Extraer valores del enum, ej: enum('disponible','ocupado','limpieza')
                    enum_str = result['COLUMN_TYPE']

                    # Extraer valores entre paréntesis
                    if '(' in enum_str and ')' in enum_str:
                        values_str = enum_str.split('(')[1].split(')')[0]
                        # Separar por comas y quitar comillas
                        valores = [v.strip("'\"") for v in values_str.split(',')]

                        # Retornar como lista de diccionarios con campos compatibles con frontend
                        return [{'id': i+1, 'estado': valor, 'nombre_estado': valor} for i, valor in enumerate(valores)]

                # Retornar lista vacía si no se puede obtener del enum
                return []
        except Exception as e:
            print(f"Error obteniendo estados del enum: {e}")
            return []

    # Método get_estados_ganado eliminado porque pertenece a GanadoService
