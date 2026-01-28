from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import random
import string
import time

# ---------------------------
# Flask app
# ---------------------------
app = Flask(__name__)
app.secret_key = "secret123"

# ---------------------------
# Database
# ---------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///traiteur.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ---------------------------
# Flask-Login
# ---------------------------
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

# ---------------------------
# Flask-Mail
# ---------------------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'aneschebbi6@gmail.com'
app.config['MAIL_PASSWORD'] = 'oicz kpzi ieak mulf'  # mot de passe application
app.config['MAIL_DEFAULT_SENDER'] = 'aneschebbi6@gmail.com'
mail = Mail(app)

# ---------------------------
# Admin Model
# ---------------------------


class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    reset_code = db.Column(db.String(5), nullable=True)
    last_code_time = db.Column(db.Integer, nullable=True)  # timestamp dernier code


# ---------------------------
# Création DB et admin initial
# ---------------------------
with app.app_context():
    db.create_all()
    if not Admin.query.filter_by(email='aneschebbi6@gmail.com').first():
        admin = Admin(
            email='aneschebbi6@gmail.com',
            password=generate_password_hash('anes123')
        )
        db.session.add(admin)
        db.session.commit()

# ---------------------------
# Flask-login loader
# ---------------------------


@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# ---------------------------
# Routes publiques
# ---------------------------


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/menu')
def menu():
    return render_template('menu.html')


@app.route('/book')
def book():
    return render_template('book.html')

# ---------------------------
# Login / Logout
# ---------------------------


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        admin = Admin.query.filter_by(email=email).first()
        if admin and check_password_hash(admin.password, password):
            login_user(admin)
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Login incorrect")
    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard/dashboard.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ---------------------------
# Mot de passe oublié
# ---------------------------


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        code = request.form.get('code')
        new_password = request.form.get('new_password')

        admin = Admin.query.filter_by(email=email).first()
        if not admin:
            return "EMAIL_NOT_FOUND"

        # Étape 1 : envoyer le code
        if email and not code and not new_password:
            now = int(time.time())
            if admin.last_code_time and now - admin.last_code_time < 60:
                return "WAIT_1_MIN"

            code_generated = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
            admin.reset_code = code_generated
            admin.last_code_time = now
            db.session.commit()

            msg = Message(
                subject="Code de réinitialisation",
                recipients=[email],
                body=f"Bonjour,\n\nVotre code de réinitialisation est : {code_generated}\n\nMerci."
            )
            mail.send(msg)
            return "CODE_SENT"

        # Étape 2 : vérifier le code
        if email and code and not new_password:
            if code != admin.reset_code:
                return "CODE_INCORRECT"
            return "CODE_CORRECT"

        # Étape 3 : changer le mot de passe
        if email and code and new_password:
            if code != admin.reset_code:
                return "CODE_INCORRECT"

            if len(new_password) < 5 or not any(c.isalpha() for c in new_password) or not any(c.isdigit() for c in new_password):
                return "PASSWORD_INVALID"

            # Vérification : mot de passe différent de l'ancien
            if check_password_hash(admin.password, new_password):
                return "PASSWORD_SAME_AS_OLD"

            admin.password = generate_password_hash(new_password)
            admin.reset_code = None
            admin.last_code_time = None
            db.session.commit()
            return "PASSWORD_CHANGED"

    return render_template('forgot_password.html')

# ---------------------------
# Ajouter un nouvel admin
# ---------------------------


@app.route('/add-admin', methods=['GET', 'POST'])
@login_required
def add_admin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if Admin.query.filter_by(email=email).first():
            return "ADMIN_EXISTS"
        new_admin = Admin(
            email=email,
            password=generate_password_hash(password)
        )
        db.session.add(new_admin)
        db.session.commit()
        return "ADMIN_ADDED"
    return render_template('add_admin.html')


# ---------------------------
# Run
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True)
