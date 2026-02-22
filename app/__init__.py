"""
OHMEALS Flask Application Factory.
Creates and configures the Flask app.
"""
import os
from flask import Flask
from werkzeug.security import generate_password_hash
try:
    from dotenv import load_dotenv
    # Load environment variables from .env file
    load_dotenv()
except ImportError:
    print("TIP: 'python-dotenv' not installed. Environment variables from .env will not be loaded automatically.")

from app.config import config
from app.extensions import db, login_manager, mail


def create_app(config_name='default'):
    """Application factory pattern."""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # ------------------------
    # Models
    # ------------------------
    from app.models.admin import Admin
    from app.models.site_setting import SiteSetting
    from app.models.expense import Expense

    # ------------------------
    # Flask-Login user loader
    # ------------------------
    @login_manager.user_loader
    def load_user(user_id):
        return Admin.query.get(int(user_id))

    # ------------------------
    # Context Processor (GLOBAL)
    # ------------------------
    @app.context_processor
    def inject_site_settings():
        settings = SiteSetting.query.all()
        site_settings = {s.key: s.value for s in settings}
        return dict(site_settings=site_settings)

    # ------------------------
    # Register blueprints
    # ------------------------
    from app.controllers.page_controller import page_bp
    from app.controllers.auth_controller import auth_bp
    from app.controllers.menu_controller import menu_bp
    from app.controllers.api_controller import api_bp
    from app.controllers.accounting_controller import accounting_bp

    app.register_blueprint(page_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(menu_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(accounting_bp)

    # ------------------------
    # Database init
    # ------------------------
    with app.app_context():
        db.create_all()

        # Create default admin if table is empty and env vars are present
        admin_pass = os.environ.get('ADMIN_PASSWORD')
        if not Admin.query.first():
            if not admin_pass:
                # Optionally log a warning or raise an error in production
                # For now, we'll just skip creation if password is missing
                print("WARNING: ADMIN_PASSWORD not set. Skip creating default admin.")
            else:
                admin_user = os.environ.get('ADMIN_USER', 'admin')
                admin_email = os.environ.get('ADMIN_EMAIL', 'admin@ohmeals.com')
                
                admin = Admin(
                    username=admin_user,
                    email=admin_email,
                    password=generate_password_hash(admin_pass),
                    must_change_password=True  # Force password change
                )
                db.session.add(admin)
                db.session.commit()
                print(f"Default admin '{admin_user}' created successfully.")

    return app
