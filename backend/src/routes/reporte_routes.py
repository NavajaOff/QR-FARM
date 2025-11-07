"""Rutas del módulo de reportes."""

from flask import Blueprint

from ..controllers.reporte_controller import ReporteController
from ..utils.auth import token_required


reporte_bp = Blueprint("reporte", __name__)

reporte_bp.route("/resumen", methods=["GET"])(token_required(ReporteController.obtener_resumen))
reporte_bp.route("/resumen/pdf", methods=["GET"])(token_required(ReporteController.descargar_resumen_pdf))

