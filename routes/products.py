from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from extensions import db
from models.product import Product

products_bp = Blueprint('products', __name__)

@products_bp.route('/', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'price': float(p.price),
        'stock': p.stock,
        'category_id': p.category_id
    } for p in products])

@products_bp.route('/', methods=['POST'])
@jwt_required()
def create_product():
    data = request.get_json()
    category_id = data.get('category_id')
    if category_id == '' or category_id == 0:
        category_id = None
    product = Product(
        name=data['name'],
        price=data['price'],
        stock=data.get('stock', 0),
        category_id=category_id
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({'message': 'Product created successfully'}), 201
