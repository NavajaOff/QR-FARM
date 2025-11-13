# Servicio Ganado
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from ..database.db import get_connection
from ..models.animal import Ganado, EstadoGanado

class GanadoService:
    @staticmethod
    def _to_iso_string(value: Any) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, str):
            return value
        return None

    @staticmethod
    def _calcular_edad(valor: Any) -> Optional[int]:
        referencia = None
        if isinstance(valor, datetime):
            referencia = valor.date()
        elif isinstance(valor, date):
            referencia = valor
        elif isinstance(valor, str):
            try:
                referencia = datetime.fromisoformat(valor.replace('Z', '')).date()
            except ValueError:
                try:
                    referencia = datetime.strptime(valor.split('T')[0], '%Y-%m-%d').date()
                except ValueError:
                    return None
        else:
            return None

        hoy = date.today()
        edad = hoy.year - referencia.year - ((hoy.month, hoy.day) < (referencia.month, referencia.day))
        return edad if edad >= 0 else None

    @staticmethod
    def crear_ganado(ganado: Ganado) -> Optional[Ganado]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            sql = """
                INSERT INTO ganado (
                    nombre, raza, fecha_nacimiento,
                    sexo, peso, id_estado, id_potrero, id_persona
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s
                )
            """

            # Convertir estado a ID numérico basado en el enum EstadoGanado
            estado_id = None
            if ganado.estado == EstadoGanado.ACTIVO:
                estado_id = 1
            elif ganado.estado == EstadoGanado.SALUDABLE:
                estado_id = 2
            elif ganado.estado == EstadoGanado.REVISION:
                estado_id = 3
            elif ganado.estado == EstadoGanado.VENDIDO:
                estado_id = 4
            elif ganado.estado == EstadoGanado.ENFERMO:
                estado_id = 5
            else:
                # Si no coincide, usar default
                estado_id = 1

            # Convertir fecha_nacimiento a string si es date object
            fecha_nac = ganado.fecha_nacimiento
            if fecha_nac and hasattr(fecha_nac, 'isoformat'):
                fecha_nac = fecha_nac.isoformat()
            elif isinstance(fecha_nac, str):
                # Si ya es string, mantenerlo
                pass
            else:
                fecha_nac = None

            values = (
                ganado.nombre, ganado.raza,
                fecha_nac, ganado.sexo.value,
                ganado.peso, estado_id,
                ganado.id_potrero, ganado.id_persona
            )

            cursor.execute(sql, values)
            conn.commit()

            ganado.id = cursor.lastrowid
            return ganado

        except Exception as e:
            print(f"Error al crear animal: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def obtener_ganado(id: int) -> Optional[Ganado]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            sql = "SELECT * FROM ganado WHERE id = %s"
            cursor.execute(sql, (id,))

            result = cursor.fetchone()
            if result:
                return Ganado.from_dict(result)
            return None

        except Exception as e:
            print(f"Error al obtener ganado: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def obtener_todos_ganados() -> List[Ganado]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT * FROM ganado")
            results = cursor.fetchall()

            return [Ganado.from_dict(result) for result in results]

        except Exception as e:
            print(f"Error al obtener ganados: {e}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def actualizar_ganado(id: int, ganado: Ganado) -> bool:
        try:
            conn = get_connection()
            cursor = conn.cursor()

            sql = """
                UPDATE ganado SET
                    codigo_qr = %s,
                    nombre = %s,
                    raza = %s,
                    fecha_nacimiento = %s,
                    edad = %s,
                    sexo = %s,
                    peso = %s,
                    estado = %s,
                    estado_salud = %s,
                    id_potrero = %s,
                    id_persona = %s,
                    updated_at = NOW()
                WHERE id = %s
            """

            values = (
                ganado.codigo_qr, ganado.nombre, ganado.raza,
                ganado.fecha_nacimiento, ganado.edad, ganado.sexo.value,
                ganado.peso, ganado.estado.value, ganado.estado_salud,
                ganado.id_potrero, ganado.id_persona, id
            )

            cursor.execute(sql, values)
            conn.commit()

            return cursor.rowcount > 0

        except Exception as e:
            print(f"Error al actualizar ganado: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def eliminar_ganado(id: int) -> bool:
        try:
            conn = get_connection()
            cursor = conn.cursor()

            sql = "DELETE FROM ganado WHERE id = %s"
            cursor.execute(sql, (id,))
            conn.commit()

            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Error al eliminar animal: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def buscar_por_potrero(potrero_id: int) -> List[Ganado]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            sql = "SELECT * FROM ganado WHERE id_potrero = %s"
            cursor.execute(sql, (potrero_id,))
            results = cursor.fetchall()

            return [Ganado.from_dict(result) for result in results]
            
        except Exception as e:
            print(f"Error al buscar animales por potrero: {e}")
            return []
        finally:
            if 'conn' in locals() and conn is not None:
                conn.close()

    @staticmethod
    def buscar_por_codigo_qr(codigo_qr: str) -> Optional[Ganado]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            sql = "SELECT * FROM ganado WHERE codigo_qr = %s"
            cursor.execute(sql, (codigo_qr,))

            result = cursor.fetchone()
            if result:
                return Ganado.from_dict(result)
            return None
            
        except Exception as e:
            print(f"Error al buscar animal por código QR: {e}")
            return None
        finally:
            if 'conn' in locals() and conn is not None:
                conn.close()

    @staticmethod
    def obtener_ganado(id: int) -> Optional[Ganado]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT g.*,
                       eg.tipo_estado as estado_tipo,
                       p.nombre as potrero_nombre,
                       CONCAT(per.primer_nombre, ' ', COALESCE(per.segundo_nombre, ''), ' ', per.primer_apellido, ' ', COALESCE(per.segundo_apellido, '')) as persona_nombre,
                       per.primer_nombre as persona_primer_nombre,
                       per.primer_apellido as persona_primer_apellido,
                       qr.codigo_qr
                FROM ganado g
                LEFT JOIN estado_ganado eg ON g.id_estado = eg.id
                LEFT JOIN potrero p ON g.id_potrero = p.id
                LEFT JOIN personas per ON g.id_persona = per.id
                LEFT JOIN qr ON g.id = qr.id_ganado
                WHERE g.id = %s
            """, (id,))

            result = cursor.fetchone()
            if result:
                return Ganado.from_dict(result)
            return None

        except Exception as e:
            print(f"Error al obtener ganado {id}: {e}")
            return None
        finally:
            if 'conn' in locals() and conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

    @staticmethod
    def obtener_todos_ganados() -> List[Ganado]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT g.*,
                       eg.tipo_estado as estado_tipo,
                       p.nombre as potrero_nombre,
                       CONCAT(per.primer_nombre, ' ', COALESCE(per.segundo_nombre, ''), ' ', per.primer_apellido, ' ', COALESCE(per.segundo_apellido, '')) as persona_nombre,
                       per.primer_nombre as persona_primer_nombre,
                       per.primer_apellido as persona_primer_apellido,
                       qr.codigo_qr
                FROM ganado g
                LEFT JOIN estado_ganado eg ON g.id_estado = eg.id
                LEFT JOIN potrero p ON g.id_potrero = p.id
                LEFT JOIN personas per ON g.id_persona = per.id
                LEFT JOIN qr ON g.id = qr.id_ganado
                ORDER BY g.id DESC
                LIMIT 50
            """)
            results = cursor.fetchall()

            # Crear objetos Ganado con el estado_tipo incluido
            ganados = []
            for result in results:
                # Agregar estado_tipo al diccionario antes de crear el objeto
                result_copy = result.copy()
                result_copy['estado_tipo'] = result.get('estado_tipo')
                ganado = Ganado.from_dict(result_copy)
                ganados.append(ganado)

            return ganados

        except Exception as e:
            print(f"Error al obtener animales: {e}")
            return []
        finally:
            if 'conn' in locals() and conn is not None:
                conn.close()

    @staticmethod
    def _mapear_estado_a_id(estado: EstadoGanado) -> int:
        """Mapea un estado del enum EstadoGanado a su ID en la base de datos."""
        estado_mapping = {
            EstadoGanado.ACTIVO: 1,
            EstadoGanado.SALUDABLE: 2,
            EstadoGanado.REVISION: 3,
            EstadoGanado.VENDIDO: 4,
            EstadoGanado.ENFERMO: 5
        }
        return estado_mapping.get(estado, 1)  # Default: activo

    @staticmethod
    def _obtener_estado_id_desde_db(estado_value: str) -> Optional[int]:
        """Obtiene el ID del estado desde la base de datos."""
        try:
            conn_temp = get_connection()
            cursor_temp = conn_temp.cursor()
            cursor_temp.execute("SELECT id FROM estado_ganado WHERE tipo_estado = %s", (estado_value,))
            result = cursor_temp.fetchone()
            cursor_temp.close()
            conn_temp.close()
            return result[0] if result else None
        except Exception as e:
            print(f"Error obteniendo ID de estado: {e}")
            return None

    @staticmethod
    def _convertir_fecha_nacimiento(fecha_nac):
        """Convierte la fecha de nacimiento al formato adecuado para la BD."""
        if fecha_nac and hasattr(fecha_nac, 'isoformat'):
            return fecha_nac.isoformat()
        elif isinstance(fecha_nac, str):
            return fecha_nac  # Ya es string, mantener como está
        else:
            return None

    @staticmethod
    def actualizar_ganado(id: int, ganado: Ganado) -> bool:
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Obtener el ID del estado
            estado_id = GanadoService._obtener_estado_id_desde_db(ganado.estado.value)
            if estado_id is None:
                estado_id = GanadoService._mapear_estado_a_id(ganado.estado)

            # Convertir fecha de nacimiento
            fecha_nac = GanadoService._convertir_fecha_nacimiento(ganado.fecha_nacimiento)

            sql = """
                UPDATE ganado SET
                    nombre = %s,
                    raza = %s,
                    fecha_nacimiento = %s,
                    sexo = %s,
                    peso = %s,
                    id_estado = %s,
                    id_potrero = %s,
                    id_persona = %s
                WHERE id = %s
            """

            values = (
                ganado.nombre, ganado.raza,
                fecha_nac, ganado.sexo.value,
                ganado.peso, estado_id,
                ganado.id_potrero, ganado.id_persona, id
            )

            cursor.execute(sql, values)
            conn.commit()

            return cursor.rowcount > 0

        except Exception as e:
            print(f"Error al actualizar animal: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def eliminar_ganado(id: int) -> bool:
        try:
            conn = get_connection()
            cursor = conn.cursor()

            sql = "DELETE FROM ganado WHERE id = %s"
            cursor.execute(sql, (id,))
            conn.commit()

            return cursor.rowcount > 0

        except Exception as e:
            print(f"Error al eliminar ganado: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def buscar_por_potrero(potrero_id: int) -> List[Ganado]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            sql = "SELECT * FROM ganado WHERE id_potrero = %s"
            cursor.execute(sql, (potrero_id,))
            results = cursor.fetchall()

            return [Ganado.from_dict(result) for result in results]

        except Exception as e:
            print(f"Error al buscar ganados por potrero: {e}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def buscar_por_codigo_qr(codigo_qr: str) -> Optional[Ganado]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            sql = "SELECT * FROM ganado WHERE codigo_qr = %s"
            cursor.execute(sql, (codigo_qr,))

            result = cursor.fetchone()
            if result:
                return Ganado.from_dict(result)
            return None

        except Exception as e:
            print(f"Error al buscar ganado por código QR: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def obtener_ganado_detallado(identifier: Union[int, str]) -> Optional[Dict[str, Any]]:
        from ..database.db import get_connection

        connection = get_connection()
        if connection is None:
            print("No se pudo obtener conexión a la base de datos.")
            return None

        try:
            with connection.cursor(dictionary=True) as cursor:
                sql = """
                    SELECT
                        g.id,
                        g.nombre,
                        g.raza,
                        g.fecha_nacimiento,
                        g.sexo,
                        g.peso,
                        g.id_potrero,
                        g.id_persona,
                        g.id_estado,
                        q.codigo_qr,
                        p.nombre AS potrero_nombre,
                        per.telefono AS propietario_telefono,
                        CONCAT_WS(' ', per.primer_nombre, per.segundo_nombre, per.primer_apellido, per.segundo_apellido) AS propietario_nombre
                    FROM gestion_ganadera.ganado g
                    LEFT JOIN gestion_ganadera.qr q ON q.id_ganado = g.id
                    LEFT JOIN gestion_ganadera.potrero p ON p.id = g.id_potrero
                    LEFT JOIN gestion_ganadera.personas per ON per.id = g.id_persona
                    WHERE g.id = %s OR q.codigo_qr = %s
                    LIMIT 1;
                """
                cursor.execute(sql, (identifier, identifier))
                ganado = cursor.fetchone()
                if not ganado:
                    return None
                return ganado
        except Exception as ex:
            print(f"Error en obtener_ganado_detallado: {ex}")
            return None
        finally:
            try:
                connection.close()
            except Exception:
                pass

    @staticmethod
    def obtener_estados_ganado() -> List[dict]:
        try:
            conn = get_connection()
            if conn is None:
                print("Advertencia: Base de datos no disponible, retornando lista vacía")
                return []
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT id, tipo_estado FROM estado_ganado ORDER BY tipo_estado")
            results = cursor.fetchall()

            # Transformar la estructura para que coincida con lo que espera el frontend
            estados_transformados = []
            for result in results:
                estados_transformados.append({
                    'id': result['id'],
                    'estado': result['tipo_estado'],  # Cambiar 'tipo_estado' a 'estado'
                    'nombre_estado': result['tipo_estado']  # Agregar campo adicional
                })

            print(f"Estados de ganado obtenidos y transformados: {estados_transformados}")
            return estados_transformados

        except Exception as e:
            print(f"Error al obtener estados de ganado: {e}")
            # Retornar lista vacía si hay error
            return []
        finally:
            if 'conn' in locals() and conn is not None:
                conn.close()
