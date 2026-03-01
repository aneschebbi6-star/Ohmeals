from flask import Blueprint, render_template, request, jsonify
from app.models.product import Product, ProductVariant
from app.models.order import Order, OrderItem
from app.extensions import db, mail
from flask_mail import Message
from app.models.admin import Admin
from threading import Thread
from flask import current_app

menu_bp = Blueprint('menu', __name__)

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
    prepared_products = [p.to_dict() for p in products]

    # (Optionnel) Préparer les listes spécifiques si vous voulez faire du rendu serveur
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
        
        # ---------------------------------------------------------
        # Send Email Notification to All Administrators
        # ---------------------------------------------------------
        try:
            admins = Admin.query.all()
            admin_emails = [admin.email for admin in admins if admin.email]
            
            if admin_emails:
                msg = Message(
                    subject=f"Nouvelle commande Ohmeals #{new_order.id}",
                    recipients=admin_emails,
                    body=f"Une nouvelle commande a été passée par {new_order.customer_name}.\n"
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
            # On ne bloque pas la commande si l'envoi de l'email échoue
        # ---------------------------------------------------------
        
        return jsonify({
            'success': True,
            'message': 'Commande créée avec succès',
            'order_id': new_order.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erreur lors de la création: {str(e)}'}), 500