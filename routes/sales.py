from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.sale import Sale, SaleItem
from models.product import Product
from models.user import User

sales_bp = Blueprint('sales', __name__)

@sales_bp.route('/', methods=['GET'])
@jwt_required()
def get_sales():
    sales = Sale.query.order_by(Sale.created_at.desc()).all()
    return jsonify([{
        'id': s.id,
        'cashier_name': s.cashier_name,
        'total': float(s.total),
        'amount_paid': float(s.amount_paid),
        'change_due': float(s.change_due),
        'payment_method': s.payment_method,
        'created_at': s.created_at.isoformat()
    } for s in sales])

@sales_bp.route('/', methods=['POST'])
@jwt_required()
def create_sale():
    data = request.get_json()
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    items = data.get('items', [])
    total = sum(item['price'] * item['quantity'] for item in items)
    amount_paid = data.get('amount_paid', total)
    change_due = amount_paid - total

    sale = Sale(
        cashier_id=user.id,
        cashier_name=user.name,
        total=total,
        amount_paid=amount_paid,
        change_due=change_due,
        payment_method=data.get('payment_method', 'cash')
    )
    db.session.add(sale)
    db.session.flush()

    for item in items:
        product = Product.query.get(item['product_id'])
        product.stock -= item['quantity']
        sale_item = SaleItem(
            sale_id=sale.id,
            product_id=item['product_id'],
            product_name=product.name,
            quantity=item['quantity'],
            price=item['price'],
            subtotal=item['price'] * item['quantity']
        )
        db.session.add(sale_item)

    db.session.commit()
    return jsonify({'message': 'Sale created', 'change_due': float(change_due)}), 201
