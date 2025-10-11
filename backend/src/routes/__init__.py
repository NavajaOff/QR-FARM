"""Routes module."""
from flask import Flask
from src.database.db import init_db
from src.routes.potrero_routes import potrero_bp
from src.routes.usuario_routes import usuario_bp
from flask_cors import CORS

def create_app(config_class=None):
    """Create Flask application."""
    app = Flask(__name__)
    
    # Load config
    if config_class is None:
        # Load default config
        app.config.from_object('src.config.Config')
    else:
        # Load provided config
        app.config.from_object(config_class)
    
    # Initialize database
    init_db(app)
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(potrero_bp, url_prefix='/api/potreros')
    app.register_blueprint(usuario_bp, url_prefix='/api/usuarios')
    
    return app
