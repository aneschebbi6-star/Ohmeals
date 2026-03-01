"""
Authentication controller - admin login/logout.
Routes: /login, /logout, /forgot-password, /dashboard
"""
from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Message
import random
import string
import time

from app.extensions import db, mail
from app.models.admin import Admin
from app.utils import is_valid_password

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = Admin.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.must_change_password:
                return redirect(url_for('auth.change_password'))
            return redirect(url_for('auth.dashboard'))
        
        return render_template('login.html', error="Identifiants incorrects")
    
    return render_template('login.html')


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Force password change."""
    if not current_user.must_change_password:
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        is_valid, error_msg = is_valid_password(new_password)
        if not is_valid:
            return render_template('dashboard/change_password.html', error=error_msg)
        
        if new_password != confirm_password:
            return render_template('dashboard/change_password.html', error="Les mots de passe ne correspondent pas.")

        current_user.password = generate_password_hash(new_password)
        current_user.must_change_password = False
        db.session.commit()
        
        return redirect(url_for('auth.dashboard'))

    return render_template('dashboard/change_password.html')


@auth_bp.before_request
def check_password_change():
    """Ensure user changes password if required."""
    if current_user.is_authenticated and current_user.must_change_password:
        if request.endpoint not in ['auth.change_password', 'auth.logout', 'static']:
            return redirect(url_for('auth.change_password'))


@auth_bp.route('/dashboard')
@login_required
def dashboard():
    """Admin dashboard page."""
    return render_template('dashboard/dashboard.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Admin logout."""
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Password reset flow."""
    if request.method == 'POST':
        email = request.form.get('email')
        code = request.form.get('code')
        new_password = request.form.get('new_password')

        user = Admin.query.filter_by(email=email).first()
        if not user:
            return "EMAIL_NOT_FOUND"

        # Step 1: Send code
        if email and not code and not new_password:
            now = int(time.time())
            if user.last_code_time and now - user.last_code_time < 60:
                return "WAIT_1_MIN"

            code_generated = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
            user.reset_code = code_generated
            user.last_code_time = now
            db.session.commit()

            try:
                msg = Message(
                    subject="Code de réinitialisation",
                    recipients=[email],
                    body=f"Bonjour {user.username},\n\nVotre code de réinitialisation est : {code_generated}\n\nMerci."
                )
                mail.send(msg)
                print(f"Email envoyé avec succès à {email}")
            except Exception as e:
                print(f"Erreur d'envoi d'email à {email}: {str(e)}")
            return "CODE_SENT"

        # Step 2: Verify code
        if email and code and not new_password:
            if code != user.reset_code:
                return "CODE_INCORRECT"
            return "CODE_CORRECT"

        # Step 3: Change password
        if email and code and new_password:
            if code != user.reset_code:
                return "CODE_INCORRECT"
            is_valid, error_msg = is_valid_password(new_password)
            if not is_valid:
                return error_msg  # Or handle error appropriately for frontend (e.g., specific error code)

            user.password = generate_password_hash(new_password)
            user.reset_code = None
            user.must_change_password = False
            db.session.commit()
            return "PASSWORD_CHANGED"

    return render_template('forgot_password.html')
