"""Servicio para generación de reportes consolidados del sistema."""

from __future__ import annotations

from typing import Dict, Any, List, Iterable
from datetime import datetime, date, timedelta, timezone
from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

from ..database.db import get_connection


class ReporteService:
    """Provee datos resumidos y generación de reportes en PDF."""
    
    # SQL constants
    SQL_WHERE_TENANT_ID = " WHERE tenant_id = %s"
    SQL_WHERE_G_TENANT_ID = " WHERE g.tenant_id = %s"
    SQL_AND_G_TENANT_ID = " AND g.tenant_id = %s"
    SQL_GROUP_BY_ESTADO = " GROUP BY COALESCE(estado, 'sin_estado') ORDER BY cantidad DESC"
    SQL_GROUP_BY_ESTADO_GANADO = " GROUP BY COALESCE(eg.tipo_estado, 'sin_estado') ORDER BY cantidad DESC"
    SQL_GROUP_BY_ESTADO_VACUNACION = " GROUP BY COALESCE(v.estado, 'sin_estado') ORDER BY cantidad DESC"

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
    def _fetch_daily_counts(
        cursor,
        tabla: str,
        columna_fecha: str,
        dias: int = 10,
        tenant_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Obtiene conteos diarios de registros para la tabla dada."""
        try:
            query = f"""
                SELECT DATE({columna_fecha}) AS fecha, COUNT(*) AS total
                FROM {tabla}
                WHERE {columna_fecha} IS NOT NULL
                  AND {columna_fecha} >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            """
            params = (dias,)
            if tenant_id is not None:
                # Detectar si la tabla tiene alias o JOIN para aplicar tenant_id correctamente
                tabla_lower = tabla.lower()
                # Si la tabla ya tiene un JOIN con ganado (alias g), usar g.tenant_id directamente
                if 'join ganado g' in tabla_lower or ('join g' in tabla_lower and 'ganado' in tabla_lower):
                    # Tabla con JOIN a ganado, filtrar por g.tenant_id directamente
                    query += " AND g.tenant_id = %s"
                    params = (dias, tenant_id)
                elif 'v.' in columna_fecha and 'vacunacion' in tabla_lower:
                    # Para vacunaciones sin JOIN explícito, usar EXISTS con alias diferente
                    query += " AND EXISTS (SELECT 1 FROM ganado g2 WHERE g2.id = v.id_animal AND g2.tenant_id = %s)"
                    params = (dias, tenant_id)
                else:
                    # Tabla normal, filtrar por tenant_id directo
                    query += " AND tenant_id = %s"
                    params = (dias, tenant_id)
            query += f" GROUP BY DATE({columna_fecha}) ORDER BY fecha"
            print(f"[REPORTE_SERVICE] SQL generado: {query}")
            print(f"[REPORTE_SERVICE] Params: {params}")
            cursor.execute(query, params)
            return cursor.fetchall()
        except Exception as exc:
            import traceback
            print(f"[REPORTE_SERVICE] Error obteniendo tendencia para {tabla}.{columna_fecha}: {exc}")
            print(f"[REPORTE_SERVICE] Traceback: {traceback.format_exc()}")
            return []

    @staticmethod
    def _normalizar_fecha(valor: Any) -> str:
        if isinstance(valor, datetime):
            return valor.date().isoformat()
        if isinstance(valor, date):
            return valor.isoformat()
        return str(valor) if valor is not None else ""

    @staticmethod
    def _calcular_variacion(serie: List[Dict[str, Any]]) -> Dict[str, Any]:
        if len(serie) < 2:
            return {"variacion": 0.0, "variacion_absoluta": 0}

        ultimo = serie[-1].get("total", 0) or 0
        anterior = serie[-2].get("total", 0) or 0
        delta_absoluto = ultimo - anterior

        if anterior == 0:
            variacion = 100.0 if ultimo > 0 else 0.0
        else:
            variacion = (delta_absoluto / anterior) * 100

        return {
            "variacion": round(variacion, 2),
            "variacion_absoluta": delta_absoluto,
        }

    @staticmethod
    def _build_trend_payload(
        cursor,
        tabla: str,
        columnas_fecha: Iterable[str],
        fallback_total: int = 0,
        tenant_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Construye un payload de tendencia usando la primera columna disponible."""
        # Si no hay columnas de fecha, retornar trend vacío
        if not columnas_fecha:
            return ReporteService._empty_trend()
        
        for columna in columnas_fecha:
            try:
                resultados = ReporteService._fetch_daily_counts(cursor, tabla, columna, tenant_id=tenant_id)
                if resultados:
                    serie: List[Dict[str, Any]] = []
                    total_periodo = 0
                    for row in resultados:
                        fecha_valor = row.get("fecha")
                        total = row.get("total", 0) or 0
                        serie.append(
                            {
                                "fecha": ReporteService._normalizar_fecha(fecha_valor),
                                "total": total,
                            }
                        )
                        total_periodo += total

                    promedio = round(total_periodo / len(serie), 2) if serie else 0.0
                    variacion = ReporteService._calcular_variacion(serie)

                    return {
                        "serie": serie,
                        "total_periodo": total_periodo,
                        "promedio_diario": promedio,
                        **variacion,
                    }
            except Exception as exc:
                import traceback
                print(f"[REPORTE_SERVICE] Error procesando columna {columna} de tabla {tabla}: {exc}")
                print(f"[REPORTE_SERVICE] Traceback: {traceback.format_exc()}")
                continue

        # Si ninguna columna devolvió datos, regresar estructura vacía
        return ReporteService._fallback_trend(fallback_total)

    @staticmethod
    def _empty_trend() -> Dict[str, Any]:
        return {
            "serie": [],
            "total_periodo": 0,
            "promedio_diario": 0.0,
            "variacion": 0.0,
            "variacion_absoluta": 0,
        }

    @staticmethod
    def _fallback_trend(total: int) -> Dict[str, Any]:
        valor = int(total or 0)
        today = datetime.now(timezone.utc).date()
        serie = []
        for offset in range(5, 0, -1):
            fecha = today - timedelta(days=offset)
            serie.append({"fecha": fecha.isoformat(), "total": valor})
        serie.append({"fecha": today.isoformat(), "total": valor})
        promedio = float(valor)
        total_periodo = valor * len(serie)
        return {
            "serie": serie,
            "total_periodo": total_periodo,
            "promedio_diario": promedio,
            "variacion": 0.0,
            "variacion_absoluta": 0,
        }

    @staticmethod
    def _obtener_usuarios_metricas(cursor, tenant_id):
        """Obtiene métricas de usuarios."""
        usuarios_query = """
            SELECT
                COUNT(*) AS total,
                SUM(CASE WHEN estado = 'activo' THEN 1 ELSE 0 END) AS activos,
                SUM(CASE WHEN estado = 'inactivo' THEN 1 ELSE 0 END) AS inactivos
            FROM usuarios
        """
        if tenant_id is not None:
            usuarios_query += ReporteService.SQL_WHERE_TENANT_ID
            cursor.execute(usuarios_query, (tenant_id,))
        else:
            cursor.execute(usuarios_query)
        usuarios = cursor.fetchone() or {"total": 0, "activos": 0, "inactivos": 0}

        usuarios_breakdown_query = "SELECT COALESCE(estado, 'sin_estado') AS estado, COUNT(*) AS cantidad FROM usuarios"
        if tenant_id is not None:
            usuarios_breakdown_query += ReporteService.SQL_WHERE_TENANT_ID
            usuarios_breakdown_query += ReporteService.SQL_GROUP_BY_ESTADO
            cursor.execute(usuarios_breakdown_query, (tenant_id,))
        else:
            usuarios_breakdown_query += ReporteService.SQL_GROUP_BY_ESTADO
            cursor.execute(usuarios_breakdown_query)
        usuarios_breakdown = cursor.fetchall()
        return usuarios, usuarios_breakdown

    @staticmethod
    def _obtener_ganado_metricas(cursor, tenant_id):
        """Obtiene métricas de ganado."""
        ganado_query = "SELECT COUNT(*) AS total FROM ganado"
        if tenant_id is not None:
            ganado_query += ReporteService.SQL_WHERE_TENANT_ID
            cursor.execute(ganado_query, (tenant_id,))
        else:
            cursor.execute(ganado_query)
        ganado_total = cursor.fetchone() or {"total": 0}

        ganado_breakdown_query = """
            SELECT
                COALESCE(eg.tipo_estado, 'sin_estado') AS estado,
                COUNT(*) AS cantidad
            FROM ganado g
            LEFT JOIN estado_ganado eg ON g.id_estado = eg.id
        """
        if tenant_id is not None:
            ganado_breakdown_query += ReporteService.SQL_WHERE_G_TENANT_ID
            ganado_breakdown_query += ReporteService.SQL_GROUP_BY_ESTADO_GANADO
            cursor.execute(ganado_breakdown_query, (tenant_id,))
        else:
            ganado_breakdown_query += ReporteService.SQL_GROUP_BY_ESTADO_GANADO
            cursor.execute(ganado_breakdown_query)
        ganado_breakdown = cursor.fetchall()
        return ganado_total, ganado_breakdown

    @staticmethod
    def _obtener_potreros_metricas(cursor, tenant_id):
        """Obtiene métricas de potreros."""
        potreros_query = "SELECT COUNT(*) AS total FROM potrero"
        if tenant_id is not None:
            potreros_query += ReporteService.SQL_WHERE_TENANT_ID
            cursor.execute(potreros_query, (tenant_id,))
        else:
            cursor.execute(potreros_query)
        potreros_total = cursor.fetchone() or {"total": 0}

        potreros_breakdown_query = """
            SELECT
                COALESCE(ep.nombre_estado, 'sin_estado') AS estado,
                COUNT(*) AS cantidad
            FROM potrero p
            LEFT JOIN estado_potrero ep ON p.id_estado_potrero = ep.id
        """
        group_clause = " GROUP BY COALESCE(ep.nombre_estado, 'sin_estado') ORDER BY cantidad DESC"
        if tenant_id is not None:
            potreros_breakdown_query += " WHERE p.tenant_id = %s"
            potreros_breakdown_query += group_clause
            cursor.execute(potreros_breakdown_query, (tenant_id,))
        else:
            potreros_breakdown_query += group_clause
            cursor.execute(potreros_breakdown_query)
        potreros_breakdown = cursor.fetchall()
        return potreros_total, potreros_breakdown

    @staticmethod
    def _obtener_vacunaciones_metricas(cursor, tenant_id):
        """Obtiene métricas de vacunaciones."""
        vacunacion_query = """
            SELECT COUNT(*) AS total FROM vacunacion v
            INNER JOIN ganado g ON v.id_animal = g.id
        """
        if tenant_id is not None:
            vacunacion_query += ReporteService.SQL_WHERE_G_TENANT_ID
            cursor.execute(vacunacion_query, (tenant_id,))
        else:
            cursor.execute(vacunacion_query)
        vacunacion_total = cursor.fetchone() or {"total": 0}

        vacunacion_breakdown_query = """
            SELECT COALESCE(v.estado, 'sin_estado') AS estado, COUNT(*) AS cantidad
            FROM vacunacion v
            INNER JOIN ganado g ON v.id_animal = g.id
        """
        if tenant_id is not None:
            vacunacion_breakdown_query += ReporteService.SQL_WHERE_G_TENANT_ID
            vacunacion_breakdown_query += ReporteService.SQL_GROUP_BY_ESTADO_VACUNACION
            cursor.execute(vacunacion_breakdown_query, (tenant_id,))
        else:
            vacunacion_breakdown_query += ReporteService.SQL_GROUP_BY_ESTADO_VACUNACION
            cursor.execute(vacunacion_breakdown_query)
        vacunacion_breakdown = cursor.fetchall()

        proximas_query = """
            SELECT COUNT(*) AS proximas
            FROM vacunacion v
            INNER JOIN ganado g ON v.id_animal = g.id
            WHERE v.proxima_dosis IS NOT NULL AND v.proxima_dosis >= CURDATE()
        """
        if tenant_id is not None:
            proximas_query += ReporteService.SQL_AND_G_TENANT_ID
            cursor.execute(proximas_query, (tenant_id,))
        else:
            cursor.execute(proximas_query)
        vacunacion_proximas = cursor.fetchone() or {"proximas": 0}
        return vacunacion_total, vacunacion_breakdown, vacunacion_proximas

    @staticmethod
    def obtener_resumen() -> Dict[str, Any]:
        """Obtiene métricas generales del sistema."""
        from ..utils.tenant import get_current_tenant_id

        conn = None
        cursor = None

        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)

            tenant_id = get_current_tenant_id()

            usuarios, usuarios_breakdown = ReporteService._obtener_usuarios_metricas(cursor, tenant_id)
            ganado_total, ganado_breakdown = ReporteService._obtener_ganado_metricas(cursor, tenant_id)
            potreros_total, potreros_breakdown = ReporteService._obtener_potreros_metricas(cursor, tenant_id)
            vacunacion_total, vacunacion_breakdown, vacunacion_proximas = ReporteService._obtener_vacunaciones_metricas(cursor, tenant_id)

            usuarios_total = int(usuarios.get("total", 0))
            ganado_total_count = int(ganado_total.get("total", 0))
            potreros_total_count = int(potreros_total.get("total", 0))
            vacunaciones_total_count = int(vacunacion_total.get("total", 0))

            tendencias = {
                "usuarios": ReporteService._build_trend_payload(
                    cursor,
                    "usuarios",
                    (),  # La tabla no cuenta con campos de fecha
                    fallback_total=usuarios_total,
                    tenant_id=tenant_id,
                ),
                "ganado": ReporteService._build_trend_payload(
                    cursor,
                    "ganado",
                    ("fecha_nacimiento",),
                    fallback_total=ganado_total_count,
                    tenant_id=tenant_id,
                ),
                "potreros": ReporteService._build_trend_payload(
                    cursor,
                    "potrero",
                    (),  # Nota: fecha_ultimo_uso, proxima_limpieza y ultima_limpieza ahora se obtienen
                    # desde historial_potrero, no desde potrero directamente
                    # Usar fallback ya que las fechas están en historial_potrero
                    fallback_total=potreros_total_count,
                    tenant_id=tenant_id,
                ),
                "vacunaciones": ReporteService._build_trend_payload(
                    cursor,
                    "vacunacion v INNER JOIN ganado g ON v.id_animal = g.id",
                    ("v.fecha_aplicacion", "v.proxima_dosis"),
                    fallback_total=vacunaciones_total_count,
                    tenant_id=tenant_id,
                ),
            }

            return {
                "generado_en": datetime.now(timezone.utc).isoformat(),
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
                "tendencias": tendencias,
            }

        except Exception as exc:
            import traceback
            error_trace = traceback.format_exc()
            print(f"[REPORTE_SERVICE] Error generando resumen de reportes: {exc}")
            print(f"[REPORTE_SERVICE] Traceback completo:\n{error_trace}")
            return {
                "error": True,
                "error_message": str(exc),
                "generado_en": datetime.now(timezone.utc).isoformat(),
                "usuarios": {"totales": {"total": 0, "activos": 0, "inactivos": 0}, "por_estado": []},
                "ganado": {"totales": {"total": 0}, "por_estado": []},
                "potreros": {"totales": {"total": 0}, "por_estado": []},
                "vacunaciones": {"totales": {"total": 0}, "por_estado": [], "proximas": 0},
                "tendencias": {
                    "usuarios": ReporteService._empty_trend(),
                    "ganado": ReporteService._empty_trend(),
                    "potreros": ReporteService._empty_trend(),
                    "vacunaciones": ReporteService._empty_trend(),
                },
                "error_detail": str(exc),
            }
        finally:
            ReporteService._safe_close(conn, cursor)

    @staticmethod
    def generar_pdf(resumen: Dict[str, Any]) -> BytesIO:
        """Genera un PDF en memoria a partir del resumen."""
        pdf_buffer = BytesIO()
        pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
        _width, height = letter

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
        pdf_buffer.seek(0)
        return pdf_buffer

