"""Controlador para endpoints de reportes."""

from flask import jsonify, send_file

from ..services.reporte_service import ReporteService


class ReporteController:
    """Expone endpoints para consultar y descargar reportes."""

    @staticmethod
    def obtener_resumen():
        try:
            resumen = ReporteService.obtener_resumen()

            if resumen.get("error"):
                return jsonify({
                    "status": "error",
                    "message": "No fue posible generar el resumen",
                    "data": resumen,
                }), 500

            return jsonify({
                "status": "success",
                "data": resumen,
            }), 200

        except Exception as exc:
            return jsonify({
                "status": "error",
                "message": str(exc),
            }), 500

    @staticmethod
    def descargar_resumen_pdf():
        try:
            resumen = ReporteService.obtener_resumen()

            if resumen.get("error"):
                return jsonify({
                    "status": "error",
                    "message": "No fue posible generar el PDF",
                }), 500

            pdf_buffer = ReporteService.generar_pdf(resumen)

            return send_file(
                pdf_buffer,
                download_name="reporte_qr_farm.pdf",
                mimetype="application/pdf",
                as_attachment=True,
            )

        except Exception as exc:
            return jsonify({
                "status": "error",
                "message": str(exc),
            }), 500

