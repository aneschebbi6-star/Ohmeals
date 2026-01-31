"""
API controller - REST API for React dashboard.
Prefix: /api
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models.admin import Admin
from app.models.product import Product
from app.models.order import Order, OrderItem

api_bp = Blueprint('api', __name__, url_prefix='/api')


# ============================================
# ADMIN CRUD
# ============================================

@api_bp.route('/admins', methods=['GET'])
@login_required
def get_admins():
    """Get all admins."""
    admins = Admin.query.all()
    return jsonify([
        {'id': a.id, 'username': a.username, 'email': a.email}
        for a in admins
    ])


@api_bp.route('/admins', methods=['POST'])
@login_required
def add_admin():
    """Create new admin."""
    data = request.get_json()
    
    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Tous les champs sont requis'}), 400
    
    if Admin.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username déjà utilisé'}), 400
    
    if Admin.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email déjà utilisé'}), 400

    new_admin = Admin(
        username=data['username'],
        email=data['email'],
        password=generate_password_hash(data['password'])
    )
    db.session.add(new_admin)
    db.session.commit()
    
    return jsonify({'message': 'Admin créé avec succès', 'id': new_admin.id}), 201


@api_bp.route('/admins/<int:id>', methods=['PUT'])
@login_required
def update_admin(id):
    """Update admin."""
    admin = Admin.query.get_or_404(id)
    data = request.get_json()
    
    admin.username = data.get('username', admin.username)
    admin.email = data.get('email', admin.email)
    
    if data.get('password') and data['password'].strip():
        admin.password = generate_password_hash(data['password'])
    
    db.session.commit()
    return jsonify({'message': 'Admin modifié avec succès'})


@api_bp.route('/admins/<int:id>', methods=['DELETE'])
@login_required
def delete_admin(id):
    """Delete admin."""
    admin = Admin.query.get_or_404(id)
    db.session.delete(admin)
    db.session.commit()
    return jsonify({'message': 'Admin supprimé avec succès'})


# ============================================
# PRODUCT CRUD
# ============================================

@api_bp.route('/products', methods=['GET'])
@login_required
def get_products():
    """Get all products."""
    products = Product.query.all()
    return jsonify([
        {
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'category': p.category,
            'unit': p.unit,
            'price': p.price,
            'image': p.image,
            'is_active': p.is_active
        }
        for p in products
    ])


@api_bp.route('/products', methods=['POST'])
@login_required
def add_product():
    """Create new product."""
    data = request.get_json()
    
    if not data.get('name') or not data.get('category') or not data.get('unit') or data.get('price') is None:
        return jsonify({'error': 'Champs obligatoires manquants'}), 400

    new_product = Product(
        name=data['name'],
        description=data.get('description', ''),
        category=data['category'],
        unit=data['unit'],
        price=float(data['price']),
        image=data.get('image', ''),
        is_active=data.get('is_active', True)
    )
    db.session.add(new_product)
    db.session.commit()
    
    return jsonify({'message': 'Produit créé avec succès', 'id': new_product.id}), 201


@api_bp.route('/products/<int:id>', methods=['PUT'])
@login_required
def update_product(id):
    """Update product."""
    product = Product.query.get_or_404(id)
    data = request.get_json()
    
    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.category = data.get('category', product.category)
    product.unit = data.get('unit', product.unit)
    
    if data.get('price') is not None:
        product.price = float(data['price'])
    
    product.image = data.get('image', product.image)
    
    if 'is_active' in data:
        product.is_active = bool(data['is_active'])
    
    db.session.commit()
    return jsonify({'message': 'Produit modifié avec succès'})


@api_bp.route('/products/<int:id>', methods=['DELETE'])
@login_required
def delete_product(id):
    """Delete product."""
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Produit supprimé avec succès'})


# ============================================
# ORDER CRUD
# ============================================

@api_bp.route('/orders', methods=['GET'])
@login_required
def get_orders():
    """Get all orders."""
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify([
        {
            'id': o.id,
            'customer_name': o.customer_name,
            'customer_phone': o.customer_phone,
            'customer_email': o.customer_email,
            'delivery_address': o.delivery_address,
            'delivery_fee': o.delivery_fee,
            'total_price': o.total_price,
            'status': o.status,
            'created_at': o.created_at.isoformat() if o.created_at else None,
            'items': [
                {
                    'id': item.id,
                    'product_id': item.product_id,
                    'product_name': item.product.name if item.product else None,
                    'quantity': item.quantity,
                    'unit': item.unit,
                    'price': item.price
                }
                for item in o.items
            ]
        }
        for o in orders
    ])


@api_bp.route('/orders', methods=['POST'])
@login_required
def add_order():
    """Create new order with items."""
    data = request.get_json()
    
    if not data.get('customer_name') or not data.get('customer_phone') or not data.get('delivery_address'):
        return jsonify({'error': 'Informations client manquantes'}), 400
    
    if not data.get('items') or len(data['items']) == 0:
        return jsonify({'error': 'La commande doit contenir au moins un produit'}), 400

    # Calculate total from items
    items_total = 0
    order_items = []
    
    for item_data in data['items']:
        product = Product.query.get(item_data['product_id'])
        if not product:
            return jsonify({'error': f'Produit {item_data["product_id"]} non trouvé'}), 400
        
        quantity = float(item_data['quantity'])
        item_price = product.price * quantity
        items_total += item_price
        
        order_items.append({
            'product_id': product.id,
            'quantity': quantity,
            'unit': product.unit,
            'price': item_price
        })

    delivery_fee = float(data.get('delivery_fee', 0))
    total_price = items_total + delivery_fee

    # Create order
    new_order = Order(
        customer_name=data['customer_name'],
        customer_phone=data['customer_phone'],
        customer_email=data.get('customer_email', ''),
        delivery_address=data['delivery_address'],
        delivery_fee=delivery_fee,
        total_price=total_price,
        status='En attente'
    )
    db.session.add(new_order)
    db.session.flush()  # Get order ID

    # Create order items
    for item_data in order_items:
        order_item = OrderItem(
            order_id=new_order.id,
            **item_data
        )
        db.session.add(order_item)

    db.session.commit()
    
    return jsonify({'message': 'Commande créée avec succès', 'id': new_order.id}), 201


@api_bp.route('/orders/<int:id>', methods=['PUT'])
@login_required
def update_order(id):
    """Update order status."""
    order = Order.query.get_or_404(id)
    data = request.get_json()
    
    order.status = data.get('status', order.status)
    order.customer_name = data.get('customer_name', order.customer_name)
    order.customer_phone = data.get('customer_phone', order.customer_phone)
    order.customer_email = data.get('customer_email', order.customer_email)
    order.delivery_address = data.get('delivery_address', order.delivery_address)
    
    db.session.commit()
    return jsonify({'message': 'Commande modifiée avec succès'})


@api_bp.route('/orders/<int:id>', methods=['DELETE'])
@login_required
def delete_order(id):
    """Delete order."""
    order = Order.query.get_or_404(id)
    db.session.delete(order)
    db.session.commit()
    return jsonify({'message': 'Commande supprimée avec succès'})


# ============================================
# STATS (for dashboard)
# ============================================

@api_bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    """Get dashboard statistics."""
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='En attente').count()
    total_products = Product.query.count()
    active_products = Product.query.filter_by(is_active=True).count()
    total_admins = Admin.query.count()
    
    # Calculate total revenue
    orders = Order.query.all()
    total_revenue = sum(o.total_price for o in orders)
    
    return jsonify({
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_products': total_products,
        'active_products': active_products,
        'total_admins': total_admins,
        'total_revenue': total_revenue
    })
