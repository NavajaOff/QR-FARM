"""Routes module."""
from flask import Flask
from src.database.db import init_db
from src.routes.potrero_routes import potrero_bp

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
    
    # Register blueprints
    app.register_blueprint(potrero_bp)
    
    return app
