from flask import jsonify, request
from bson import ObjectId
from app import app, mongo

# GET ALL BILLS
@app.route('/bills', methods=['GET'])
def get_bills():
    bills = list(mongo.db.bills.find())
    for bill in bills:
        bill['_id'] = str(bill['_id'])
    return jsonify(bills)

# WAITER SUBMIT PAYMENT
@app.route('/submit-payment', methods=['POST'])
def submit_payment():
    data = request.get_json()
    bill_id = data.get('bill_id')
    mongo.db.bills.update_one(
        {"_id": ObjectId(bill_id)},
        {"$set": {"status": "submitted"}}
    )
    return jsonify({"message": "submitted"})

# CASHIER CONFIRM PAYMENT
@app.route('/confirm-payment', methods=['POST'])
def confirm_payment():
    data = request.get_json()
    bill_id = data.get('bill_id')
    mongo.db.bills.update_one(
        {"_id": ObjectId(bill_id)},
        {"$set": {"status": "paid"}}
    )
    return jsonify({"message": "paid"})
