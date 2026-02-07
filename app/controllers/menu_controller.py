from flask import Blueprint, render_template, request, jsonify
from app.models.product import Product, ProductVariant
from app.models.order import Order, OrderItem
from app.extensions import db

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
    Page Panier - Affiche les articles ajoutés au panier.
    Le panier est géré côté client via localStorage.
    """
    return render_template('book.html')


@menu_bp.route('/order', methods=['POST'])
def create_order():
    """
    Endpoint public pour créer une commande.
    Reçoit les données du formulaire de checkout en JSON.
    """
    data = request.get_json()
    
    # Validation des champs obligatoires
    if not data:
        return jsonify({'error': 'Données manquantes'}), 400
    
    if not data.get('customer_name') or not data.get('customer_phone') or not data.get('delivery_address'):
        return jsonify({'error': 'Nom, téléphone et adresse sont obligatoires'}), 400
    
    if not data.get('items') or len(data['items']) == 0:
        return jsonify({'error': 'Le panier est vide'}), 400
    
    try:
        # Calculer le total
        items_total = 0
        order_items_data = []
        
        for item in data['items']:
            quantity = float(item.get('quantity', 1))
            price = float(item.get('price', 0))
            line_total = price * quantity
            items_total += line_total
            
            order_items_data.append({
                'product_id': item.get('product_id'),
                'quantity': quantity,
                'unit': item.get('unit', 'piece'),
                'price': line_total
            })
        
        # Créer la commande
        # Include city in delivery address if provided
        city = data.get('city', '')
        full_address = f"{data['delivery_address']}, {city}" if city else data['delivery_address']
        
        new_order = Order(
            customer_name=data['customer_name'],
            customer_phone=data['customer_phone'],
            customer_email=data.get('customer_email', ''),
            delivery_address=full_address,
            total_price=items_total,
            status='En attente'
        )
        db.session.add(new_order)
        db.session.flush()  # Pour obtenir l'ID
        
        # Créer les items
        for item_data in order_items_data:
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item_data['product_id'],
                quantity=item_data['quantity'],
                unit=item_data['unit'],
                price=item_data['price']
            )
            db.session.add(order_item)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Commande créée avec succès',
            'order_id': new_order.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de la création: {str(e)}'}), 500