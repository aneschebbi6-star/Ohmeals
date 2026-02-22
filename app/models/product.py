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
    image = db.Column(db.Text, nullable=True)             # Legacy primary image
    video_url = db.Column(db.Text, nullable=True)         # Optional video URL
    is_active = db.Column(db.Boolean, default=True)
    discount = db.Column(db.Float, default=0)  # Percentage discount (0-100)

    # Relation 1-n vers ProductVariant
    variants = db.relationship(
        'ProductVariant',
        backref='product',
        cascade='all, delete-orphan',
        order_by='ProductVariant.position'
    )

    # Relation 1-n vers ProductImage (galerie multi-images)
    images = db.relationship(
        'ProductImage',
        backref='product',
        cascade='all, delete-orphan',
        order_by='ProductImage.position'
    )

    def __repr__(self):
        return f'<Product {self.name} ({self.category})>'

    def get_primary_image(self):
        """Return the primary image URL (from gallery or legacy field)."""
        if self.images:
            primary = next((img for img in self.images if img.is_primary), None)
            if primary:
                return primary.image_url
            return self.images[0].image_url
        return self.image

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

    def to_dict(self):
        """
        Convert product and variants to dictionary for frontend/JSON.
        """
        variants = []
        for v in self.variants:
            variants.append({
                'id': v.id,
                'name': v.variant_name,
                'variant_name': v.variant_name,
                'unit': v.unit,
                'price': float(v.price),
                'price_display': v.get_price_display(),
                'is_default': v.is_default,
                'position': v.position,
                'is_available': v.is_available,
                'stock_quantity': v.stock_quantity,
                'track_stock': v.track_stock,
                'availability_status': v.get_availability_status(),
                'is_in_stock': v.is_in_stock()
            })
        
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description or '',
            'category': self.category,
            'taste': self.taste,
            'image': self.get_primary_image() or 'default_food.jpg',
            'video_url': self.video_url,
            'discount': self.discount,
            'variants': sorted(variants, key=lambda x: x['position']),
            'images': [{'image_url': img.image_url, 'is_primary': img.is_primary, 'position': img.position} for img in self.images]
        }

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
    stock_quantity = db.Column(db.Integer, default=100)      # Stock disponible
    track_stock = db.Column(db.Boolean, default=True)        # Désactiver si stock illimité

    def is_in_stock(self):
        """Check if variant is available and in stock."""
        if not self.is_available:
            return False
        if self.track_stock:
            return self.stock_quantity > 0
        return True

    def get_availability_status(self):
        """Return status string for UI."""
        if not self.is_available:
            return 'indisponible'
        if self.track_stock:
            if self.stock_quantity <= 0:
                return 'épuisé'
            if self.stock_quantity < 5:
                return 'limité'
        return 'en_stock'

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


# ------------------------
# ProductImage table
# ------------------------


class ProductImage(db.Model):
    """ProductImage model - multiple images per product."""
    __tablename__ = 'product_images'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    image_url = db.Column(db.Text, nullable=False)
    position = db.Column(db.Integer, default=0)       # Ordre d'affichage
    is_primary = db.Column(db.Boolean, default=False)  # Image principale

    def __repr__(self):
        return f'<ProductImage product={self.product_id} pos={self.position} primary={self.is_primary}>'