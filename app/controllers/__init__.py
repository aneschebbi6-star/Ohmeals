"""
Controllers package for OHMEALS.
Import all blueprints here for registration.
"""
from app.controllers.page_controller import page_bp
from app.controllers.auth_controller import auth_bp
from app.controllers.menu_controller import menu_bp
from app.controllers.api_controller import api_bp

__all__ = ['page_bp', 'auth_bp', 'menu_bp', 'api_bp']
