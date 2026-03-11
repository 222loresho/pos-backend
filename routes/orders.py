from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.order import Order, OrderItem
from models.product import Product
from models.user import User

orders_bp = Blueprint('orders', __name__)

def order_to_dict(o):
    items = OrderItem.query.filter_by(order_id=o.id).all()
    return {
        'id': o.id,
        'order_number': f'#{str(o.id).zfill(4)}',
        'table_name': o.table_name,
        'cashier_name': o.cashier_name,
        'waiter_name': o.waiter_name or o.cashier_name,
        'status': o.status,
        'total': float(o.total),
        'created_at': o.created_at.isoformat(),
        'items': [{
            'product_id': i.product_id,
            'product_name': i.product_name,
            'quantity': i.quantity,
            'price': float(i.price),
            'subtotal': float(i.subtotal)
        } for i in items]
    }

@orders_bp.route('/', methods=['GET'])
@jwt_required()
def get_orders():
    orders = Order.query.filter_by(status='pending').order_by(Order.created_at.desc()).all()
    return jsonify([order_to_dict(o) for o in orders])

@orders_bp.route('/completed', methods=['GET'])
@jwt_required()
def get_completed_orders():
    orders = Order.query.filter_by(status='completed').order_by(Order.created_at.desc()).limit(100).all()
    return jsonify([order_to_dict(o) for o in orders])

@orders_bp.route('/', methods=['POST'])
@jwt_required()
def create_order():
    data = request.get_json()
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    total = sum(i['subtotal'] for i in data['items'])
    order = Order(
        table_name=data['table_name'],
        cashier_id=user_id,
        cashier_name=user.name,
        waiter_name=data.get('waiter_name', user.name),
        status='pending',
        total=total
    )
    db.session.add(order)
    db.session.flush()
    for i in data['items']:
        item = OrderItem(
            order_id=order.id,
            product_id=i['product_id'],
            product_name=i['product_name'],
            quantity=i['quantity'],
            price=i['price'],
            subtotal=i['subtotal']
        )
        db.session.add(item)
    db.session.commit()
    return jsonify({'message': 'Order saved!', 'order_id': order.id}), 201

@orders_bp.route('/<int:id>/complete', methods=['POST'])
@jwt_required()
def complete_order(id):
    from models.sale import Sale, SaleItem
    data = request.get_json()
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    order = Order.query.get_or_404(id)
    items = OrderItem.query.filter_by(order_id=id).all()
    sale = Sale(
        cashier_id=user_id,
        cashier_name=user.name,
        total=order.total,
        amount_paid=data['amount_paid'],
        change_due=float(data['amount_paid']) - float(order.total),
        payment_method=data.get('payment_method', 'cash')
    )
    db.session.add(sale)
    db.session.flush()
    for i in items:
        db.session.add(SaleItem(
            sale_id=sale.id,
            product_id=i.product_id,
            product_name=i.product_name,
            quantity=i.quantity,
            price=i.price,
            subtotal=i.subtotal
        ))
        product = Product.query.get(i.product_id)
        if product:
            product.stock -= i.quantity
    order.status = 'completed'
    db.session.commit()
    return jsonify({'message': 'Order completed!', 'change_due': sale.change_due})

@orders_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_order(id):
    order = Order.query.get_or_404(id)
    OrderItem.query.filter_by(order_id=id).delete()
    db.session.delete(order)
    db.session.commit()
    return jsonify({'message': 'Order cancelled!'})

@orders_bp.route('/<int:order_id>', methods=['PUT'])
@jwt_required()
def update_order(order_id):
    data = request.get_json()
    order = Order.query.get_or_404(order_id)
    OrderItem.query.filter_by(order_id=order_id).delete()
    for item in data['items']:
        oi = OrderItem(
            order_id=order_id,
            product_id=item['product_id'],
            product_name=item['product_name'],
            quantity=item['quantity'],
            price=item['price'],
            subtotal=item['subtotal']
        )
        db.session.add(oi)
    order.total = data['total']
    db.session.commit()
    return jsonify({'message': 'Order updated'})
