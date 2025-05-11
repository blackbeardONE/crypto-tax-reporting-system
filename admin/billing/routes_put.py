from flask import request, jsonify, abort
from db import SessionLocal, BillingRecord
from logger import setup_logger
from datetime import datetime
from . import billing_bp
from admin.admin_auth import admin_login_required

logger = setup_logger()

@billing_bp.route('/invoices/<int:invoice_id>', methods=['PUT'])
@admin_login_required
def update_invoice(invoice_id):
    data = request.json
    db = SessionLocal()
    invoice = db.query(BillingRecord).filter(BillingRecord.id == invoice_id).first()
    if not invoice:
        db.close()
        logger.warning(f"Invoice {invoice_id} not found for update")
        abort(404, description="Invoice not found")
    for field in ['amount', 'date', 'description']:
        if field in data:
            if field == 'date':
                try:
                    setattr(invoice, 'billing_date', datetime.strptime(data[field], '%Y-%m-%d'))
                except ValueError:
                    db.close()
                    logger.warning(f"Invalid date format for {field} in update_invoice")
                    abort(400, description=f"Invalid date format for {field}, expected YYYY-MM-DD")
            else:
                setattr(invoice, field, data[field])
    db.commit()
    db.close()
    logger.info(f"Updated invoice {invoice_id}")
    return jsonify({"message": "Invoice updated"})
