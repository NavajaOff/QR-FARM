"""Configuration module."""
import os

class Config:
    """Base configuration."""
    
    # Secret key para JWT y sesiones
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Configuración de la base de datos
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_USER = os.environ.get('DB_USER') or 'root'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or ''
    DB_NAME = os.environ.get('DB_NAME') or 'gestion_ganadera'
    
    # Configuración de JWT
    JWT_ACCESS_TOKEN_EXPIRES = 24 * 60 * 60  # 24 horas en segundos