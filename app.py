from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import random
import string

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------------------
# Database
# ---------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///traiteur.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ---------------------------
# Flask-login
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
# User Model
# ---------------------------


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    reset_code = db.Column(db.String(5), nullable=True)  # Code temporaire


# ---------------------------
# Créer DB et compte admin
# ---------------------------
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='anes').first():
        admin = User(
            username='anes',
            password=generate_password_hash('anes123'),
            email='aneschebbi6@gmail.com'
        )
        db.session.add(admin)
        db.session.commit()

# ---------------------------
# Flask-login loader
# ---------------------------


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
# Login
# ---------------------------


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
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
# Forgot Password AJAX
# ---------------------------

# @app.route('/forgot-password', methods=['GET', 'POST'])
# def forgot_password():
#     if request.method == 'POST':
#         email = request.form.get('email')
#         code = request.form.get('code')
#         new_password = request.form.get('new_password')

#         user = User.query.filter_by(email=email).first()
#         if not user:
#             return "EMAIL_NOT_FOUND"

#         # Étape 1 : envoyer le code
#         if email and not code and not new_password:
#             code_generated = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
#             user.reset_code = code_generated
#             user.code_timestamp = datetime.utcnow()  # Ajouter timestamp pour limiter renvoi
#             db.session.commit()

#             # Envoyer email
#             msg = Message(
#                 subject="Code de réinitialisation",
#                 recipients=[email],
#                 body=f"Bonjour {user.username},\n\nVotre code de réinitialisation est : {code_generated}\n\nMerci."
#             )
#             mail.send(msg)
#             return "CODE_SENT"

#         # Étape 2 : vérifier le code
#         if email and code and not new_password:
#             if code != user.reset_code:
#                 return "CODE_INCORRECT"
#             else:
#                 return "CODE_CORRECT"

#         # Étape 3 : changer le mot de passe
#         if email and code and new_password:
#             if code != user.reset_code:
#                 return "CODE_INCORRECT"

#             # Validation mot de passe : lettres + chiffres, >= 5 caractères
#             if len(new_password) < 5 or not any(c.isalpha() for c in new_password) or not any(c.isdigit() for c in new_password):
#                 return "PASSWORD_INVALID"

#             # Changer mot de passe
#             user.password = generate_password_hash(new_password)
#             user.reset_code = None
#             db.session.commit()

#             # Afficher page password_changed.html immédiatement
#             return render_template('password_changed.html')

#     # GET : afficher page forgot_password
#     return render_template('forgot_password.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        code = request.form.get('code')
        new_password = request.form.get('new_password')

        user = User.query.filter_by(email=email).first()
        if not user:
            return "EMAIL_NOT_FOUND"

        # -------------------
        # Étape 1 : envoyer le code
        # -------------------
        if email and not code and not new_password:
            import time
            now = int(time.time())
            # Stocker le timestamp du dernier envoi dans l'utilisateur si pas déjà fait
            if hasattr(user, 'last_code_time') and now - user.last_code_time < 60:
                return "WAIT_1_MIN"

            code_generated = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
            user.reset_code = code_generated
            # Ajouter un attribut temporaire pour le timestamp
            user.last_code_time = now
            db.session.commit()

            # Envoyer email
            msg = Message(
                subject="Code de réinitialisation",
                recipients=[email],
                body=f"Bonjour {user.username},\n\nVotre code de réinitialisation est : {code_generated}\n\nMerci."
            )
            mail.send(msg)
            return "CODE_SENT"

        # -------------------
        # Étape 2 : vérifier le code
        # -------------------
        if email and code and not new_password:
            if code != user.reset_code:
                return "CODE_INCORRECT"
            return "CODE_CORRECT"

        # -------------------
        # Étape 3 : changer le mot de passe
        # -------------------
        if email and code and new_password:
            if code != user.reset_code:
                return "CODE_INCORRECT"

            # Validation côté serveur : lettres + chiffres + >=5 caractères
            if len(new_password) < 5 or not any(c.isalpha() for c in new_password) or not any(c.isdigit() for c in new_password):
                return "PASSWORD_INVALID"

            user.password = generate_password_hash(new_password)
            user.reset_code = None
            db.session.commit()
            return "PASSWORD_CHANGED"

    # GET : afficher la page forgot_password
    return render_template('forgot_password.html')


# ---------------------------
# Run
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True)
