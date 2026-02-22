"""
API controller - REST API for React dashboard.
Prefix: /api
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models.admin import Admin
from app.models.product import Product, ProductVariant, ProductImage
from app.models.order import Order, OrderItem
from app.models.site_setting import SiteSetting  
from app.utils import is_valid_email, is_valid_password
from app.services.accounting_service import get_financial_summary, get_revenue_chart_data
from app.services import product_service, order_service

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

    if not is_valid_email(data['email']):
        return jsonify({'error': 'Format email invalide'}), 400

    is_valid_pass, pass_error = is_valid_password(data['password'])
    if not is_valid_pass:
        return jsonify({'error': pass_error}), 400

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
    if data.get('email'):
        if not is_valid_email(data['email']):
            return jsonify({'error': 'Format email invalide'}), 400
        admin.email = data['email']

    if data.get('password') and data['password'].strip():
        is_valid_pass, pass_error = is_valid_password(data['password'])
        if not is_valid_pass:
            return jsonify({'error': pass_error}), 400
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
    """Get all products with their variants and images."""
    result = product_service.get_all_products(include_inactive=True)
    return jsonify(result), 200


@api_bp.route('/products', methods=['POST'])
@login_required
def add_product():
    """Create new product with optional first variant, images, and video."""
    data = request.get_json()
    # Basic validation
    required_fields = ['name', 'category', 'variant_name', 'unit', 'price']
    for field in required_fields:
        val = data.get(field)
        if val is None or (isinstance(val, str) and not val.strip()):
            if field == 'price' and val == 0: continue
            return jsonify({'error': f'Champ obligatoire manquant: {field}'}), 400

    new_product = product_service.create_product(data)
    return jsonify({'message': 'Produit ajouté avec succès', 'product_id': new_product.id}), 201


@api_bp.route('/products/<int:id>', methods=['PUT'])
@login_required
def update_product(id):
    """Update product info, variants, images, and video."""
    data = request.get_json()
    product_service.update_product(id, data)
    return jsonify({'message': 'Produit modifié avec succès'}), 200


@api_bp.route('/products/<int:id>', methods=['DELETE'])
@login_required
def delete_product(id):
    """Delete product and all its variants."""
    product_service.delete_product(id)
    return jsonify({'message': 'Produit et variantes supprimés avec succès'}), 200


# Logic moved to product_service


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
    orders = order_service.get_all_orders()
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
    ]), 200


@api_bp.route('/orders', methods=['POST'])
@login_required
def add_order():
    """Create new order with items."""
    data = request.get_json()
    try:
        new_order = order_service.create_order(data)
        return jsonify({'message': 'Commande créée avec succès', 'id': new_order.id}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/orders/<int:id>', methods=['PUT'])
@login_required
def update_order(id):
    """Update order details."""
    data = request.get_json()
    order_service.update_order(id, data)
    return jsonify({'message': 'Commande modifiée avec succès'}), 200


@api_bp.route('/orders/<int:id>', methods=['DELETE'])
@login_required
def delete_order(id):
    """Delete order."""
    order_service.delete_order(id)
    return jsonify({'message': 'Commande supprimée avec succès'}), 200


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
    
    # 2. Financial Metrics (Current Month & Today Sync)
    month_summary = get_financial_summary('month')
    today_summary = get_financial_summary('today')
    
    month_revenue = month_summary.get('revenue', 0)
    month_profit = month_summary.get('profit', 0)
    today_revenue = today_summary.get('revenue', 0)
    today_profit = today_summary.get('profit', 0)
    
    # All-time revenue for reference
    all_time_revenue = db.session.query(func.coalesce(func.sum(Order.total_price), 0))\
        .filter_by(status='Livrée').scalar() or 0

    # 3. Revenue Chart Data (Last 7 Days)
    today_date = datetime.now().date()
    seven_days_ago = today_date - timedelta(days=6)
    chart_data_results = get_revenue_chart_data(seven_days_ago, today_date, 'daily')
    
    # Ensure all 7 days are present
    revenue_map = {r['label']: r['total'] for r in chart_data_results}
    chart_data = []
    for i in range(7):
        day = (seven_days_ago + timedelta(days=i)).strftime('%Y-%m-%d')
        chart_data.append({"date": day, "total": revenue_map.get(day, 0.0)})

    # 4. Top 5 Best Selling Products (Delivered only)
    top_products_query = db.session.query(
        Product.name, func.sum(OrderItem.quantity).label('total_qty')
    ).join(Product).join(Order).filter(Order.status == 'Livrée')\
    .group_by(Product.name).order_by(desc('total_qty')).limit(5).all()

    top_products = [{"name": r[0], "sold": r[1] or 0} for r in top_products_query]

    return jsonify({
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_products': total_products,
        'active_products': active_products,
        'total_admins': total_admins,
        'total_revenue': float(all_time_revenue),
        'month_revenue': month_revenue,
        'month_profit': month_profit,
        'today_revenue': today_revenue,
        'today_profit': today_profit,
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