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
        """Choose the most specific tenant context."""
        if tenant_id_override is not None:
            return tenant_id_override
        try:
            return get_current_tenant_id()
        except Exception:
            return None

    @staticmethod
    def _formatear_notificacion_limpieza(
        row: Dict[str, Any],
        referencia_datetime: datetime
    ) -> Dict[str, Any]:
        """Normalize a cleaning row into the notification shape."""
        fecha = row.get('fecha_proxima_limpieza')
        if fecha is None:
            raise ValueError('Cleaning event missing fecha_proxima_limpieza')

        dias_restantes = max(0, (fecha - referencia_datetime).days)
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

        dias_restantes = max(0, (fecha - referencia_datetime).days)
        responsable = row.get('responsable_nombre') or 'Responsable no asignado'
        vacuna = row.get('nombre_tipo_vacuna') or 'Vacuna desconocida'
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
    def obtener_notificaciones_proximas(
        tenant_id_override: Optional[int]
    ) -> List[Dict[str, Any]]:
        """Return the next alerts combining potrero and vaccination windows."""
        eventos_potreros = NotificationService._obtener_potreros_con_limpieza_proxima(tenant_id_override)
        eventos_vacunaciones = NotificationService._obtener_vacunaciones_con_dosis_proxima(tenant_id_override)

        combinadas = eventos_potreros + eventos_vacunaciones
        combinadas.sort(key=lambda evento: evento['fecha'])
        return combinadas

