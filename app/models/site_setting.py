from app.extensions import db


class SiteSetting(db.Model):
    __tablename__ = "site_settings"

    id = db.Column(db.Integer, primary_key=True)

    # clé unique du setting
    key = db.Column(db.String(100), unique=True, nullable=False)

    # valeur du setting (texte long autorisé)
    value = db.Column(db.Text, nullable=True)

    # optionnel : description interne (admin)
    description = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<SiteSetting {self.key}>"

    @staticmethod
    def get(key, default=""):
        setting = SiteSetting.query.filter_by(key=key).first()
        return setting.value if setting else default
