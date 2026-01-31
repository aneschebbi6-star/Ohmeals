"""
Product model for OHMEALS.
Supports different unit types: kilo, piece, personne.
"""
from app.extensions import db


class Product(db.Model):
    """Product model with category and unit support."""
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Category: 'snack' or 'plat'
    category = db.Column(db.String(50), nullable=False)
    
    # Unit: 'kilo', 'piece', or 'personne'
    unit = db.Column(db.String(20), nullable=False)
    
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(200), nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Product {self.name} ({self.unit})>'

    def get_price_display(self):
        """Return formatted price with unit."""
        unit_labels = {
            'kilo': 'DT / kilo',
            'piece': 'DT / pièce',
            'personne': 'DT / personne'
        }
        return f'{self.price} {unit_labels.get(self.unit, "DT")}'

    def calculate_total(self, quantity):
        """Calculate total price for given quantity."""
        return self.price * quantity
