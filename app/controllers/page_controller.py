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
    all_products = Product.query.filter_by(is_active=True).all()

    # 2. Sélectionner max 2 produits par catégorie, max 6 produits au total
    category_counts = {}
    selected_products = []
    remaining_products = []
    
    for p in all_products:
        if category_counts.get(p.category, 0) < 2:
            selected_products.append(p)
            category_counts[p.category] = category_counts.get(p.category, 0) + 1
        else:
            remaining_products.append(p)
            
    if len(selected_products) < 6:
        needed = 6 - len(selected_products)
        selected_products.extend(remaining_products[:needed])
        
    selected_products = selected_products[:6]

    # 3. Préparer les données en utilisant to_dict() pour la consistance
    prepared_products = [p.to_dict() for p in selected_products]

    # 4. Rendu
    return render_template(
        'index.html',
        products=prepared_products
    )


@page_bp.route('/about')
def about():
    """About page."""
    return render_template('about.html')