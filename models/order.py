from extensions import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String(50), nullable=False)
    cashier_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    cashier_name = db.Column(db.String(100))
    waiter_name = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')
    total = db.Column(db.Numeric(10, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    product_name = db.Column(db.String(100))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Numeric(10, 2))
    subtotal = db.Column(db.Numeric(10, 2))
