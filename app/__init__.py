"""
OHMEALS Flask Application Factory.
Creates and configures the Flask app.
"""
from flask import Flask
from werkzeug.security import generate_password_hash

from app.config import config
from app.extensions import db, login_manager, mail


def create_app(config_name='default'):
    """Application factory pattern."""
    app = Flask(
        __name__,
        template_folder='../templates',
        static_folder='../static'
    )
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
    # User loader for Flask-Login
    from app.models.admin import Admin
    
    @login_manager.user_loader
    def load_user(user_id):
        return Admin.query.get(int(user_id))
    
    # Register blueprints
    from app.controllers.page_controller import page_bp
    from app.controllers.auth_controller import auth_bp
    from app.controllers.menu_controller import menu_bp
    from app.controllers.api_controller import api_bp
    
    app.register_blueprint(page_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(menu_bp)
    app.register_blueprint(api_bp)
    
    # Create database tables and default admin
    with app.app_context():
        db.create_all()
        
        # Create default admin if not exists
        if not Admin.query.filter_by(username='anes').first():
            admin = Admin(
                username='anes',
                email='aneschebbi6@gmail.com',
                password=generate_password_hash('anes123')
            )
            db.session.add(admin)
            db.session.commit()
    
    return app
