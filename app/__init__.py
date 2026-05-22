import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

# Global instances of extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_class=None):
    app = Flask(__name__)
    
    # Load configuration
    if config_class is None:
        from config import Config
        app.config.from_object(Config)
    else:
        app.config.from_object(config_class)
        
    # Initialize extensions with app
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Configure authentication login view and alert styles
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'
    
    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    
    # Register custom template filters
    @app.template_filter('to_ist')
    def to_ist(dt):
        if not dt:
            return ""
        from datetime import timedelta
        return dt + timedelta(hours=5, minutes=30)
    
    # Create database tables if they do not exist
    with app.app_context():
        db.create_all()
        
    return app
