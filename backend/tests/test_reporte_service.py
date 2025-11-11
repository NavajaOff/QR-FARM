"""Pruebas para ReporteService."""

from __future__ import annotations

from io import BytesIO

from .helpers import load_module, prepare_environment


def test_generar_pdf_crea_documento(monkeypatch):
    """El PDF generado debe contener datos binarios válidos."""
    prepare_environment(monkeypatch)
    reporte_module = load_module("reporte_service_module", "src/services/reporte_service.py")

    resumen = {
        "generado_en": "2025-11-11T10:00:00Z",
        "usuarios": {"totales": {"total": 1, "activos": 1, "inactivos": 0}, "por_estado": []},
        "ganado": {"totales": {"total": 2}, "por_estado": []},
        "potreros": {"totales": {"total": 1}, "por_estado": []},
        "vacunaciones": {"totales": {"total": 3}, "por_estado": [], "proximas": 1},
    }

    pdf_stream = reporte_module.ReporteService.generar_pdf(resumen)

    assert isinstance(pdf_stream, BytesIO)
    contenido = pdf_stream.read(5)
    assert contenido.startswith(b"%PDF")

