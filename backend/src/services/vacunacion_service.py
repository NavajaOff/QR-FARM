# Servicio Vacunacion
from typing import List, Optional
from src.database.db import get_connection
from src.models.vacunacion import Vacunacion

class VacunacionService:
    @staticmethod
    def obtener_todas_vacunaciones() -> List[Vacunacion]:
        """Obtener todas las vacunaciones con información relacionada"""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT
                    v.id,
                    v.id_animal,
                    g.nombre as nombre_animal,
                    v.fecha_inicio,
                    v.fecha_fin,
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
                ORDER BY v.id DESC
            """

            cursor.execute(query)
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
    def obtener_vacunacion_por_id(id: int) -> Optional[Vacunacion]:
        """Obtener una vacunación por ID"""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT
                    v.id,
                    v.id_animal,
                    g.nombre as nombre_animal,
                    v.fecha_inicio,
                    v.fecha_fin,
                    v.fecha_aplicacion,
                    v.proxima_dosis,
                    v.responsable,
                    CONCAT(p.primer_nombre, ' ', COALESCE(p.segundo_nombre, ''), ' ', p.primer_apellido, ' ', COALESCE(p.segundo_apellido, '')) as nombre_responsable,
                    v.estado,
                    v.id_tipo_vacuna,
                    tv.nombre as nombre_tipo_vacuna
                FROM vacunacion v
                LEFT JOIN ganado g ON v.id_animal = g.id
                LEFT JOIN personas p ON v.responsable = p.id
                LEFT JOIN tipo_vacuna tv ON v.id_tipo_vacuna = tv.id
                WHERE v.id = %s
            """

            cursor.execute(query, (id,))
            row = cursor.fetchone()

            if row:
                return Vacunacion.from_dict(row)
            return None

        except Exception as e:
            print(f"Error obteniendo vacunación por ID: {str(e)}")
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
            conn = get_connection()
            cursor = conn.cursor()

            query = """
                INSERT INTO vacunacion (
                    id_animal, fecha_inicio, fecha_fin, fecha_aplicacion,
                    proxima_dosis, responsable, estado, id_tipo_vacuna
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """

            values = (
                vacunacion.id_animal,
                vacunacion.fecha_inicio,
                vacunacion.fecha_fin,
                vacunacion.fecha_aplicacion,
                vacunacion.proxima_dosis,
                vacunacion.responsable,
                vacunacion.estado.value if hasattr(vacunacion.estado, 'value') else str(vacunacion.estado),
                vacunacion.id_tipo_vacuna
            )

            cursor.execute(query, values)
            conn.commit()

            return True

        except Exception as e:
            print(f"Error creando vacunación: {str(e)}")
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals() and conn.is_connected():
                conn.close()

    @staticmethod
    def actualizar_vacunacion(id: int, vacunacion: Vacunacion) -> bool:
        """Actualizar una vacunación existente"""
        try:
            conn = get_connection()
            cursor = conn.cursor()

            query = """
                UPDATE vacunacion SET
                    id_animal = %s,
                    fecha_inicio = %s,
                    fecha_fin = %s,
                    fecha_aplicacion = %s,
                    proxima_dosis = %s,
                    responsable = %s,
                    estado = %s,
                    id_tipo_vacuna = %s
                WHERE id = %s
            """

            values = (
                vacunacion.id_animal,
                vacunacion.fecha_inicio,
                vacunacion.fecha_fin,
                vacunacion.fecha_aplicacion,
                vacunacion.proxima_dosis,
                vacunacion.responsable,
                vacunacion.estado.value if hasattr(vacunacion.estado, 'value') else str(vacunacion.estado),
                vacunacion.id_tipo_vacuna,
                id
            )

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
    def eliminar_vacunacion(id: int) -> bool:
        """Eliminar una vacunación"""
        try:
            conn = get_connection()
            cursor = conn.cursor()

            query = "DELETE FROM vacunacion WHERE id = %s"
            cursor.execute(query, (id,))
            conn.commit()

            return cursor.rowcount > 0

        except Exception as e:
            print(f"Error eliminando vacunación: {str(e)}")
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