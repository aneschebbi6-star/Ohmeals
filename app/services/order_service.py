"""
Order service layer for OHMEALS.
"""
from app.extensions import db, mail
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.admin import Admin
from flask_mail import Message
from threading import Thread
from flask import current_app

def get_all_orders():
    """Get all orders sorted by date descending."""
    return Order.query.order_by(Order.created_at.desc()).all()

def create_order(data):
    """Create new order with items."""
    if not data.get('customer_name') or not data.get('customer_phone') or not data.get('delivery_address'):
        raise ValueError('Informations client manquantes')

    if not data.get('items') or len(data['items']) == 0:
        raise ValueError('La commande doit contenir au moins un produit')

    items_total = 0
    order_items_prepared = []

    for item_data in data['items']:
        product = Product.query.get(item_data['product_id'])
        if not product:
            raise ValueError(f"Produit {item_data['product_id']} non trouvé")

        quantity = float(item_data['quantity'])
        
        # Fallback for price since Product doesn't have it directly anymore
        variant = product.get_default_variant()
        if not variant:
            raise ValueError(f"Le produit {product.name} n'a pas de variante ou de prix défini")
            
        unit = item_data.get('unit') or variant.unit
        price_per_unit = float(item_data.get('price_per_unit') or variant.price)
        item_total_price = price_per_unit * quantity
        
        items_total += item_total_price

        order_items_prepared.append({
            'product_id': product.id,
            'quantity': quantity,
            'unit': unit,
            'price': item_total_price # Total for this item (as per OrderItem model)
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

    for item_prep in order_items_prepared:
        order_item = OrderItem(order_id=new_order.id, **item_prep)
        db.session.add(order_item)

    db.session.commit()
    
    # ---------------------------------------------------------
    # Send Email Notification to All Administrators
    # ---------------------------------------------------------
    try:
        admins = Admin.query.all()
        admin_emails = [admin.email for admin in admins if admin.email]
        
        if admin_emails:
            msg = Message(
                subject=f"Nouvelle commande Ohmeals #{new_order.id} (Dashboard)",
                recipients=admin_emails,
                body=f"Une nouvelle commande a été créée depuis le dashboard par/pour {new_order.customer_name}.\n"
                     f"Téléphone: {new_order.customer_phone}\n"
                     f"Adresse: {new_order.delivery_address}\n"
                     f"Total: {new_order.total_price} DT\n\n"
                     f"Connectez-vous au dashboard pour voir les détails de la commande."
            )
            
            def send_async_email(app, msg):
                with app.app_context():
                    try:
                        mail.send(msg)
                    except Exception as e:
                        print(f"Erreur lors de l'envoi de l'email: {str(e)}")
                        
            Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
    except Exception as e:
        print(f"Erreur préparation email: {str(e)}")
    # ---------------------------------------------------------
    
    return new_order

def update_order(order_id, data):
    """Update order details."""
    order = Order.query.get_or_404(order_id)
    
    if 'status' in data: order.status = data['status']
    if 'customer_name' in data: order.customer_name = data['customer_name']
    if 'customer_phone' in data: order.customer_phone = data['customer_phone']
    if 'customer_email' in data: order.customer_email = data['customer_email']
    if 'delivery_address' in data: order.delivery_address = data['delivery_address']

    db.session.commit()
    return order

def delete_order(order_id):
    """Delete order."""
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    return True
