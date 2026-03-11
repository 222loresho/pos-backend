from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User
from passlib.hash import bcrypt

users_bp = Blueprint('users', __name__)

def admin_required():
    identity = get_jwt_identity()
    user = User.query.get(identity)
    if not user or user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    return None

@users_bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    err = admin_required()
    if err: return err
    users = User.query.all()
    return jsonify([{
        'id': u.id,
        'name': u.name,
        'username': u.username,
        'role': u.role,
        'active': u.active
    } for u in users])

@users_bp.route('/', methods=['POST'])
@jwt_required()
def create_user():
    err = admin_required()
    if err: return err
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    user = User(
        name=data['name'],
        username=data['username'],
        password=bcrypt.hash(data['password']),
        role=data.get('role', 'cashier'),
        active=True
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created', 'id': user.id}), 201

@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    err = admin_required()
    if err: return err
    user = User.query.get_or_404(user_id)
    data = request.json
    if 'name' in data: user.name = data['name']
    if 'role' in data: user.role = data['role']
    if 'active' in data: user.active = data['active']
    if 'password' in data and data['password']:
        user.password = bcrypt.hash(data['password'])
    db.session.commit()
    return jsonify({'message': 'User updated'})

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    err = admin_required()
    if err: return err
    identity = get_jwt_identity()
    if identity == user_id:
        return jsonify({'error': 'Cannot delete yourself'}), 400
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'})
