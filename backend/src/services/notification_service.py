"""Notification service combining upcoming cleaning and vaccination events."""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from src.database.db import get_connection
from src.utils.tenant import get_current_tenant_id


class NotificationService:
    """Gathers upcoming alerting events for tenants."""

    CLEANING_THRESHOLD_DAYS = 7
    VACCINATION_THRESHOLD_DAYS = 7

    @staticmethod
    def _resolver_tenant_id(tenant_id_override: Optional[int]) -> Optional[int]:
        """Choose the most specific tenant context. Always requires tenant_id to filter notifications."""
        if tenant_id_override is not None:
            return tenant_id_override
        try:
            # Always require tenant_id to filter notifications per tenant
            # Even superadmin must select a tenant to see notifications
            from flask import g
            if hasattr(g, 'current_user') and g.current_user:
                from ..utils.tenant import _obtener_rol_nombre
                rol_nombre = _obtener_rol_nombre(g.current_user)
                if rol_nombre == 'super_admin':
                    # Superadmin can use tenant_id from query params or context
                    # If not provided, return None to show empty list (not error)
                    tenant_id = get_current_tenant_id(require_tenant=False)
                    # Return None instead of raising exception - will show empty notifications
                    return tenant_id
                else:
                    # Non-superadmin users must have a tenant_id from their context
                    tenant_id = get_current_tenant_id(require_tenant=True)
                    if tenant_id is None:
                        raise ValueError("Tenant ID requerido para usuarios no superadmin")
                    return tenant_id
            # Fallback: try to get tenant_id from context
            tenant_id = get_current_tenant_id(require_tenant=True)
            if tenant_id is None:
                raise ValueError("No se pudo determinar el tenant_id del contexto")
            return tenant_id
        except ValueError:
            # Re-raise ValueError to be handled by controller
            raise
        except Exception as e:
            # Log other errors and re-raise
            print(f"Error resolviendo tenant_id para notificaciones: {e}")
            raise ValueError(f"Error al determinar el tenant: {str(e)}")

    @staticmethod
    def _formatear_notificacion_limpieza(
        row: Dict[str, Any],
        referencia_datetime: datetime
    ) -> Dict[str, Any]:
        """Normalize a cleaning row into the notification shape."""
        fecha = row.get('fecha_proxima_limpieza')
        if fecha is None:
            raise ValueError('Cleaning event missing fecha_proxima_limpieza')

        dias_restantes = max(0, (fecha.date() - referencia_datetime.date()).days)
        responsable = row.get('responsable_nombre') or 'Responsable no asignado'
        return {
            'id': row.get('potrero_id'),
            'tipo': 'limpieza',
            'titulo': f"Limpieza próxima en {row.get('potrero_nombre', 'Potrero desconocido')}",
            'descripcion': f"Programada para el {fecha.date().isoformat()}",
            'fecha': fecha.isoformat(),
            'dias_restantes': dias_restantes,
            'responsable': responsable,
            'contexto': {
                'potrero_id': row.get('potrero_id'),
                'nombre_potrero': row.get('potrero_nombre')
            }
        }

    @staticmethod
    def _formatear_notificacion_vacunacion(
        row: Dict[str, Any],
        referencia_datetime: datetime
    ) -> Dict[str, Any]:
        """Normalize a vaccination row into the notification shape."""
        fecha = row.get('proxima_dosis')
        if fecha is None:
            raise ValueError('Vaccination event missing proxima_dosis')

        dias_restantes = max(0, (fecha.date() - referencia_datetime.date()).days)
        responsable = row.get('responsable_nombre') or 'Responsable no asignado'
        vacuna = (
            row.get('nombre_tipo_vacuna')
            or row.get('nombre_vacuna')
            or row.get('tipo_vacuna')
            or 'Vacuna desconocida'
        )
        animal = row.get('nombre_animal') or 'Animal desconocido'
        return {
            'id': row.get('vacunacion_id'),
            'tipo': 'vacunacion',
            'titulo': f"Vacunación próxima para {animal}",
            'descripcion': f"{vacuna} agendada para {fecha.date().isoformat()}",
            'fecha': fecha.isoformat(),
            'dias_restantes': dias_restantes,
            'responsable': responsable,
            'contexto': {
                'vacunacion_id': row.get('vacunacion_id'),
                'animal_id': row.get('animal_id'),
                'nombre_vacuna': vacuna,
                'nombre_tipo_vacuna': row.get('nombre_tipo_vacuna'),
                'nombre_animal': animal
            }
        }

    @staticmethod
    def _obtener_potreros_con_limpieza_proxima(
        tenant_id_override: Optional[int]
    ) -> List[Dict[str, Any]]:
        """Fetch cleaning events whose next date lies within the threshold."""
        tenant_id = NotificationService._resolver_tenant_id(tenant_id_override)
        threshold_days = NotificationService.CLEANING_THRESHOLD_DAYS
        query = """
            SELECT
                p.id AS potrero_id,
                p.nombre AS potrero_nombre,
                hp.fecha_proxima_limpieza,
                CONCAT(
                    COALESCE(per.primer_nombre, ''), ' ',
                    COALESCE(per.segundo_nombre, ''), ' ',
                    COALESCE(per.primer_apellido, ''), ' ',
                    COALESCE(per.segundo_apellido, '')
                ) AS responsable_nombre
            FROM potrero p
            JOIN historial_potreros hp ON hp.id_potrero = p.id
            LEFT JOIN personas per ON per.id = p.responsable_persona_id
            WHERE hp.fecha_proxima_limpieza IS NOT NULL
              AND hp.fecha_proxima_limpieza BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL %s DAY)
        """
        params: List[Any] = [threshold_days]
        if tenant_id is not None:
            query += " AND p.tenant_id = %s"
            params.append(tenant_id)
        query += " ORDER BY hp.fecha_proxima_limpieza ASC"

        connection = get_connection()
        if connection is None:
            return []

        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            ahora = datetime.utcnow()
            eventos = []
            for row in rows:
                if row.get('fecha_proxima_limpieza') is None:
                    continue
                eventos.append(
                    NotificationService._formatear_notificacion_limpieza(row, ahora)
                )
            return eventos
        except Exception as exc:  # pragma: no cover - best effort logging
            print(f"Error fetching cleaning notifications: {exc}")
            return []
        finally:
            cursor.close()
            if hasattr(connection, 'is_connected') and connection.is_connected():
                connection.close()

    @staticmethod
    def _obtener_vacunaciones_con_dosis_proxima(
        tenant_id_override: Optional[int]
    ) -> List[Dict[str, Any]]:
        """Fetch vaccination events whose next dose lies within the threshold."""
        tenant_id = NotificationService._resolver_tenant_id(tenant_id_override)
        threshold_days = NotificationService.VACCINATION_THRESHOLD_DAYS
        query = """
            SELECT
                v.id AS vacunacion_id,
                v.id_animal AS animal_id,
                g.nombre AS nombre_animal,
                v.proxima_dosis,
                v.estado,
                v.id_tipo_vacuna,
                CONCAT(
                    COALESCE(per.primer_nombre, ''), ' ',
                    COALESCE(per.segundo_nombre, ''), ' ',
                    COALESCE(per.primer_apellido, ''), ' ',
                    COALESCE(per.segundo_apellido, '')
                ) AS responsable_nombre,
                tv.nombre_vacuna AS nombre_tipo_vacuna
            FROM vacunacion v
            LEFT JOIN ganado g ON g.id = v.id_animal
            LEFT JOIN personas per ON per.id = v.responsable
            LEFT JOIN tipo_vacuna tv ON tv.id = v.id_tipo_vacuna
            WHERE v.proxima_dosis IS NOT NULL
              AND v.proxima_dosis BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL %s DAY)
        """
        params: List[Any] = [threshold_days]
        if tenant_id is not None:
            query += " AND v.tenant_id = %s"
            params.append(tenant_id)
        query += " ORDER BY v.proxima_dosis ASC"

        connection = get_connection()
        if connection is None:
            return []

        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            ahora = datetime.utcnow()
            eventos = []
            for row in rows:
                if row.get('proxima_dosis') is None:
                    continue
                eventos.append(
                    NotificationService._formatear_notificacion_vacunacion(row, ahora)
                )
            return eventos
        except Exception as exc:  # pragma: no cover - best effort logging
            print(f"Error fetching vaccination notifications: {exc}")
            return []
        finally:
            cursor.close()
            if hasattr(connection, 'is_connected') and connection.is_connected():
                connection.close()

    @staticmethod
    def _obtener_solicitudes_recuperacion_pendientes(
        tenant_id_override: Optional[int]
    ) -> List[Dict[str, Any]]:
        """Fetch pending password recovery requests as notifications."""
        tenant_id = NotificationService._resolver_tenant_id(tenant_id_override)
        if tenant_id is None:
            return []
        
        from src.services.recovery_service import RecoveryService
        try:
            requests = RecoveryService.list_pending_requests(tenant_id)
            eventos = []
            for req in requests:
                created_at = req.get('created_at')
                if isinstance(created_at, datetime):
                    fecha_str = created_at.isoformat()
                elif created_at:
                    fecha_str = str(created_at)
                else:
                    fecha_str = datetime.utcnow().isoformat()
                
                eventos.append({
                    'id': f"recovery-{req['id']}",
                    'tipo': 'recuperacion',
                    'titulo': f"Solicitud de recuperación de contraseña",
                    'descripcion': f"Usuario {req.get('usuario_nombre', req.get('solicitante_email', 'Desconocido'))} ({req.get('usuario_email', req.get('solicitante_email', ''))})",
                    'fecha': fecha_str,
                    'dias_restantes': 0,
                    'responsable': req.get('usuario_nombre', 'Usuario'),
                    'contexto': {
                        'recovery_id': req['id'],
                        'usuario_id': req['usuario_id'],
                        'tipo_solicitud': req.get('tipo', 'usuario'),
                        'usuario_email': req.get('usuario_email', req.get('solicitante_email', ''))
                    }
                })
            return eventos
        except Exception as exc:
            print(f"Error fetching recovery notifications: {exc}")
            return []

    @staticmethod
    def obtener_notificaciones_proximas(
        tenant_id_override: Optional[int]
    ) -> List[Dict[str, Any]]:
        """Return the next alerts combining potrero, vaccination, and recovery requests."""
        eventos_potreros = NotificationService._obtener_potreros_con_limpieza_proxima(tenant_id_override)
        eventos_vacunaciones = NotificationService._obtener_vacunaciones_con_dosis_proxima(tenant_id_override)
        eventos_recuperacion = NotificationService._obtener_solicitudes_recuperacion_pendientes(tenant_id_override)

        combinadas = eventos_potreros + eventos_vacunaciones + eventos_recuperacion
        # Sort by date, but recovery requests should appear first
        combinadas.sort(key=lambda evento: (
            0 if evento.get('tipo') == 'recuperacion' else 1,
            evento['fecha']
        ))
        return combinadas

