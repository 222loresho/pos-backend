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

@products_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_product(id):
    product = Product.query.get_or_404(id)
    data = request.get_json()
    category_id = data.get('category_id')
    if category_id == '' or category_id == 0:
        category_id = None
    product.name = data.get('name', product.name)
    product.price = data.get('price', product.price)
    product.stock = data.get('stock', product.stock)
    product.category_id = category_id
    db.session.commit()
    return jsonify({'message': 'Product updated successfully'})

@products_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'})

@products_bp.route('/low-stock', methods=['GET'])
@jwt_required()
def low_stock():
    threshold = request.args.get('threshold', 10, type=int)
    products = Product.query.filter(Product.stock <= threshold).order_by(Product.stock.asc()).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'stock': p.stock,
        'price': float(p.price),
        'category_id': p.category_id
    } for p in products])
