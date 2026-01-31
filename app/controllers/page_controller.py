"""
Page controller - public routes.
Routes: /, /about
"""
from flask import Blueprint, render_template
from app.models.product import Product

page_bp = Blueprint('page', __name__)


@page_bp.route('/')
def index():
    """Home page with featured products."""
    # Get 6 active products for homepage
    products = Product.query.filter_by(is_active=True).limit(6).all()
    
    # Prepare products for template
    plats = []
    for p in products:
        plats.append({
            'id': p.id,
            'name': p.name,
            'description': p.description or '',
            'category': p.category,  # Use actual category (snack/plat)
            'unit': p.unit,
            'price': p.price,
            'image': p.image or 'f1.png',
            'prices': {p.unit: p.price}
        })
    
    return render_template('index.html', plats=plats, active_category='*')


@page_bp.route('/about')
def about():
    """About page."""
    return render_template('about.html')
