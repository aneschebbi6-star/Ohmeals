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
    # Récupérer 6 produits actifs
    products = (
        Product.query
        .filter_by(is_active=True)
        .limit(6)
        .all()
    )

    plats = []

    for p in products:
        # Variante par défaut (ou première disponible)
        default_variant = None
        for v in p.variants:
            if v.is_available and v.is_default:
                default_variant = v
                break

        # Si aucune variante par défaut, prendre la première disponible
        if not default_variant:
            for v in p.variants:
                if v.is_available:
                    default_variant = v
                    break

        plats.append({
            'id': p.id,
            'name': p.name,
            'description': p.description or '',
            'category': p.category,     # snack / plat / salade
            'taste': p.taste,           # sucré / salé
            'image': p.image or 'f1.png',

            # Infos affichables (via variante)
            'default_variant': {
                'id': default_variant.id if default_variant else None,
                'name': default_variant.variant_name if default_variant else '',
                'unit': default_variant.unit if default_variant else '',
                'price': default_variant.price if default_variant else 0,
                'price_display': default_variant.get_price_display()
                if default_variant else ''
            }
        })

    return render_template(
        'index.html',
        plats=plats,
        active_category='*'
    )


@page_bp.route('/about')
def about():
    """About page."""
    return render_template('about.html')
