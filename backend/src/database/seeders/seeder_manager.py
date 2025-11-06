#!/usr/bin/env python3
"""
Gestor de Seeders para QR-FARM
Inserta datos base necesarios para el funcionamiento del sistema
"""

import sys
import os
from datetime import datetime

# Agregar el directorio backend al path para importar módulos
backend_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, backend_path)

from src.database.db import get_connection
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class SeederManager:
    """Gestor principal de seeders del sistema"""
    
    def __init__(self):
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Establece conexión con la base de datos"""
        try:
            self.conn = get_connection()
            self.cursor = self.conn.cursor(dictionary=True)
            print("✅ Conexión establecida con la base de datos")
            return True
        except Exception as e:
            print(f"❌ Error al conectar con la base de datos: {str(e)}")
            return False
    
    def disconnect(self):
        """Cierra la conexión con la base de datos"""
        if self.cursor:
            self.cursor.close()
        if self.conn and self.conn.is_connected():
            self.conn.close()
            print("✅ Conexión cerrada")
    
    def seed_roles(self):
        """Inserta los roles básicos del sistema"""
        print("\n📝 Insertando roles...")
        
        roles = [
            (1, 'admin', 'Administrador del sistema con acceso total'),
            (2, 'user', 'Usuario regular con acceso limitado'),
            (3, 'veterinario', 'Veterinario con acceso a información médica'),
            (4, 'supervisor', 'Supervisor con acceso a reportes')
        ]
        
        try:
            # Verificar si ya existen roles
            self.cursor.execute("SELECT COUNT(*) as count FROM roles")
            count = self.cursor.fetchone()['count']
            
            if count == 0:
                query = "INSERT INTO roles (id, rol, descripcion) VALUES (%s, %s, %s)"
                self.cursor.executemany(query, roles)
                self.conn.commit()
                print(f"   ✅ {len(roles)} roles insertados correctamente")
            else:
                print(f"   ℹ️ Ya existen {count} roles en la base de datos")
                
        except Exception as e:
            print(f"   ❌ Error al insertar roles: {str(e)}")
            self.conn.rollback()
    
    def seed_tipos_pasto(self):
        """Inserta los tipos de pasto disponibles"""
        print("\n🌱 Insertando tipos de pasto...")
        
        tipos_pasto = [
            (1, 'Brachiaria', 'Pasto resistente ideal para ganado bovino'),
            (2, 'Estrella', 'Pasto de rápido crecimiento y alta palatabilidad'),
            (3, 'Guinea', 'Pasto nutritivo para zonas tropicales'),
            (4, 'Kikuyo', 'Pasto para climas fríos'),
            (5, 'Angleton', 'Pasto resistente a la sequía')
        ]
        
        try:
            # Verificar si ya existen tipos de pasto
            self.cursor.execute("SELECT COUNT(*) as count FROM tipo_pasto")
            count = self.cursor.fetchone()['count']
            
            if count == 0:
                query = "INSERT INTO tipo_pasto (id, nombre, descripcion) VALUES (%s, %s, %s)"
                self.cursor.executemany(query, tipos_pasto)
                self.conn.commit()
                print(f"   ✅ {len(tipos_pasto)} tipos de pasto insertados correctamente")
            else:
                print(f"   ℹ️ Ya existen {count} tipos de pasto en la base de datos")
                
        except Exception as e:
            print(f"   ❌ Error al insertar tipos de pasto: {str(e)}")
            self.conn.rollback()
    
    def seed_tipos_vacuna(self):
        """Inserta los tipos de vacunas disponibles"""
        print("\n💉 Insertando tipos de vacunas...")
        
        tipos_vacuna = [
            ('Fiebre Aftosa', 'Vacuna obligatoria contra la fiebre aftosa', 6),
            ('Carbunco', 'Vacuna contra el carbunco bacteridiano', 12),
            ('Brucelosis', 'Vacuna contra la brucelosis bovina', 0),
            ('Rabia', 'Vacuna contra la rabia', 12),
            ('Leptospirosis', 'Vacuna contra la leptospirosis', 6),
            ('IBR', 'Vacuna contra la rinotraqueitis infecciosa bovina', 12),
            ('DVB', 'Vacuna contra la diarrea viral bovina', 12),
            ('Clostridiales', 'Vacuna contra enfermedades clostridiales', 6)
        ]
        
        try:
            # Verificar si ya existen tipos de vacuna
            self.cursor.execute("SELECT COUNT(*) as count FROM tipo_vacuna")
            count = self.cursor.fetchone()['count']
            
            if count == 0:
                query = "INSERT INTO tipo_vacuna (nombre, descripcion, frecuencia_meses) VALUES (%s, %s, %s)"
                self.cursor.executemany(query, tipos_vacuna)
                self.conn.commit()
                print(f"   ✅ {len(tipos_vacuna)} tipos de vacuna insertados correctamente")
            else:
                print(f"   ℹ️ Ya existen {count} tipos de vacuna en la base de datos")
                
        except Exception as e:
            print(f"   ❌ Error al insertar tipos de vacuna: {str(e)}")
            self.conn.rollback()
    
    def seed_estados_ganado(self):
        """Inserta los estados posibles del ganado"""
        print("\n🐄 Insertando estados del ganado...")
        
        # Nota: Esta tabla podría no existir en la estructura actual
        # Se incluye como ejemplo según el prompt original
        try:
            # Verificar si la tabla existe
            self.cursor.execute("""
                SELECT COUNT(*) as count 
                FROM information_schema.tables 
                WHERE table_schema = %s 
                AND table_name = 'estado_ganado'
            """, (os.getenv('DB_NAME', 'gestion_ganadera'),))
            
            table_exists = self.cursor.fetchone()['count'] > 0
            
            if table_exists:
                estados = [
                    ('Sano', 'Animal en buen estado de salud'),
                    ('Enfermo', 'Animal con problemas de salud'),
                    ('En tratamiento', 'Animal recibiendo tratamiento médico'),
                    ('En cuarentena', 'Animal en período de observación'),
                    ('Recuperación', 'Animal en proceso de recuperación'),
                    ('Preñada', 'Vaca en estado de gestación')
                ]
                
                self.cursor.execute("SELECT COUNT(*) as count FROM estado_ganado")
                count = self.cursor.fetchone()['count']
                
                if count == 0:
                    query = "INSERT INTO estado_ganado (nombre, descripcion) VALUES (%s, %s)"
                    self.cursor.executemany(query, estados)
                    self.conn.commit()
                    print(f"   ✅ {len(estados)} estados de ganado insertados correctamente")
                else:
                    print(f"   ℹ️ Ya existen {count} estados de ganado en la base de datos")
            else:
                print("   ⚠️ La tabla 'estado_ganado' no existe en la base de datos")
                
        except Exception as e:
            print(f"   ❌ Error al insertar estados de ganado: {str(e)}")
            self.conn.rollback()
    
    def run(self):
        """Ejecuta todos los seeders"""
        print("=" * 60)
        print("🚀 INICIANDO PROCESO DE SEEDERS - QR-FARM")
        print("=" * 60)
        
        if not self.connect():
            print("\n❌ No se pudo establecer conexión con la base de datos")
            return False
        
        try:
            # Ejecutar seeders en orden
            self.seed_roles()
            self.seed_tipos_pasto()
            self.seed_tipos_vacuna()
            self.seed_estados_ganado()
            
            print("\n" + "=" * 60)
            print("✅ PROCESO DE SEEDERS COMPLETADO EXITOSAMENTE")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error general en el proceso de seeders: {str(e)}")
            return False
            
        finally:
            self.disconnect()
    
    def reset(self):
        """Elimina todos los datos de las tablas (excepto el admin)"""
        print("=" * 60)
        print("⚠️ REINICIANDO DATOS BASE - QR-FARM")
        print("=" * 60)
        
        if not self.connect():
            print("\n❌ No se pudo establecer conexión con la base de datos")
            return False
        
        try:
            respuesta = input("\n⚠️ ¿Está seguro de que desea eliminar todos los datos base? (s/n): ")
            
            if respuesta.lower() != 's':
                print("Operación cancelada")
                return False
            
            # Eliminar datos en orden inverso para respetar foreign keys
            tablas = [
                'tipo_vacuna',
                'tipo_pasto',
                'estado_ganado'  # Si existe
            ]
            
            for tabla in tablas:
                try:
                    # Verificar si la tabla existe
                    self.cursor.execute(f"""
                        SELECT COUNT(*) as count 
                        FROM information_schema.tables 
                        WHERE table_schema = %s 
                        AND table_name = %s
                    """, (os.getenv('DB_NAME', 'gestion_ganadera'), tabla))
                    
                    if self.cursor.fetchone()['count'] > 0:
                        self.cursor.execute(f"DELETE FROM {tabla}")
                        print(f"   ✅ Tabla '{tabla}' limpiada")
                except Exception as e:
                    print(f"   ⚠️ No se pudo limpiar la tabla '{tabla}': {str(e)}")
            
            # No eliminar roles para mantener integridad del sistema
            print("   ℹ️ Los roles no se eliminan para mantener la integridad del sistema")
            
            self.conn.commit()
            print("\n✅ Datos base reiniciados correctamente")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error al reiniciar datos: {str(e)}")
            self.conn.rollback()
            return False
            
        finally:
            self.disconnect()


def main():
    """Función principal para ejecutar los seeders"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gestor de Seeders para QR-FARM')
    parser.add_argument('--reset', action='store_true', help='Reinicia todos los datos base')
    args = parser.parse_args()
    
    seeder = SeederManager()
    
    if args.reset:
        seeder.reset()
        print("\nEjecutando seeders después del reset...")
        seeder.run()
    else:
        seeder.run()


if __name__ == "__main__":
    main()