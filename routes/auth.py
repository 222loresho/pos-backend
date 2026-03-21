from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.user import User
from extensions import db
from passlib.hash import pbkdf2_sha256

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({"error": "Username already exists"}), 400
    hashed = pbkdf2_sha256.hash(data.get('password'))
    user = User(name=data.get('name'), username=data.get('username'), password=hashed, role=data.get('role', 'cashier'))
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    if not user or not pbkdf2_sha256.verify(data.get('password'), user.password):
        return jsonify({"error": "Invalid credentials"}), 401
    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": {"id": user.id, "name": user.name, "role": user.role}}), 200

@auth_bp.route('/pin-login', methods=['POST'])
def pin_login():
    data = request.json
    username = data.get('username', '').strip()
    user = User.query.filter(User.username.ilike(username)).first()
    if not user or not user.active:
        return jsonify({'error': 'User not found or inactive'}), 401
    if not user.pin or user.pin != data.get('pin'):
        return jsonify({'error': 'Wrong PIN'}), 401
    token = create_access_token(identity=str(user.id))
    return jsonify({'token': token, 'user': {'id': user.id, 'name': user.name, 'role': user.role}})

@auth_bp.route('/verify-pin', methods=['POST'])
@jwt_required()
def verify_pin():
    data = request.json
    identity = get_jwt_identity()
    user = User.query.get(identity)
    if not user:
        return jsonify({'valid': False}), 404
    if user.pin and data.get('pin') == user.pin:
        return jsonify({'valid': True})
    return jsonify({'valid': False})
