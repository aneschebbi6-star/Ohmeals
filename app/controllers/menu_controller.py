from flask import Blueprint, render_template
from app.models.product import Product, ProductVariant

menu_bp = Blueprint('menu', __name__)

def prepare_product(p):
    """
    Prépare un produit avec ses variantes pour le template.
    Fix: Assure que les variantes sont triées et que toutes les infos (goût, unit) sont présentes.
    """
    variants = []
    
    # On récupère les variantes triées par position
    # La relation Product.variants a un order_by='ProductVariant.position'
    for v in p.variants:
        variants.append({
            'id': v.id,
            'name': v.variant_name,  # 'name' ou 'variant_name' selon compatibilité JS, ici on adapte pour correspondre au modèle
            'variant_name': v.variant_name, # Standard
            'unit': v.unit,
            'price': float(v.price), # Conversion float pour compatibilité JS
            'price_display': v.get_price_display(),
            'is_default': v.is_default,
            'position': v.position,
            'is_available': v.is_available
        })

    return {
        'id': p.id,
        'name': p.name,
        'description': p.description or '',
        'category': p.category,  # snack / plat / salade
        'taste': p.taste,       # sucré / salé
        'image': p.image or 'default_food.jpg', # Fallback si null
        'variants': sorted(variants, key=lambda x: x['position'])
    }

@menu_bp.route('/menu')
def menu():
    """
    Dynamic menu page - Affiche tous les produits actifs avec leurs variantes.
    
    FIX: Passe la liste complète 'products' au template.
    Le JavaScript (menu.js) s'attend à recevoir 'window.productsDB' contenant
    tous les produits pour effectuer le filtrage par catégorie et le tri.
    """
    # Récupérer tous les produits ACTIFS
    products = Product.query.filter_by(is_active=True).all()
    
    # Préparer la liste complète pour le JavaScript
    # Cela résout le bug où JS avait une liste vide ou des données incomplètes
    prepared_products = [prepare_product(p) for p in products]

    # (Optionnel) Préparer les listes spécifiques si vous voulez faire du rendu serveur
    # Mais pour le tri JS dynamique, on garde la liste 'products' comme source principale.
    snacks = [p for p in prepared_products if p['category'] == 'snack']
    plats = [p for p in prepared_products if p['category'] == 'plat']
    salades = [p for p in prepared_products if p['category'] == 'salade']

    return render_template(
        'menu.html',
        products=prepared_products,
        snacks=snacks,
        plats=plats,
        salades=salades
    )

@menu_bp.route('/book')
def book():
    """
    Page de commande / Réservation.
    Utilise la même logique de préparation pour afficher le catalogue complet.
    """
    products = Product.query.filter_by(is_active=True).all()
    prepared_products = [prepare_product(p) for p in products]

    return render_template(
        'book.html',
        products=prepared_products
    )