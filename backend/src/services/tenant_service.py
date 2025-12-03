"""Servicio para gestión de tenants."""
from typing import List, Optional, Dict, Any
from src.database.db import get_connection
from src.models.tenant import Tenant, EstadoTenant
from src.utils.slug import generar_codigo_tenant_unico


class TenantService:
    """Servicio para operaciones de tenant."""

    @staticmethod
    def crear_tenant(nombre: str) -> Optional[Tenant]:
        """
        Crear nuevo tenant.
        
        El código del tenant se genera automáticamente a partir del nombre.
        
        Args:
            nombre: Nombre del tenant
            
        Returns:
            Tenant creado o None si hay error
        """
        try:
            if not nombre or not nombre.strip():
                print("Error: El nombre del tenant no puede estar vacío")
                return None
            
            # Generar código único automáticamente
            codigo_tenant = generar_codigo_tenant_unico(nombre.strip())
            
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                INSERT INTO tenants (nombre, codigo_tenant, estado)
                VALUES (%s, %s, 'activo')
            """, (nombre.strip(), codigo_tenant))
            
            tenant_id = cursor.lastrowid
            conn.commit()
            cursor.close()
            conn.close()
            
            return TenantService.obtener_tenant(tenant_id)
        except Exception as e:
            print(f"Error creando tenant: {e}")
            return None

    @staticmethod
    def obtener_tenant(tenant_id: int) -> Optional[Tenant]:
        """Obtener tenant por ID."""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT * FROM tenants WHERE id = %s
            """, (tenant_id,))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result:
                return Tenant.from_dict(result)
            return None
        except Exception as e:
            print(f"Error obteniendo tenant: {e}")
            return None

    @staticmethod
    def obtener_tenant_por_codigo(codigo_tenant: str) -> Optional[Tenant]:
        """Obtener tenant por código."""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT * FROM tenants WHERE codigo_tenant = %s
            """, (codigo_tenant,))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result:
                return Tenant.from_dict(result)
            return None
        except Exception as e:
            print(f"Error obteniendo tenant por código: {e}")
            return None

    @staticmethod
    def listar_tenants(activos_only: bool = True) -> List[Tenant]:
        """Listar todos los tenants."""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM tenants"
            if activos_only:
                query += " WHERE estado = 'activo'"
            else:
                query += " WHERE estado = 'inactivo'"
            query += " ORDER BY nombre"
            
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return [Tenant.from_dict(r) for r in results]
        except Exception as e:
            print(f"Error listando tenants: {e}")
            return []

    @staticmethod
    def actualizar_tenant(tenant_id: int, nombre: Optional[str] = None, 
                         estado: Optional[EstadoTenant] = None) -> Optional[Tenant]:
        """Actualizar tenant."""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            updates = []
            values = []
            
            if nombre:
                updates.append("nombre = %s")
                values.append(nombre)
            
            if estado:
                estado_valor = estado.value if hasattr(estado, 'value') else str(estado)
                updates.append("estado = %s")
                values.append(estado_valor)
            
            if not updates:
                return TenantService.obtener_tenant(tenant_id)
            
            values.append(tenant_id)
            query = f"UPDATE tenants SET {', '.join(updates)} WHERE id = %s"
            
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            conn.close()
            
            return TenantService.obtener_tenant(tenant_id)
        except Exception as e:
            print(f"Error actualizando tenant: {e}")
            return None

