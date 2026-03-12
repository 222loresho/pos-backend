from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from extensions import db
from models.sale import Sale, SaleItem
from models.product import Product
from datetime import datetime, date
from sqlalchemy import func

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/daily', methods=['GET'])
@jwt_required()
def daily_report():
    report_date = request.args.get('date', date.today().isoformat())
    try:
        target_date = datetime.strptime(report_date, '%Y-%m-%d').date()
    except:
        return jsonify({'error': 'Invalid date format'}), 400

    sales = Sale.query.filter(
        func.date(Sale.created_at) == target_date
    ).all()

    total_revenue = sum(s.total for s in sales)
    total_transactions = len(sales)

    by_method = {}
    for s in sales:
        m = s.payment_method or 'cash'
        if m not in by_method:
            by_method[m] = {'count': 0, 'total': 0}
        by_method[m]['count'] += 1
        by_method[m]['total'] += s.total

    item_sales = {}
    for sale in sales:
        for item in sale.items:
            pid = item.product_id
            if pid not in item_sales:
                item_sales[pid] = {
                    'product_name': item.product_name,
                    'quantity': 0,
                    'revenue': 0
                }
            item_sales[pid]['quantity'] += item.quantity
            item_sales[pid]['revenue'] += item.subtotal

    top_products = sorted(item_sales.values(), key=lambda x: x['quantity'], reverse=True)[:10]

    sales_list = []
    for s in sales:
        sales_list.append({
            'id': s.id,
            'cashier_name': s.cashier_name,
            'total': s.total,
            'amount_paid': s.amount_paid,
            'change_due': s.change_due,
            'payment_method': s.payment_method,
            'created_at': s.created_at.isoformat(),
            'items': [{'product_name': i.product_name, 'quantity': i.quantity, 'subtotal': i.subtotal} for i in s.items]
        })

    return jsonify({
        'date': report_date,
        'total_revenue': total_revenue,
        'total_transactions': total_transactions,
        'by_payment_method': by_method,
        'top_products': top_products,
        'sales': sales_list
    })
