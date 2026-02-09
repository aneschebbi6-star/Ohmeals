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
from app.models.site_setting import SiteSetting  

# Blueprint API
api_bp = Blueprint('api', __name__, url_prefix='/api')


# ============================================
# SITE SETTINGS (GLOBAL CONFIG)
# ============================================

ALLOWED_SETTINGS_KEYS = {
    "index_description",
    "about_description",
    "footer_description",
    "phone",
    "email",
    "address",
    "facebook_url",
    "twitter_url",
    "instagram_url",
    "linkedin_url",
}


@api_bp.route('/settings', methods=['GET'])
@login_required
def get_settings():
    """Get all site settings."""
    settings = SiteSetting.query.all()
    return jsonify({s.key: s.value for s in settings}), 200


@api_bp.route('/settings', methods=['POST', 'PUT'])
@login_required
def update_settings():
    """Update site settings in bulk."""
    data = request.get_json()

    if not isinstance(data, dict):
        return jsonify({'error': 'Format invalide'}), 400

    for key, value in data.items():
        if key not in ALLOWED_SETTINGS_KEYS:
            continue  # ignore clés non autorisées

        setting = SiteSetting.query.filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            db.session.add(SiteSetting(key=key, value=value))

    db.session.commit()
    return jsonify({'message': 'Settings mis à jour avec succès'}), 200


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
# CITY CRUD
# ============================================

# City module disabled by user request
# @api_bp.route('/cities', methods=['GET']) ...



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

# ============================================
# STATS & EXPORT (for dashboard)
# ============================================

from datetime import datetime, timedelta
from sqlalchemy import func, desc
import csv
import io
from flask import make_response

@api_bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    """Get dashboard statistics including charts and top products."""
    
    # 1. Basic Counters
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='En attente').count()
    total_products = Product.query.count()
    active_products = Product.query.filter_by(is_active=True).count()
    total_admins = Admin.query.count()
    
    orders = Order.query.all()
    total_revenue = sum(o.total_price for o in orders)

    # 2. Revenue Chart Data (Last 7 Days)
    today = datetime.now().date()
    seven_days_ago = today - timedelta(days=6)
    
    # Initialize dictionary for last 7 days with 0
    revenue_data = {}
    for i in range(7):
        day = (seven_days_ago + timedelta(days=i)).strftime('%Y-%m-%d')
        revenue_data[day] = 0.0

    # Query orders from last 7 days
    recent_orders = Order.query.filter(Order.created_at >= seven_days_ago).all()
    for o in recent_orders:
        if o.created_at:
            day_str = o.created_at.strftime('%Y-%m-%d')
            if day_str in revenue_data:
                revenue_data[day_str] += o.total_price

    # Format for frontend [ {date, total}, ... ]
    chart_data = [{"date": k, "total": v} for k, v in revenue_data.items()]

    # 3. Top 5 Best Selling Products
    # Query OrderItem, join Product, group by product, sum quantity, order by sum desc
    top_products_query = db.session.query(
        Product.name, func.sum(OrderItem.quantity).label('total_qty')
    ).join(Product).group_by(Product.name).order_by(desc('total_qty')).limit(5).all()

    top_products = [{"name": r[0], "sold": r[1]} for r in top_products_query]

    return jsonify({
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_products': total_products,
        'active_products': active_products,
        'total_admins': total_admins,
        'total_revenue': total_revenue,
        'chart_data': chart_data,
        'top_products': top_products
    })


@api_bp.route('/export/orders', methods=['GET'])
@login_required
def export_orders():
    """Export all orders to CSV."""
    orders = Order.query.order_by(Order.created_at.desc()).all()
    
    # Create CSV in memory
    si = io.StringIO()
    cw = csv.writer(si)
    
    # Header
    cw.writerow(['ID', 'Date', 'Client', 'Telephone', 'Email', 'Adresse', 'Total (DT)', 'Statut', 'Produits'])
    
    # Rows
    for o in orders:
        date_str = o.created_at.strftime('%Y-%m-%d %H:%M') if o.created_at else ''
        items_str = ", ".join([f"{i.quantity}x {i.product.name if i.product else 'Unknown'}" for i in o.items])
        
        cw.writerow([
            o.id,
            date_str,
            o.customer_name,
            o.customer_phone,
            o.customer_email or '',
            o.delivery_address,
            f"{o.total_price:.2f}",
            o.status,
            items_str
        ])
        
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=commandes_ohmeals.csv"
    output.headers["Content-type"] = "text/csv"
    return output