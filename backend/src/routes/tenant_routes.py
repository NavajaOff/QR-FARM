"""Rutas para gestión de tenants."""
from flask import Blueprint
from src.controllers.tenant_controller import TenantController

tenant_bp = Blueprint('tenants', __name__)

tenant_bp.route('', methods=['GET'])(TenantController.listar_tenants)
tenant_bp.route('', methods=['POST'])(TenantController.crear_tenant)
tenant_bp.route('/<int:tenant_id>', methods=['GET'])(TenantController.obtener_tenant)
tenant_bp.route('/<int:tenant_id>', methods=['PUT'])(TenantController.actualizar_tenant)

