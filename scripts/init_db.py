# init_db.py
from app import app, db   # app = ton Flask app, db = SQLAlchemy()

with app.app_context():
    db.create_all()
    print("La base de données a été créée avec succès !")
