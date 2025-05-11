from flask import request, jsonify, abort
from db import SessionLocal, BillingRecord, User
from logger import setup_logger
from datetime import datetime
from . import billing_bp
from admin.admin_auth import admin_login_required

logger = setup_logger()

@billing_bp.route('/invoices', methods=['POST'])
@admin_login_required
def create_invoice():
    data = request.json
    required_fields = ['username', 'amount', 'date', 'description']
    if not all(field in data for field in required_fields):
        logger.warning("Missing required invoice fields in create_invoice")
        abort(400, description="Missing required invoice fields")
    db = SessionLocal()
    user = db.query(User).filter(User.username == data['username']).first()
    if not user:
        db.close()
        logger.warning(f"User {data['username']} not found for invoice creation")
        abort(404, description="User not found")
    try:
        billing_date = datetime.strptime(data['date'], '%Y-%m-%d')
    except ValueError:
        db.close()
        logger.warning("Invalid date format in create_invoice")
        abort(400, description="Invalid date format, expected YYYY-MM-DD")
    new_invoice = BillingRecord(
        user_id=user.id,
        amount=data['amount'],
        billing_date=billing_date,
        description=data['description']
    )
    db.add(new_invoice)
    db.commit()
    db.close()
    logger.info(f"Created invoice for user {data['username']}")
    return jsonify({"message": "Invoice created"}), 201
