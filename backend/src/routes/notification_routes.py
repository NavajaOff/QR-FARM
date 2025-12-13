"\"\"\"Routes for notification endpoints.\"\"\""
from flask import Blueprint

from src.controllers.notification_controller import NotificationController


notification_bp = Blueprint('notificaciones', __name__)

notification_bp.route('/proximas', methods=['GET'])(NotificationController.get_proximas)

