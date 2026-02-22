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
    # 1. Récupérer TOUS les produits actifs
    products = Product.query.filter_by(is_active=True).all()

    # 2. Préparer les données en utilisant to_dict() pour la consistance
    prepared_products = [p.to_dict() for p in products]

    # 3. Rendu
    return render_template(
        'index.html',
        products=prepared_products
    )


@page_bp.route('/about')
def about():
    """About page."""
    return render_template('about.html')