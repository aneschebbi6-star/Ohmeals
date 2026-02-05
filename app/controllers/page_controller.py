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
    # 1. Récupérer TOUS les produits actifs (pas .limit(6) si tu veux que les filtres marchent)
    products = Product.query.filter_by(is_active=True).all()

    # 2. Préparer les données EXACTEMENT comme le JavaScript les attend
    prepared_products = []

    for p in products:
        # --- Ici, on construit la liste des variantes ---
        # Le JS a besoin de 'variants': [...] pour boucler dessus
        variants_data = []
        
        if p.variants:
            for v in p.variants:
                variants_data.append({
                    'id': v.id,
                    'variant_name': v.variant_name,
                    'unit': v.unit,
                    'price': float(v.price),
                    'is_available': v.is_available,
                    'is_default': v.is_default
                })

        # --- On construit l'objet produit complet ---
        product_dict = {
            'id': p.id,
            'name': p.name,
            'description': p.description or '',
            'category': p.category,       # 'snack', 'plat', etc.
            'taste': p.taste,             # 'sucré', 'salé'
            'image': p.image,
            # C'est cette clé 'variants' qui est cruciale pour ton menu.js !
            'variants': variants_data
        }
        
        prepared_products.append(product_dict)

    # 3. Rendu
    # IMPORTANT : On envoie 'products=prepared_products' et non 'plats'
    return render_template(
        'index.html',
        products=prepared_products
    )


@page_bp.route('/about')
def about():
    """About page."""
    return render_template('about.html')