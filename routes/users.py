from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User
from passlib.hash import pbkdf2_sha256

users_bp = Blueprint('users', __name__)

def get_current_user():
    identity = get_jwt_identity()
    return User.query.get(identity)

def admin_required():
    user = get_current_user()
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
        'active': u.active,
        'pin': u.pin
    } for u in users])

@users_bp.route('/', methods=['POST'])
@jwt_required()
def create_user():
    err = admin_required()
    if err: return err
    data = request.get_json()
    name = data.get('name', '').strip()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    role = data.get('role', 'cashier')
    pin = data.get('pin', '1234').strip()

    if not name or not username or not password:
        return jsonify({'error': 'Name, username and password are required'}), 400
    if len(pin) != 4 or not pin.isdigit():
        return jsonify({'error': 'PIN must be exactly 4 digits'}), 400
    if User.query.filter(db.func.lower(User.username) == username.lower()).first():
        return jsonify({'error': 'Username already exists'}), 400

    user = User(
        name=name,
        username=username.lower(),
        password=pbkdf2_sha256.hash(password),
        role=role,
        active=True,
        pin=pin
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
    data = request.get_json()
    if 'name' in data: user.name = data['name'].strip()
    if 'role' in data: user.role = data['role']
    if 'active' in data: user.active = data['active']
    if 'pin' in data and data['pin']:
        pin = str(data['pin']).strip()
        if len(pin) != 4 or not pin.isdigit():
            return jsonify({'error': 'PIN must be exactly 4 digits'}), 400
        user.pin = pin
    if 'password' in data and data['password']:
        user.password = pbkdf2_sha256.hash(data['password'])
    db.session.commit()
    return jsonify({'message': 'User updated'})

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    err = admin_required()
    if err: return err
    current = get_current_user()
    if current.id == user_id:
        return jsonify({'error': 'Cannot delete yourself'}), 400
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'})
