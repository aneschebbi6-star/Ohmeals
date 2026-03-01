"""
Order and OrderItem models for OHMEALS.
Handles customer orders with delivery information.
"""
from datetime import datetime
from app.extensions import db


class Order(db.Model):
    """Order model - delivery only."""
    __tablename__ = 'orders'
    __table_args__ = (
        db.Index('idx_order_status', 'status'),
        db.CheckConstraint('total_price >= 0', name='check_positive_total'),
    )

    id = db.Column(db.Integer, primary_key=True)
    
    # Customer information
    customer_name = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_email = db.Column(db.String(120), nullable=True)
    
    # Delivery information (required)
    delivery_address = db.Column(db.Text, nullable=False)
    delivery_fee = db.Column(db.Float, nullable=False, default=0.0)
    
    # Order totals
    total_price = db.Column(db.Float, nullable=False)
    
    # Status: 'En attente', 'En préparation', 'En livraison', 'Livrée', 'Annulée'
    status = db.Column(db.String(50), default='En attente')
    
    created_at = db.Column(db.DateTime, default=datetime.now)

    # Relationship to order items
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Order {self.id} - {self.customer_name}>'

    def calculate_total(self):
        """Calculate total from items + delivery fee."""
        items_total = sum(item.price for item in self.items)
        return items_total + self.delivery_fee


class OrderItem(db.Model):
    """Order item - links products to orders with quantity."""
    __tablename__ = 'order_items'
    __table_args__ = (
        db.Index('idx_item_order', 'order_id'),
        db.CheckConstraint('quantity > 0', name='check_positive_qty'),
        db.CheckConstraint('price >= 0', name='check_positive_item_price'),
    )

    id = db.Column(db.Integer, primary_key=True)
    
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # Quantity and pricing at time of order
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)  # Total price for this item

    # Relationship to product
    product = db.relationship('Product')

    def __repr__(self):
        return f'<OrderItem product={self.product_id} qty={self.quantity}>'
