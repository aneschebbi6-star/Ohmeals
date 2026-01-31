"""
Menu controller - internal menu and book pages.
Routes: /menu, /book
"""
from flask import Blueprint, render_template
from app.models.product import Product

menu_bp = Blueprint('menu', __name__)


@menu_bp.route('/menu')
def menu():
    """Dynamic menu page - displays active products."""
    products = Product.query.filter_by(is_active=True).all()
    
    # Separate products by category
    snacks = [p for p in products if p.category == 'snack']
    plats = [p for p in products if p.category == 'plat']
    
    return render_template('menu.html', products=products, snacks=snacks, plats=plats)


@menu_bp.route('/book')
def book():
    """Booking/order page."""
    products = Product.query.filter_by(is_active=True).all()
    return render_template('book.html', products=products)
