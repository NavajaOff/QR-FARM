# Servicio Vacunacion
from typing import List, Optional
from src.database.db import get_connection
from src.models.vacunacion import Vacunacion
from src.utils.tenant import get_current_tenant_id

class VacunacionService:
    @staticmethod
    def _obtener_tenant_id() -> Optional[int]:
        """Obtiene el tenant_id del contexto actual."""
        try:
            return get_current_tenant_id()
        except Exception:
            return None
    @staticmethod
    def obtener_todas_vacunaciones(tenant_id_override: Optional[int] = None) -> List[Vacunacion]:
        """
        Obtener todas las vacunaciones con información relacionada.
        
        Args:
            tenant_id_override: Si se proporciona, filtra por este tenant
        """
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            tenant_id = tenant_id_override if tenant_id_override is not None else VacunacionService._obtener_tenant_id()
            
            query = """
                SELECT
                    v.id,
                    v.id_animal,
                    g.nombre as nombre_animal,
                    v.fecha_aplicacion,
                    v.proxima_dosis,
                    v.responsable,
                    CONCAT(p.primer_nombre, ' ', COALESCE(p.segundo_nombre, ''), ' ', p.primer_apellido, ' ', COALESCE(p.segundo_apellido, '')) as nombre_responsable,
                    v.estado,
                    v.id_tipo_vacuna,
                    tv.nombre_vacuna as nombre_tipo_vacuna
                FROM vacunacion v
                LEFT JOIN ganado g ON v.id_animal = g.id
                LEFT JOIN personas p ON v.responsable = p.id
                LEFT JOIN tipo_vacuna tv ON v.id_tipo_vacuna = tv.id
            """
            
            params = ()
            if tenant_id is not None:
                query += " WHERE v.tenant_id = %s"
                params = (tenant_id,)
            
            query += " ORDER BY v.id DESC"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            vacunaciones = []
            for row in rows:
                vacunacion = Vacunacion.from_dict(row)
                vacunaciones.append(vacunacion)

            return vacunaciones

        except Exception as e:
            print(f"Error obteniendo vacunaciones: {str(e)}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals() and conn.is_connected():
                conn.close()

    @staticmethod
    def obtener_vacunacion_por_id(id: int, tenant_id_override: Optional[int] = None) -> Optional[Vacunacion]:
        """
        Obtener una vacunación por ID.
        
        Args:
            id: ID de la vacunación
            tenant_id_override: Si se proporciona, valida que la vacunación pertenezca a este tenant
        """
        try:
            print(f"Service: Buscando vacunación con ID: {id}")
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            tenant_id = tenant_id_override if tenant_id_override is not None else VacunacionService._obtener_tenant_id()
            
            query = """
                SELECT
                    v.id,
                    v.id_animal,
                    g.nombre as nombre_animal,
                    v.fecha_aplicacion,
                    v.proxima_dosis,
                    v.responsable,
                    CONCAT(p.primer_nombre, ' ', COALESCE(p.segundo_nombre, ''), ' ', p.primer_apellido, ' ', COALESCE(p.segundo_apellido, '')) as nombre_responsable,
                    v.estado,
                    v.id_tipo_vacuna,
                    tv.nombre_vacuna as nombre_tipo_vacuna
                FROM vacunacion v
                LEFT JOIN ganado g ON v.id_animal = g.id
                LEFT JOIN personas p ON v.responsable = p.id
                LEFT JOIN tipo_vacuna tv ON v.id_tipo_vacuna = tv.id
                WHERE v.id = %s
            """
            
            params = (id,)
            if tenant_id is not None:
                query += " AND v.tenant_id = %s"
                params = (id, tenant_id)

            print(f"Service: Ejecutando query para obtener vacunación: {query} con ID: {id}")
            cursor.execute(query, params)
            row = cursor.fetchone()
            print(f"Service: Resultado de la query: {row}")

            if row:
                print(f"Service: Vacunación encontrada: {row}")
                return Vacunacion.from_dict(row)
            print(f"Service: No se encontró vacunación con ID: {id}")
            return None

        except Exception as e:
            print(f"Service: Error obteniendo vacunación por ID: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals() and conn.is_connected():
                conn.close()

    @staticmethod
    def crear_vacunacion(vacunacion: Vacunacion) -> bool:
        """Crear una nueva vacunación"""
        try:
            from datetime import timedelta
            print(f"Service: Creando vacunación con datos: {vacunacion.to_dict()}")

            # Calcular próxima dosis automáticamente (6 meses después de fecha_aplicacion)
            proxima_dosis = None
            if vacunacion.fecha_aplicacion:
                # Convertir string a datetime si es necesario
                if isinstance(vacunacion.fecha_aplicacion, str):
                    from datetime import datetime
                    vacunacion.fecha_aplicacion = datetime.fromisoformat(vacunacion.fecha_aplicacion.replace('Z', '+00:00'))
                proxima_dosis = vacunacion.fecha_aplicacion + timedelta(days=180)  # 6 meses = 180 días
                print(f"Service: Próxima dosis calculada: {proxima_dosis}")

            conn = get_connection()
            cursor = conn.cursor()

            tenant_id = VacunacionService._obtener_tenant_id()
            if tenant_id is None:
                raise ValueError("Tenant requerido para crear vacunación")

            query = """
                INSERT INTO vacunacion (
                    id_animal, fecha_aplicacion, proxima_dosis, responsable, estado, id_tipo_vacuna, tenant_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            values = (
                vacunacion.id_animal,
                vacunacion.fecha_aplicacion,
                proxima_dosis,
                vacunacion.responsable,
                vacunacion.estado.value if hasattr(vacunacion.estado, 'value') else str(vacunacion.estado),
                vacunacion.id_tipo_vacuna,
                tenant_id
            )

            print(f"Service: Ejecutando query: {query}")
            print(f"Service: Valores: {values}")
            cursor.execute(query, values)
            conn.commit()
            print(f"Service: Vacunación creada exitosamente")

            return True

        except Exception as e:
            print(f"Service: Error creando vacunación: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals() and conn.is_connected():
                conn.close()

    @staticmethod
    def actualizar_vacunacion(id: int, vacunacion: Vacunacion, tenant_id_override: Optional[int] = None) -> bool:
        """
        Actualizar una vacunación existente.
        
        Args:
            id: ID de la vacunación
            vacunacion: Objeto Vacunacion con datos actualizados
            tenant_id_override: Si se proporciona, valida que la vacunación pertenezca a este tenant
        """
        try:
            conn = get_connection()
            cursor = conn.cursor()

            tenant_id = tenant_id_override if tenant_id_override is not None else VacunacionService._obtener_tenant_id()
            
            query = """
                UPDATE vacunacion SET
                    id_animal = %s,
                    fecha_aplicacion = %s,
                    proxima_dosis = %s,
                    responsable = %s,
                    estado = %s,
                    id_tipo_vacuna = %s
                WHERE id = %s
            """
            
            values_list = [
                vacunacion.id_animal,
                vacunacion.fecha_aplicacion,
                vacunacion.proxima_dosis,
                vacunacion.responsable,
                vacunacion.estado.value if hasattr(vacunacion.estado, 'value') else str(vacunacion.estado),
                vacunacion.id_tipo_vacuna,
                id
            ]
            
            if tenant_id is not None:
                query += " AND tenant_id = %s"
                values_list.append(tenant_id)
            
            values = tuple(values_list)

            cursor.execute(query, values)
            conn.commit()

            return cursor.rowcount > 0

        except Exception as e:
            print(f"Error actualizando vacunación: {str(e)}")
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals() and conn.is_connected():
                conn.close()

    @staticmethod
    def eliminar_vacunacion(id: int, tenant_id_override: Optional[int] = None) -> bool:
        """
        Eliminar una vacunación.
        
        Args:
            id: ID de la vacunación
            tenant_id_override: Si se proporciona, valida que la vacunación pertenezca a este tenant
        """
        try:
            print(f"Service: Intentando eliminar vacunación con ID: {id}")
            conn = get_connection()
            cursor = conn.cursor()
            print(f"Service: Conexión a BD obtenida")

            tenant_id = tenant_id_override if tenant_id_override is not None else VacunacionService._obtener_tenant_id()
            
            query = "DELETE FROM vacunacion WHERE id = %s"
            params = (id,)
            if tenant_id is not None:
                query += " AND tenant_id = %s"
                params = (id, tenant_id)
            
            print(f"Service: Ejecutando query: {query} con ID: {id}")
            cursor.execute(query, params)
            conn.commit()
            print(f"Service: Query ejecutada, rowcount: {cursor.rowcount}")

            result = cursor.rowcount > 0
            print(f"Service: Resultado de eliminación: {result}")
            return result

        except Exception as e:
            print(f"Service: Error eliminando vacunación: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals() and conn.is_connected():
                conn.close()

    @staticmethod
    def obtener_tipos_vacuna() -> List[dict]:
        """Obtener lista de tipos de vacuna"""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            query = "SELECT id, nombre_vacuna as nombre FROM tipo_vacuna ORDER BY nombre_vacuna"
            cursor.execute(query)
            rows = cursor.fetchall()

            return rows

        except Exception as e:
            print(f"Error obteniendo tipos de vacuna: {str(e)}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals() and conn.is_connected():
                conn.close()