"""
API controller - REST API for React dashboard.
Prefix: /api
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models.admin import Admin
from app.models.product import Product, ProductVariant
from app.models.order import Order, OrderItem

# Blueprint API
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
    """Get all products with their variants."""
    products = Product.query.all()
    result = []

    for p in products:
        variants = []
        for v in p.variants:
            variants.append({
                "id": v.id,
                "variant_name": v.variant_name,
                "unit": v.unit,
                "price": v.price,
                "is_available": v.is_available,
                "is_default": v.is_default,
                "position": v.position,
                "price_display": v.get_price_display()
            })
        result.append({
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "category": p.category,
            "taste": getattr(p, 'taste', None),
            "image": p.image,
            "is_active": p.is_active,
            "variants": variants
        })

    return jsonify(result), 200


@api_bp.route('/products', methods=['POST'])
@login_required
def add_product():
    """Create new product with optional first variant."""
    data = request.get_json()
    # Vérification des champs obligatoires
    required_fields = ['name', 'category', 'variant_name', 'unit', 'price']
    for field in required_fields:
        val = data.get(field)
        if val is None or (isinstance(val, str) and not val.strip()):
            # Exception: price peut être 0
            if field == 'price' and val == 0:
                continue
            return jsonify({'error': f'Champ obligatoire manquant: {field}'}), 400

    try:
        price = float(data['price'])
        if price < 0:
            return jsonify({'error': 'Le prix ne peut pas être négatif'}), 400
    except ValueError:
        return jsonify({'error': 'Prix invalide'}), 400

    new_product = Product(
        name=data['name'],
        description=data.get('description'),
        category=data['category'],
        taste=data.get('taste'),
        image=data.get('image'),
        is_active=True
    )
    db.session.add(new_product)
    db.session.commit()

    variant_name = data.get('variant_name')
    if variant_name:
        variant = ProductVariant(
            variant_name=variant_name,
            price=price,
            unit=data.get('unit', 'piece'),
            is_default=True,
            position=1,
            product_id=new_product.id
        )
        db.session.add(variant)
        db.session.commit()

    return jsonify({'message': 'Produit ajouté avec succès', 'product_id': new_product.id}), 201


@api_bp.route('/products/<int:id>', methods=['PUT'])
@login_required
def update_product(id):
    """Update product info and optionally its variants."""
    product = Product.query.get_or_404(id)
    data = request.get_json()

    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.category = data.get('category', product.category)
    product.taste = data.get('taste', getattr(product, 'taste', None))
    product.image = data.get('image', product.image)
    if 'is_active' in data:
        product.is_active = bool(data['is_active'])

    if data.get('variants'):
        for vdata in data['variants']:
            if vdata.get('id'):
                variant = ProductVariant.query.get(vdata['id'])
                if variant:
                    variant.variant_name = vdata.get('variant_name', variant.variant_name)
                    variant.unit = vdata.get('unit', variant.unit)
                    if vdata.get('price') is not None:
                        variant.price = float(vdata['price'])
                    variant.is_available = vdata.get('is_available', variant.is_available)
                    variant.is_default = vdata.get('is_default', variant.is_default)
                    variant.position = vdata.get('position', variant.position)
            else:
                new_variant = ProductVariant(
                    product_id=product.id,
                    variant_name=vdata['variant_name'],
                    unit=vdata['unit'],
                    price=float(vdata['price']),
                    is_available=vdata.get('is_available', True),
                    is_default=vdata.get('is_default', False),
                    position=vdata.get('position', 0)
                )
                db.session.add(new_variant)

    db.session.commit()
    return jsonify({'message': 'Produit et variantes modifiés avec succès'})


@api_bp.route('/products/<int:id>', methods=['DELETE'])
@login_required
def delete_product(id):
    """Delete product and all its variants."""
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Produit et variantes supprimés avec succès'})


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
    db.session.flush()

    for item_data in order_items:
        order_item = OrderItem(order_id=new_order.id, **item_data)
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
