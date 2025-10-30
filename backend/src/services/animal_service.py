# Servicio Ganado
from typing import List, Optional
from datetime import datetime
from ..database.db import get_connection
from ..models.animal import Ganado

class GanadoService:
    @staticmethod
    def crear_ganado(ganado: Ganado) -> Optional[Ganado]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            sql = """
                INSERT INTO ganado (
                    codigo_qr, nombre, raza, fecha_nacimiento, edad,
                    sexo, peso, estado, estado_salud, id_potrero, id_persona,
                    created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
                )
            """

            values = (
                ganado.codigo_qr, ganado.nombre, ganado.raza,
                ganado.fecha_nacimiento, ganado.edad, ganado.sexo.value,
                ganado.peso, ganado.estado.value, ganado.estado_salud,
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
            print(f"Error al buscar animal por código QR: {e}")
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
            print(f"Error al obtener animal: {e}")
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
            print(f"Error al obtener animales: {e}")
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
    def obtener_estados_ganado() -> List[dict]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT id, tipo_estado FROM estado_ganado ORDER BY tipo_estado")
            results = cursor.fetchall()

            print(f"Estados de ganado obtenidos: {results}")
            return results

        except Exception as e:
            print(f"Error al obtener estados de ganado: {e}")
            # Retornar lista vacía si no hay datos
            return []
        finally:
            if 'conn' in locals():
                conn.close()
