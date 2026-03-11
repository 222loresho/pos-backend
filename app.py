from flask import Flask, jsonify
from extensions import db, jwt
from dotenv import load_dotenv
from flask_cors import CORS
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
jwt.init_app(app)

from models.user import User
from models.category import Category
from models.product import Product
from models.sale import Sale, SaleItem
from models.order import Order, OrderItem

from routes.auth import auth_bp
from routes.products import products_bp
from routes.categories import categories_bp
from routes.sales import sales_bp
from routes.orders import orders_bp

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(products_bp, url_prefix="/api/products")
app.register_blueprint(categories_bp, url_prefix="/api/categories")
app.register_blueprint(sales_bp, url_prefix="/api/sales")
app.register_blueprint(orders_bp, url_prefix="/api/orders")

@app.route("/api/health")
def health():
    return jsonify({"status": "Flask is running!"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
