from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ===== YOUR CONFIG (ALREADY FILLED) =====
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres.brkvmeleudpontlxmmir:0OHz1aGVi2fye7EA@aws-1-eu-west-1.pooler.supabase.com:6543/postgres"
app.config["JWT_SECRET_KEY"] = "09333f71c3fd95637e321ff2f35feccf08d1e9a7c505f7d215863210b6feae49"
# ========================================

db = SQLAlchemy(app)
jwt = JWTManager(app)

# ===== MODELS =====
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Float)
    stock = db.Column(db.Integer)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table = db.Column(db.String(50))
    status = db.Column(db.String(20), default="pending")
    total = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ===== ROUTES =====
@app.route("/")
def home():
    return {"status":"running"}

@app.route("/api/products")
def products():
    return jsonify([{"id":p.id,"name":p.name,"price":p.price,"stock":p.stock} for p in Product.query.all()])

@app.route("/api/orders")
def orders():
    return jsonify([{"id":o.id,"table":o.table,"status":o.status,"total":o.total} for o in Order.query.all()])

@app.route("/api/orders", methods=["POST"])
def create_order():
    data = request.json
    o = Order(table=data["table"], total=data["total"])
    db.session.add(o)
    db.session.commit()
    return {"message":"saved"}

@app.route("/api/orders/<id>/submit", methods=["POST"])
def submit(id):
    o = Order.query.get(id)
    o.status = "submitted"
    db.session.commit()
    return {"message":"submitted"}

@app.route("/api/orders/<id>/confirm", methods=["POST"])
def confirm(id):
    o = Order.query.get(id)
    o.status = "confirmed"
    db.session.commit()
    return {"message":"confirmed"}

if __name__ == "__main__":
    db.create_all()
    app.run(host="0.0.0.0", port=5001)
