# Servicio Animal
from typing import List, Optional
from datetime import datetime
from ..database.db import get_connection
from ..models.animal import Animal

class AnimalService:
    @staticmethod
    def crear_animal(animal: Animal) -> Optional[Animal]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            sql = """
                INSERT INTO animales (
                    codigo_qr, nombre, raza, genero, fecha_nacimiento,
                    peso, estado_salud, historial_vacunas, potrero_id,
                    madre_id, padre_id, fecha_registro, ultima_actualizacion
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
                )
            """
            
            values = (
                animal.codigo_qr, animal.nombre, animal.raza, animal.genero,
                animal.fecha_nacimiento, animal.peso, animal.estado_salud,
                animal.historial_vacunas, animal.potrero_id, animal.madre_id,
                animal.padre_id
            )
            
            cursor.execute(sql, values)
            conn.commit()
            
            animal.id = cursor.lastrowid
            return animal
            
        except Exception as e:
            print(f"Error al crear animal: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def obtener_animal(id: int) -> Optional[Animal]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            sql = "SELECT * FROM animales WHERE id = %s"
            cursor.execute(sql, (id,))
            
            result = cursor.fetchone()
            if result:
                return Animal.from_dict(result)
            return None
            
        except Exception as e:
            print(f"Error al obtener animal: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def obtener_todos_animales() -> List[Animal]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT * FROM animales")
            results = cursor.fetchall()
            
            return [Animal.from_dict(result) for result in results]
            
        except Exception as e:
            print(f"Error al obtener animales: {e}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def actualizar_animal(id: int, animal: Animal) -> bool:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            sql = """
                UPDATE animales SET 
                    codigo_qr = %s,
                    nombre = %s,
                    raza = %s,
                    genero = %s,
                    fecha_nacimiento = %s,
                    peso = %s,
                    estado_salud = %s,
                    historial_vacunas = %s,
                    potrero_id = %s,
                    madre_id = %s,
                    padre_id = %s,
                    ultima_actualizacion = NOW()
                WHERE id = %s
            """
            
            values = (
                animal.codigo_qr, animal.nombre, animal.raza, animal.genero,
                animal.fecha_nacimiento, animal.peso, animal.estado_salud,
                animal.historial_vacunas, animal.potrero_id, animal.madre_id,
                animal.padre_id, id
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
    def eliminar_animal(id: int) -> bool:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            sql = "DELETE FROM animales WHERE id = %s"
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
    def buscar_por_potrero(potrero_id: int) -> List[Animal]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            sql = "SELECT * FROM animales WHERE potrero_id = %s"
            cursor.execute(sql, (potrero_id,))
            results = cursor.fetchall()
            
            return [Animal.from_dict(result) for result in results]
            
        except Exception as e:
            print(f"Error al buscar animales por potrero: {e}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod 
    def buscar_por_codigo_qr(codigo_qr: str) -> Optional[Animal]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            sql = "SELECT * FROM animales WHERE codigo_qr = %s"
            cursor.execute(sql, (codigo_qr,))
            
            result = cursor.fetchone()
            if result:
                return Animal.from_dict(result)
            return None
            
        except Exception as e:
            print(f"Error al buscar animal por código QR: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()
    @staticmethod
    def crear_animal(animal: Animal) -> Optional[Animal]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            sql = """
                INSERT INTO animales (
                    codigo_qr, nombre, raza, genero, fecha_nacimiento,
                    peso, estado_salud, historial_vacunas, potrero_id,
                    madre_id, padre_id, fecha_registro, ultima_actualizacion
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
                )
            """
            
            values = (
                animal.numero_arete, animal.nombre, animal.raza, animal.genero,
                animal.fecha_nacimiento, animal.peso, animal.estado_salud,
                animal.historial_vacunas, animal.potrero_id, animal.madre_id,
                animal.padre_id
            )
            
            cursor.execute(sql, values)
            conn.commit()
            
            animal.id = cursor.lastrowid
            return animal
            
        except Exception as e:
            print(f"Error al crear animal: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def obtener_animal(id: int) -> Optional[Animal]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            sql = "SELECT * FROM animales WHERE id = %s"
            cursor.execute(sql, (id,))
            
            result = cursor.fetchone()
            if result:
                return Animal.from_dict(result)
            return None
            
        except Exception as e:
            print(f"Error al obtener animal: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def obtener_todos_animales() -> List[Animal]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT * FROM animales")
            results = cursor.fetchall()
            
            return [Animal.from_dict(result) for result in results]
            
        except Exception as e:
            print(f"Error al obtener animales: {e}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def actualizar_animal(id: int, animal: Animal) -> bool:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            sql = """
                UPDATE animales SET 
                    codigo_qr = %s,
                    nombre = %s,
                    raza = %s,
                    genero = %s,
                    fecha_nacimiento = %s,
                    peso = %s,
                    estado_salud = %s,
                    historial_vacunas = %s,
                    potrero_id = %s,
                    madre_id = %s,
                    padre_id = %s,
                    ultima_actualizacion = NOW()
                WHERE id = %s
            """
            
            values = (
                animal.codigo_qr, animal.nombre, animal.raza, animal.genero,
                animal.fecha_nacimiento, animal.peso, animal.estado_salud,
                animal.historial_vacunas, animal.potrero_id, animal.madre_id,
                animal.padre_id, id
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
    def eliminar_animal(id: int) -> bool:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            sql = "DELETE FROM animales WHERE id = %s"
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
    def buscar_por_potrero(potrero_id: int) -> List[Animal]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            sql = "SELECT * FROM animales WHERE potrero_id = %s"
            cursor.execute(sql, (potrero_id,))
            results = cursor.fetchall()
            
            return [Animal.from_dict(result) for result in results]
            
        except Exception as e:
            print(f"Error al buscar animales por potrero: {e}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod 
    def buscar_por_codigo_qr(codigo_qr: str) -> Optional[Animal]:
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            sql = "SELECT * FROM animales WHERE codigo_qr = %s"
            cursor.execute(sql, (codigo_qr,))
            
            result = cursor.fetchone()
            if result:
                return Animal.from_dict(result)
            return None
            
        except Exception as e:
            print(f"Error al buscar animal por arete: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()
