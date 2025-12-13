# Servicio Cargo
from typing import List, Optional
from ..database.db import get_connection
from ..models.cargo import Cargo
import logging

logger = logging.getLogger(__name__)


class CargoService:
    @staticmethod
    def obtener_todos_cargos() -> List[Cargo]:
        """Obtiene todos los cargos disponibles."""
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            
            sql = "SELECT * FROM cargos ORDER BY id ASC"
            cursor.execute(sql)
            results = cursor.fetchall()
            
            cargos = []
            for result in results:
                cargos.append(Cargo.from_dict(result))
            
            return cargos
            
        except Exception as e:
            logger.error(f"Error al obtener cargos: {e}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()
