"""Servicio para generación de reportes consolidados del sistema."""

from __future__ import annotations

from typing import Dict, Any, List
from datetime import datetime
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

from ..database.db import get_connection


class ReporteService:
    """Provee datos resumidos y generación de reportes en PDF."""

    @staticmethod
    def _fetch_estado_breakdown(cursor, tabla: str, campo_estado: str = "estado", joins: str = "") -> List[Dict[str, Any]]:
        query = f"""
            SELECT
                COALESCE({campo_estado}, 'sin_estado') AS estado,
                COUNT(*) AS cantidad
            FROM {tabla}
            {joins}
            GROUP BY COALESCE({campo_estado}, 'sin_estado')
            ORDER BY cantidad DESC
        """
        cursor.execute(query)
        return cursor.fetchall()

    @staticmethod
    def _safe_close(conn, cursor) -> None:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            try:
                conn.close()
            except Exception:
                pass

    @staticmethod
    def obtener_resumen() -> Dict[str, Any]:
        """Obtiene métricas generales del sistema."""
        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            # Usuarios
            cursor.execute(
                """
                SELECT
                    COUNT(*) AS total,
                    SUM(CASE WHEN estado = 'activo' THEN 1 ELSE 0 END) AS activos,
                    SUM(CASE WHEN estado = 'inactivo' THEN 1 ELSE 0 END) AS inactivos
                FROM usuarios
                """
            )
            usuarios = cursor.fetchone() or {"total": 0, "activos": 0, "inactivos": 0}
            usuarios_breakdown = ReporteService._fetch_estado_breakdown(cursor, "usuarios")

            # Ganado
            cursor.execute("SELECT COUNT(*) AS total FROM ganado")
            ganado_total = cursor.fetchone() or {"total": 0}
            ganado_breakdown = ReporteService._fetch_estado_breakdown(
                cursor,
                "ganado g",
                campo_estado="eg.tipo_estado",
                joins="LEFT JOIN estado_ganado eg ON g.id_estado = eg.id",
            )

            # Potreros
            cursor.execute("SELECT COUNT(*) AS total FROM potrero")
            potreros_total = cursor.fetchone() or {"total": 0}
            potreros_breakdown = ReporteService._fetch_estado_breakdown(cursor, "potrero")

            # Vacunaciones
            cursor.execute("SELECT COUNT(*) AS total FROM vacunacion")
            vacunacion_total = cursor.fetchone() or {"total": 0}
            vacunacion_breakdown = ReporteService._fetch_estado_breakdown(cursor, "vacunacion")

            cursor.execute(
                """
                SELECT COUNT(*) AS proximas
                FROM vacunacion
                WHERE proxima_dosis IS NOT NULL AND proxima_dosis >= CURDATE()
                """
            )
            vacunacion_proximas = cursor.fetchone() or {"proximas": 0}

            return {
                "generado_en": datetime.utcnow().isoformat(),
                "usuarios": {
                    "totales": usuarios,
                    "por_estado": usuarios_breakdown,
                },
                "ganado": {
                    "totales": ganado_total,
                    "por_estado": ganado_breakdown,
                },
                "potreros": {
                    "totales": potreros_total,
                    "por_estado": potreros_breakdown,
                },
                "vacunaciones": {
                    "totales": vacunacion_total,
                    "por_estado": vacunacion_breakdown,
                    "proximas": vacunacion_proximas.get("proximas", 0),
                },
            }

        except Exception as exc:
            print(f"Error generando resumen de reportes: {exc}")
            return {
                "generado_en": datetime.utcnow().isoformat(),
                "usuarios": {"totales": {"total": 0, "activos": 0, "inactivos": 0}, "por_estado": []},
                "ganado": {"totales": {"total": 0}, "por_estado": []},
                "potreros": {"totales": {"total": 0}, "por_estado": []},
                "vacunaciones": {"totales": {"total": 0}, "por_estado": [], "proximas": 0},
                "error": str(exc),
            }
        finally:
            ReporteService._safe_close(conn, cursor)

    @staticmethod
    def generar_pdf(resumen: Dict[str, Any]) -> BytesIO:
        """Genera un PDF en memoria a partir del resumen."""
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        margin = 0.75 * inch
        y = height - margin

        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawString(margin, y, "Reporte General QR-FARM")
        y -= 0.35 * inch

        pdf.setFont("Helvetica", 10)
        generado = resumen.get("generado_en")
        pdf.drawString(margin, y, f"Generado: {generado}")
        y -= 0.35 * inch

        def draw_section(titulo: str, totales: Dict[str, Any], detalle: List[Dict[str, Any]], extra: str = ""):
            nonlocal y
            if y < margin + inch:
                pdf.showPage()
                y = height - margin

            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawString(margin, y, titulo)
            y -= 0.25 * inch

            pdf.setFont("Helvetica", 11)
            for clave, valor in totales.items():
                pdf.drawString(margin + 0.2 * inch, y, f"{clave.capitalize()}: {valor}")
                y -= 0.2 * inch

            if detalle:
                y -= 0.05 * inch
                pdf.setFont("Helvetica-Bold", 11)
                pdf.drawString(margin + 0.2 * inch, y, "Detalle por estado:")
                y -= 0.2 * inch
                pdf.setFont("Helvetica", 11)
                for item in detalle:
                    estado = item.get("estado", "sin_estado")
                    cantidad = item.get("cantidad", 0)
                    pdf.drawString(margin + 0.4 * inch, y, f"- {estado}: {cantidad}")
                    y -= 0.18 * inch

            if extra:
                pdf.drawString(margin + 0.2 * inch, y, extra)
                y -= 0.2 * inch

            y -= 0.15 * inch

        draw_section(
            "Usuarios",
            resumen.get("usuarios", {}).get("totales", {}),
            resumen.get("usuarios", {}).get("por_estado", []),
        )

        draw_section(
            "Ganado",
            resumen.get("ganado", {}).get("totales", {}),
            resumen.get("ganado", {}).get("por_estado", []),
        )

        draw_section(
            "Potreros",
            resumen.get("potreros", {}).get("totales", {}),
            resumen.get("potreros", {}).get("por_estado", []),
        )

        vacunacion = resumen.get("vacunaciones", {})
        draw_section(
            "Vacunaciones",
            vacunacion.get("totales", {}),
            vacunacion.get("por_estado", []),
            extra=f"Próximas dosis programadas: {vacunacion.get('proximas', 0)}",
        )

        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        return buffer

