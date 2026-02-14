"""
Admin (User) model for OHMEALS.
All users are administrators with full access.
"""
from flask_login import UserMixin
from app.extensions import db


class Admin(UserMixin, db.Model):
    """Admin user model - all users are admins."""
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    reset_code = db.Column(db.String(5), nullable=True)
    last_code_time = db.Column(db.Integer, nullable=True)
    must_change_password = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Admin {self.username}>'
