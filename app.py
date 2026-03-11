from flask import Flask
from extensions import db, jwt
from flask_cors import CORS
import os

app = Flask(__name__)

CORS(app, origins="*")

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres.brkvmeleudpontlxmmir:0OHz1aGVi2fye7EA@aws-1-eu-west-1.pooler.supabase.com:6543/postgres")
JWT_SECRET = os.environ.get("JWT_SECRET", "09333f71c3fd95637e321ff2f35feccf08d1e9a7c505f7d215863210b6feae49")

app.config["JWT_SECRET_KEY"] = JWT_SECRET
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
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

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(products_bp, url_prefix='/api/products')
app.register_blueprint(categories_bp, url_prefix='/api/categories')
app.register_blueprint(sales_bp, url_prefix='/api/sales')
app.register_blueprint(orders_bp, url_prefix='/api/orders')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
