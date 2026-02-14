"""
Expense model for OHMEALS accounting module.
Tracks manual business expenses with categories.
"""
from datetime import date
from app.extensions import db


# Expense categories for the business
EXPENSE_CATEGORIES = [
    'ingredients',   # Matières premières
    'salaires',      # Salaires
    'loyer',         # Loyer
    'equipement',    # Équipement
    'marketing',     # Marketing
    'livraison',     # Livraison
    'autre'          # Autre
]


class Expense(db.Model):
    """Expense model - manual business expense tracking."""
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Index on date for fast range queries
    __table_args__ = (
        db.Index('idx_expense_date', 'date'),
    )

    def __repr__(self):
        return f'<Expense {self.title} - {self.amount} DT>'

    def to_dict(self):
        """Serialize expense to dict for API responses."""
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'amount': float(self.amount),
            'date': self.date.isoformat(),
            'notes': self.notes or '',
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
