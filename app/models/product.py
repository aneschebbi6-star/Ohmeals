"""
Product and ProductVariant models for OHMEALS.
Supports multiple variants, unit types, categories, and pricing.
"""
from app.extensions import db

# ------------------------
# Product table
# ------------------------


class Product(db.Model):
    """Product model with category support."""
    __tablename__ = 'products'

    CATEGORY_CHOICES = ('snack', 'plat', 'salade')  # Étendu avec 'salade'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False)  # 'snack', 'plat', 'salade'
    taste = db.Column(db.String(20), nullable=True)      # 'sucré' or 'salé'
    image = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    # Relation 1-n vers ProductVariant
    variants = db.relationship(
        'ProductVariant',
        backref='product',
        cascade='all, delete-orphan',
        order_by='ProductVariant.position'
    )

    def __repr__(self):
        return f'<Product {self.name} ({self.category})>'

    # ------------------------
    # Méthodes utilitaires
    # ------------------------
    def get_default_variant(self):
        """Return the default variant if exists, else first variant."""
        if self.variants:
            for v in self.variants:
                if v.is_default:
                    return v
            return self.variants[0]
        return None

    def get_price_display(self):
        """Return price of default variant formatted with unit."""
        variant = self.get_default_variant()
        if variant:
            return variant.get_price_display()
        return "N/A"

# ------------------------
# ProductVariant table
# ------------------------


class ProductVariant(db.Model):
    """ProductVariant model linked to Product."""
    __tablename__ = 'product_variants'

    UNIT_CHOICES = ('kilo', 'piece', 'personne')

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    variant_name = db.Column(db.String(50), nullable=False)  # ex: "Petit 10cm"
    unit = db.Column(db.String(20), nullable=False)          # 'kilo', 'piece', 'personne'
    price = db.Column(db.Float, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    is_default = db.Column(db.Boolean, default=False)
    position = db.Column(db.Integer, default=0)              # Ordre d’affichage

    def __repr__(self):
        return f'<Variant {self.variant_name} ({self.unit}) - {self.price} DT>'

    # ------------------------
    # Méthodes utilitaires
    # ------------------------
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