"""
Flask extensions initialization.
Extensions are initialized without app context here,
then bound to app in create_app().
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

# Database
db = SQLAlchemy()

# Login manager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'

# Mail
mail = Mail()
